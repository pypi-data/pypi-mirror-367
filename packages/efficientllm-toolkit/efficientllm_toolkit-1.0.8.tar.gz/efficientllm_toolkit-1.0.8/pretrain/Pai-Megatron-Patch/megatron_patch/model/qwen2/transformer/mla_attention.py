# Copyright (c) 2024 Alibaba PAI and Nvidia Megatron-LM Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Multi-Head Latent Attention (MLA) implementation for Qwen2.5

MLA introduces latent dimensions to compress key-value representations,
reducing memory usage while maintaining performance.
Adapted from DeepSeek-V2's MLA implementation.
"""

import math
from dataclasses import dataclass
from typing import Union
import torch
import torch.nn as nn
from megatron.core import parallel_state, tensor_parallel
from megatron.core.models.common.embeddings.rotary_pos_embedding import apply_rotary_pos_emb
from megatron.core.transformer.module import MegatronModule
from megatron.core.transformer.spec_utils import ModuleSpec, build_module
from megatron.core.transformer.transformer_config import TransformerConfig
from megatron.core.transformer.enums import AttnMaskType
from megatron.core.utils import divide

from .attention import Attention, SelfAttentionSubmodules


@dataclass
class MLASelfAttentionSubmodules(SelfAttentionSubmodules):
    """MLA Self-Attention submodules with latent compression"""
    linear_q_a: Union[ModuleSpec, type] = None  # Query down-projection
    linear_q_b: Union[ModuleSpec, type] = None  # Query up-projection
    linear_kv_a: Union[ModuleSpec, type] = None  # KV down-projection
    linear_kv_b: Union[ModuleSpec, type] = None  # KV up-projection


class MLAAttention(Attention):
    """
    Multi-Head Latent Attention (MLA) implementation.
    
    MLA uses latent dimensions to compress key-value representations,
    which reduces memory usage and improves efficiency while maintaining
    model performance through learned low-rank projections.
    """

    def __init__(
        self,
        config: TransformerConfig,
        submodules: MLASelfAttentionSubmodules,
        layer_number: int,
        attn_mask_type: AttnMaskType = AttnMaskType.causal,
        attention_type: str = "self",
    ):
        super().__init__(
            config=config,
            submodules=submodules,
            layer_number=layer_number,
            attn_mask_type=attn_mask_type,
            attention_type=attention_type,
        )
        
        # MLA specific configurations
        self.latent_dim = getattr(config, 'mla_latent_dim', config.hidden_size // 8)  # Default to 1/8 of hidden size
        self.qk_head_dim = getattr(config, 'mla_qk_head_dim', 128)
        self.v_head_dim = config.kv_channels
        
        # Query projections: hidden -> latent -> qk_head_dim * num_heads
        self.linear_q_a = build_module(
            submodules.linear_q_a,
            config.hidden_size,
            self.latent_dim,
            config=config,
            init_method=config.init_method,
            bias=config.add_bias_linear,
            skip_bias_add=False,
        )
        
        self.linear_q_b = build_module(
            submodules.linear_q_b,
            self.latent_dim,
            self.qk_head_dim * self.num_attention_heads_per_partition,
            config=config,
            init_method=config.init_method,
            bias=config.add_bias_linear,
            skip_bias_add=False,
        )
        
        # KV projections: hidden -> latent -> (qk_head_dim + v_head_dim) * num_query_groups
        self.kv_proj_dim = (self.qk_head_dim + self.v_head_dim) * self.num_query_groups_per_partition
        
        self.linear_kv_a = build_module(
            submodules.linear_kv_a,
            config.hidden_size,
            self.latent_dim,
            config=config,
            init_method=config.init_method,
            bias=config.add_bias_linear,
            skip_bias_add=False,
        )
        
        self.linear_kv_b = build_module(
            submodules.linear_kv_b,
            self.latent_dim,
            self.kv_proj_dim,
            config=config,
            init_method=config.init_method,
            bias=config.add_bias_linear,
            skip_bias_add=False,
        )
        
        # Scaling factor for attention
        self.softmax_scale = 1.0 / math.sqrt(self.qk_head_dim)

    def forward(
        self,
        hidden_states,
        attention_mask,
        key_value_states=None,
        inference_params=None,
        rotary_pos_emb=None,
        packed_seq_params=None,
    ):
        # hidden_states: [s, b, h]
        seq_len, batch_size, _ = hidden_states.shape
        
        # Query projection through latent space
        q_latent = self.linear_q_a(hidden_states)  # [s, b, latent_dim]
        query_layer = self.linear_q_b(q_latent)    # [s, b, qk_head_dim * num_heads_per_partition]
        
        # KV projection through latent space
        kv_latent = self.linear_kv_a(hidden_states)  # [s, b, latent_dim]
        kv_layer = self.linear_kv_b(kv_latent)       # [s, b, (qk_head_dim + v_head_dim) * num_groups_per_partition]
        
        # Reshape query
        query_layer = query_layer.view(
            seq_len, batch_size, self.num_attention_heads_per_partition, self.qk_head_dim
        )
        
        # Split and reshape key, value
        kv_layer = kv_layer.view(
            seq_len, batch_size, self.num_query_groups_per_partition, self.qk_head_dim + self.v_head_dim
        )
        key_layer = kv_layer[..., :self.qk_head_dim]  # [s, b, num_groups, qk_head_dim]
        value_layer = kv_layer[..., self.qk_head_dim:]  # [s, b, num_groups, v_head_dim]
        
        # Expand key and value to match query heads if using GQA
        if self.num_query_groups_per_partition < self.num_attention_heads_per_partition:
            expansion_factor = self.num_attention_heads_per_partition // self.num_query_groups_per_partition
            key_layer = key_layer.unsqueeze(3).expand(-1, -1, -1, expansion_factor, -1)
            key_layer = key_layer.contiguous().view(
                seq_len, batch_size, self.num_attention_heads_per_partition, self.qk_head_dim
            )
            value_layer = value_layer.unsqueeze(3).expand(-1, -1, -1, expansion_factor, -1)
            value_layer = value_layer.contiguous().view(
                seq_len, batch_size, self.num_attention_heads_per_partition, self.v_head_dim
            )
        
        # Apply rotary position embedding if provided
        if rotary_pos_emb is not None:
            query_layer = apply_rotary_pos_emb(query_layer, rotary_pos_emb)
            key_layer = apply_rotary_pos_emb(key_layer, rotary_pos_emb)
        
        # Core attention computation with custom scaling
        context_layer = self.core_attention(
            query_layer, 
            key_layer, 
            value_layer, 
            attention_mask, 
            inference_params=inference_params,
            softmax_scale=self.softmax_scale
        )
        
        # Output projection
        output, bias = self.linear_proj(context_layer)
        return output, bias