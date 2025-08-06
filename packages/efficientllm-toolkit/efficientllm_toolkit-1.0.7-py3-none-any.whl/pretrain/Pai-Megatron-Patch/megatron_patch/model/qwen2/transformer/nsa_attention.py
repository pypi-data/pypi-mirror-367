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
Native Sparse Attention (NSA) implementation for Qwen2.5

NSA combines sliding window attention with sparse block-based attention
and compression mechanisms to reduce computational complexity while
maintaining performance.

Based on the Native Sparse Attention paper and PyTorch implementation.
"""

import math
from dataclasses import dataclass
from typing import Union, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from megatron.core import parallel_state, tensor_parallel
from megatron.core.models.common.embeddings.rotary_pos_embedding import apply_rotary_pos_emb
from megatron.core.transformer.module import MegatronModule
from megatron.core.transformer.spec_utils import ModuleSpec, build_module
from megatron.core.transformer.transformer_config import TransformerConfig
from megatron.core.transformer.enums import AttnMaskType

from .attention import Attention, SelfAttentionSubmodules


@dataclass
class NSASelfAttentionSubmodules(SelfAttentionSubmodules):
    """NSA Self-Attention submodules with compression networks"""
    compression_network: Union[ModuleSpec, type] = None


class CompressionNetwork(MegatronModule):
    """Simple compression network for NSA"""
    
    def __init__(self, config: TransformerConfig, compress_factor: int = 4):
        super().__init__(config=config)
        self.compress_factor = compress_factor
        self.hidden_size = config.hidden_size
        self.compressed_size = self.hidden_size // compress_factor
        
        self.compress = nn.Linear(self.hidden_size, self.compressed_size, bias=False)
        self.decompress = nn.Linear(self.compressed_size, self.hidden_size, bias=False)
        
    def forward(self, x):
        # x: [seq_len, batch, hidden_size]
        compressed = self.compress(x)
        decompressed = self.decompress(compressed)
        return decompressed


class NSAAttention(Attention):
    """
    Native Sparse Attention (NSA) implementation.
    
    NSA combines:
    1. Sliding window attention for local dependencies
    2. Sparse block-based attention for global dependencies
    3. Compression networks to reduce key-value memory
    """

    def __init__(
        self,
        config: TransformerConfig,
        submodules: NSASelfAttentionSubmodules,
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
        
        # NSA specific configurations
        self.sliding_window_size = getattr(config, 'nsa_sliding_window_size', 128)
        self.compress_block_size = getattr(config, 'nsa_compress_block_size', 64)
        self.compress_block_sliding_stride = getattr(config, 'nsa_compress_block_sliding_stride', 32)
        self.selection_block_size = getattr(config, 'nsa_selection_block_size', 64)
        self.num_selected_blocks = getattr(config, 'nsa_num_selected_blocks', 4)
        
        # Build QKV linear layer
        self.linear_qkv = build_module(
            submodules.linear_qkv,
            self.config.hidden_size,
            self.query_projection_size + 2 * self.kv_projection_size,
            config=self.config,
            init_method=self.config.init_method,
            bias=self.config.add_bias_linear,
            skip_bias_add=True,
            is_expert=False,
        )
        
        # Compression network for key-value compression
        self.compression_network = CompressionNetwork(config, compress_factor=4)
        
        # Selection network for block selection
        self.block_selector = nn.Linear(
            self.config.kv_channels, 1, bias=False
        )

    def create_sliding_window_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create sliding window attention mask"""
        mask = torch.full((seq_len, seq_len), float('-inf'), device=device)
        
        for i in range(seq_len):
            start = max(0, i - self.sliding_window_size // 2)
            end = min(seq_len, i + self.sliding_window_size // 2 + 1)
            mask[i, start:end] = 0.0
            
        # Apply causal mask
        causal_mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1) * float('-inf')
        mask = mask + causal_mask
        
        return mask

    def select_sparse_blocks(self, key_layer: torch.Tensor, value_layer: torch.Tensor) -> tuple:
        """Select important blocks for sparse attention"""
        seq_len, batch_size, num_heads, head_dim = key_layer.shape
        
        # Divide sequence into blocks
        num_blocks = seq_len // self.selection_block_size
        if seq_len % self.selection_block_size != 0:
            num_blocks += 1
            
        # Pad if necessary
        padded_seq_len = num_blocks * self.selection_block_size
        if padded_seq_len > seq_len:
            padding = padded_seq_len - seq_len
            key_padding = torch.zeros(padding, batch_size, num_heads, head_dim, 
                                    device=key_layer.device, dtype=key_layer.dtype)
            value_padding = torch.zeros(padding, batch_size, num_heads, head_dim,
                                      device=value_layer.device, dtype=value_layer.dtype)
            key_layer = torch.cat([key_layer, key_padding], dim=0)
            value_layer = torch.cat([value_layer, value_padding], dim=0)
        
        # Reshape into blocks
        key_blocks = key_layer.view(num_blocks, self.selection_block_size, batch_size, num_heads, head_dim)
        value_blocks = value_layer.view(num_blocks, self.selection_block_size, batch_size, num_heads, head_dim)
        
        # Compute block importance scores
        block_scores = []
        for i in range(num_blocks):
            block_key = key_blocks[i]  # [block_size, batch, num_heads, head_dim]
            # Use mean of the block as a simple importance measure
            block_repr = block_key.mean(dim=0)  # [batch, num_heads, head_dim]
            score = self.block_selector(block_repr).squeeze(-1)  # [batch, num_heads]
            block_scores.append(score.mean().item())
        
        # Select top-k blocks
        block_scores_tensor = torch.tensor(block_scores, device=key_layer.device)
        _, selected_indices = torch.topk(block_scores_tensor, 
                                       min(self.num_selected_blocks, num_blocks))
        
        # Gather selected blocks
        selected_key_blocks = key_blocks[selected_indices]  # [num_selected, block_size, batch, num_heads, head_dim]
        selected_value_blocks = value_blocks[selected_indices]
        
        # Reshape back
        selected_keys = selected_key_blocks.view(-1, batch_size, num_heads, head_dim)
        selected_values = selected_value_blocks.view(-1, batch_size, num_heads, head_dim)
        
        return selected_keys[:seq_len], selected_values[:seq_len]

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
        
        # Apply QKV linear layer
        mixed_x_layer, bias = self.linear_qkv(hidden_states)
        if bias is not None:
            mixed_x_layer = mixed_x_layer + bias

        # Split into Q, K, V
        query_layer = mixed_x_layer[..., :self.query_projection_size]
        key_layer = mixed_x_layer[..., self.query_projection_size:self.query_projection_size + self.kv_projection_size]
        value_layer = mixed_x_layer[..., self.query_projection_size + self.kv_projection_size:]

        # Reshape for multi-head attention
        query_layer = query_layer.view(seq_len, batch_size, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)
        key_layer = key_layer.view(seq_len, batch_size, self.num_query_groups_per_partition, self.hidden_size_per_attention_head)
        value_layer = value_layer.view(seq_len, batch_size, self.num_query_groups_per_partition, self.hidden_size_per_attention_head)

        # Expand key and value for GQA if needed
        if self.num_query_groups_per_partition < self.num_attention_heads_per_partition:
            expansion_factor = self.num_attention_heads_per_partition // self.num_query_groups_per_partition
            key_layer = key_layer.unsqueeze(3).expand(-1, -1, -1, expansion_factor, -1)
            key_layer = key_layer.contiguous().view(seq_len, batch_size, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)
            value_layer = value_layer.unsqueeze(3).expand(-1, -1, -1, expansion_factor, -1)
            value_layer = value_layer.contiguous().view(seq_len, batch_size, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)

        # Apply rotary position embedding
        if rotary_pos_emb is not None:
            query_layer = apply_rotary_pos_emb(query_layer, rotary_pos_emb)
            key_layer = apply_rotary_pos_emb(key_layer, rotary_pos_emb)

        # Apply compression to keys and values for efficiency
        # Reshape for compression: [s, b, h] where h = num_heads * head_dim
        key_compressed_input = key_layer.view(seq_len, batch_size, -1)
        value_compressed_input = value_layer.view(seq_len, batch_size, -1)
        
        # Compress and decompress (simulating learned compression)
        key_compressed = self.compression_network(key_compressed_input)
        value_compressed = self.compression_network(value_compressed_input)
        
        # Reshape back
        key_layer = key_compressed.view(seq_len, batch_size, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)
        value_layer = value_compressed.view(seq_len, batch_size, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)

        # Apply sparse block selection
        key_layer, value_layer = self.select_sparse_blocks(key_layer, value_layer)

        # Create sliding window mask
        sliding_window_mask = self.create_sliding_window_mask(seq_len, hidden_states.device)
        
        # Combine with existing attention mask if provided
        if attention_mask is not None:
            combined_mask = attention_mask + sliding_window_mask
        else:
            combined_mask = sliding_window_mask

        # Core attention computation
        context_layer = self.core_attention(
            query_layer, key_layer, value_layer, combined_mask, inference_params=inference_params
        )

        # Output projection
        output, bias = self.linear_proj(context_layer)
        return output, bias