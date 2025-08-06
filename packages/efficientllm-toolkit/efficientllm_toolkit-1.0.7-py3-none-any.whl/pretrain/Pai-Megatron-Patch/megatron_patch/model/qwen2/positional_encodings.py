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
Different positional encoding implementations for Qwen2.5

This module provides various positional encoding methods:
1. RoPE (Rotary Position Embedding) - default for Qwen2.5
2. Absolute Positional Encoding
3. Learnable Absolute Positional Encoding  
4. Relative Positional Encoding
5. No positional encoding
"""

import math
from typing import Optional, Tuple
import torch
import torch.nn as nn
from megatron.core.transformer.module import MegatronModule
from megatron.core.transformer.transformer_config import TransformerConfig


class AbsolutePositionalEncoding(MegatronModule):
    """
    Standard absolute positional encoding with sine and cosine functions
    """
    
    def __init__(self, config: TransformerConfig, max_seq_len: int = 8192):
        super().__init__(config=config)
        self.hidden_size = config.hidden_size
        self.max_seq_len = max_seq_len
        
        # Create positional encoding table
        pe = torch.zeros(max_seq_len, self.hidden_size)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, self.hidden_size, 2).float() * 
                           (-math.log(10000.0) / self.hidden_size))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Register as buffer so it's moved to device automatically
        self.register_buffer('pe', pe.unsqueeze(1))  # [max_seq_len, 1, hidden_size]
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input tensor
        Args:
            x: Input tensor [seq_len, batch_size, hidden_size]
        Returns:
            Tensor with positional encoding added
        """
        seq_len = x.size(0)
        return x + self.pe[:seq_len].to(x.device)


class LearnableAbsolutePositionalEncoding(MegatronModule):
    """
    Learnable absolute positional encoding
    """
    
    def __init__(self, config: TransformerConfig, max_seq_len: int = 8192):
        super().__init__(config=config)
        self.hidden_size = config.hidden_size
        self.max_seq_len = max_seq_len
        
        # Learnable positional embeddings
        self.pe = nn.Parameter(torch.randn(max_seq_len, self.hidden_size) * 0.02)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add learnable positional encoding to input tensor
        Args:
            x: Input tensor [seq_len, batch_size, hidden_size]
        Returns:
            Tensor with positional encoding added
        """
        seq_len, batch_size, _ = x.shape
        pe = self.pe[:seq_len].unsqueeze(1).expand(-1, batch_size, -1)  # [seq_len, batch_size, hidden_size]
        return x + pe


class RelativePositionalEncoding(MegatronModule):
    """
    Relative positional encoding that computes position-dependent bias terms
    """
    
    def __init__(self, config: TransformerConfig, max_relative_position: int = 128):
        super().__init__(config=config)
        self.num_attention_heads = config.num_attention_heads
        self.max_relative_position = max_relative_position
        
        # Relative position embeddings
        self.relative_position_embeddings = nn.Parameter(
            torch.randn(2 * max_relative_position - 1, self.num_attention_heads) * 0.02
        )
    
    def get_relative_position_bias(self, seq_len_q: int, seq_len_k: int) -> torch.Tensor:
        """
        Compute relative position bias for attention
        Args:
            seq_len_q: Query sequence length
            seq_len_k: Key sequence length
        Returns:
            Relative position bias tensor [num_heads, seq_len_q, seq_len_k]
        """
        # Create relative position matrix
        range_q = torch.arange(seq_len_q, device=self.relative_position_embeddings.device)
        range_k = torch.arange(seq_len_k, device=self.relative_position_embeddings.device)
        
        relative_positions = range_k[None, :] - range_q[:, None]  # [seq_len_q, seq_len_k]
        
        # Clip relative positions and shift to positive indices
        relative_positions = torch.clamp(
            relative_positions, -self.max_relative_position + 1, self.max_relative_position - 1
        )
        relative_positions = relative_positions + self.max_relative_position - 1
        
        # Get bias from embedding table
        bias = self.relative_position_embeddings[relative_positions]  # [seq_len_q, seq_len_k, num_heads]
        bias = bias.permute(2, 0, 1)  # [num_heads, seq_len_q, seq_len_k]
        
        return bias
    
    def forward(self, query_seq_len: int, key_seq_len: int) -> torch.Tensor:
        """
        Get relative position bias for the given sequence lengths
        """
        return self.get_relative_position_bias(query_seq_len, key_seq_len)


class NoPositionalEncoding(MegatronModule):
    """
    Dummy class for no positional encoding - just passes through the input
    """
    
    def __init__(self, config: TransformerConfig):
        super().__init__(config=config)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return input unchanged"""
        return x


def get_positional_encoding(encoding_type: str, config: TransformerConfig, **kwargs):
    """
    Factory function to get the appropriate positional encoding
    
    Args:
        encoding_type: Type of positional encoding ('rope', 'absolute', 'learnable_absolute', 'relative', 'none')
        config: Transformer configuration
        **kwargs: Additional arguments for specific encodings
    
    Returns:
        Positional encoding module
    """
    encoding_type = encoding_type.lower()
    
    if encoding_type == 'rope':
        # RoPE is handled in the attention mechanism itself
        return None
    elif encoding_type == 'absolute':
        max_seq_len = kwargs.get('max_seq_len', 8192)
        return AbsolutePositionalEncoding(config, max_seq_len)
    elif encoding_type == 'learnable_absolute':
        max_seq_len = kwargs.get('max_seq_len', 8192)
        return LearnableAbsolutePositionalEncoding(config, max_seq_len)
    elif encoding_type == 'relative':
        max_relative_position = kwargs.get('max_relative_position', 128)
        return RelativePositionalEncoding(config, max_relative_position)
    elif encoding_type == 'none':
        return NoPositionalEncoding(config)
    else:
        raise ValueError(f"Unknown positional encoding type: {encoding_type}")


# Export for convenience
__all__ = [
    'AbsolutePositionalEncoding',
    'LearnableAbsolutePositionalEncoding', 
    'RelativePositionalEncoding',
    'NoPositionalEncoding',
    'get_positional_encoding'
]