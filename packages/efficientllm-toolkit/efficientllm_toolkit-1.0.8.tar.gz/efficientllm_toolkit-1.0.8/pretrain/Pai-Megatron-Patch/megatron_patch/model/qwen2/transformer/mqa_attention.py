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
Multi-Query Attention (MQA) implementation for Qwen2.5

MQA uses a single key and value head shared across all query heads,
reducing memory bandwidth and computational cost.
"""

from dataclasses import dataclass
from typing import Union
import torch
from megatron.core.transformer.spec_utils import ModuleSpec
from megatron.core.transformer.transformer_config import TransformerConfig
from megatron.core.transformer.enums import AttnMaskType

from .attention import Attention, SelfAttentionSubmodules


@dataclass
class MQASelfAttentionSubmodules(SelfAttentionSubmodules):
    """MQA Self-Attention submodules with single K/V heads"""
    pass


class MQAAttention(Attention):
    """
    Multi-Query Attention (MQA) implementation.
    
    MQA uses multiple query heads but only single key and value heads,
    which are shared across all query heads. This reduces memory bandwidth
    and improves inference efficiency.
    """

    def __init__(
        self,
        config: TransformerConfig,
        submodules: MQASelfAttentionSubmodules,
        layer_number: int,
        attn_mask_type: AttnMaskType = AttnMaskType.causal,
        attention_type: str = "self",
    ):
        # Force num_query_groups to 1 for MQA
        original_num_query_groups = config.num_query_groups
        config.num_query_groups = 1
        
        super().__init__(
            config=config,
            submodules=submodules,
            layer_number=layer_number,
            attn_mask_type=attn_mask_type,
            attention_type=attention_type,
        )
        
        # Restore original config to avoid affecting other layers
        config.num_query_groups = original_num_query_groups
        
        # Build QKV linear layer - Q has multiple heads, K/V have single head
        self.linear_qkv = submodules.linear_qkv(
            self.config.hidden_size,
            self.query_projection_size + 2 * self.config.kv_channels,  # Q + single K + single V
            config=self.config,
            init_method=self.config.init_method,
            bias=self.config.add_bias_linear,
            skip_bias_add=True,
            is_expert=False,
        )

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
        # Apply QKV linear layer
        mixed_x_layer, bias = self.linear_qkv(hidden_states)

        if bias is not None:
            mixed_x_layer = mixed_x_layer + bias

        # Split into Q, K, V
        # Q: [s, b, num_heads * head_dim]
        # K, V: [s, b, head_dim] (single head each)
        query_projection_size = self.config.num_attention_heads * self.config.kv_channels
        key_value_size = self.config.kv_channels
        
        query_layer = mixed_x_layer[..., :query_projection_size]
        key_layer = mixed_x_layer[..., query_projection_size:query_projection_size + key_value_size]
        value_layer = mixed_x_layer[..., query_projection_size + key_value_size:]

        # Reshape query to [s, b, num_heads, head_dim]
        new_query_shape = query_layer.size()[:-1] + (
            self.config.num_attention_heads // self.config.tensor_model_parallel_size,
            self.config.kv_channels,
        )
        query_layer = query_layer.view(*new_query_shape)

        # Reshape key and value to [s, b, 1, head_dim] and expand to match query heads
        new_kv_shape = key_layer.size()[:-1] + (1, self.config.kv_channels)
        key_layer = key_layer.view(*new_kv_shape)
        value_layer = value_layer.view(*new_kv_shape)
        
        # Expand K and V to match the number of query heads
        num_heads_per_partition = self.config.num_attention_heads // self.config.tensor_model_parallel_size
        key_layer = key_layer.expand(-1, -1, num_heads_per_partition, -1)
        value_layer = value_layer.expand(-1, -1, num_heads_per_partition, -1)

        # Apply rotary position embedding if provided
        if rotary_pos_emb is not None:
            query_layer = self.apply_rotary_pos_emb(query_layer, rotary_pos_emb)
            key_layer = self.apply_rotary_pos_emb(key_layer, rotary_pos_emb)

        # Core attention computation
        context_layer = self.core_attention(
            query_layer, key_layer, value_layer, attention_mask, inference_params=inference_params
        )

        # Output projection
        output, bias = self.linear_proj(context_layer)
        return output, bias

    def apply_rotary_pos_emb(self, tensor, rotary_pos_emb):
        """Apply rotary position embedding to tensor"""
        if rotary_pos_emb is not None:
            # Apply rotary embedding - this is a simplified version
            # In practice, you would use the proper rotary embedding function
            return tensor  # Placeholder
        return tensor