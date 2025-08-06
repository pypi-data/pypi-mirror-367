#!/usr/bin/env python3
"""
RWKV model training script for EfficientLLM attention-free benchmark
"""

import os
import sys
import time
import json
import argparse
import math
from typing import Dict, Any, Optional

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import DataLoader, DistributedSampler
from torch.utils.tensorboard import SummaryWriter

# Add RWKV to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RWKV-LM'))

# EfficientLLM metrics integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Pai-Megatron-Patch'))
from megatron_patch.efficientllm_metrics import get_metrics_collector, initialize_efficientllm_metrics, should_log_metrics


class RWKVConfig:
    """RWKV model configuration"""
    def __init__(self,
                 model_type: str = 'RWKV',
                 n_layer: int = 24,
                 n_embd: int = 1024,
                 vocab_size: int = 151936,  # Qwen2.5 tokenizer
                 ctx_len: int = 8192,
                 head_size_a: int = 64,
                 head_size_divisor: int = 8):
        self.model_type = model_type
        self.n_layer = n_layer
        self.n_embd = n_embd
        self.vocab_size = vocab_size
        self.ctx_len = ctx_len
        self.head_size_a = head_size_a
        self.head_size_divisor = head_size_divisor


# Simple RWKV implementation for the benchmark
class RWKVLayer(nn.Module):
    """RWKV Layer implementation"""
    def __init__(self, config: RWKVConfig, layer_id: int):
        super().__init__()
        self.layer_id = layer_id
        self.n_embd = config.n_embd
        self.head_size = config.head_size_a
        
        # Layer norm
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.ln2 = nn.LayerNorm(config.n_embd)
        
        # Attention components
        self.att_time_mix_k = nn.Parameter(torch.ones(1, 1, config.n_embd))
        self.att_time_mix_v = nn.Parameter(torch.ones(1, 1, config.n_embd))
        self.att_time_mix_r = nn.Parameter(torch.ones(1, 1, config.n_embd))
        
        self.att_key = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.att_value = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.att_receptance = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.att_output = nn.Linear(config.n_embd, config.n_embd, bias=False)
        
        # Feed forward components
        self.ffn_time_mix_k = nn.Parameter(torch.ones(1, 1, config.n_embd))
        self.ffn_time_mix_r = nn.Parameter(torch.ones(1, 1, config.n_embd))
        
        self.ffn_key = nn.Linear(config.n_embd, config.n_embd * 4, bias=False)
        self.ffn_value = nn.Linear(config.n_embd * 4, config.n_embd, bias=False)
        self.ffn_receptance = nn.Linear(config.n_embd, config.n_embd, bias=False)
        
    def forward(self, x, state=None):
        B, T, C = x.size()
        
        # Attention
        x_ln1 = self.ln1(x)
        
        # Time mixing for attention
        if state is not None and 'att' in state:
            x_prev = state['att']
        else:
            x_prev = torch.zeros_like(x_ln1[:, :1])
            x_prev = torch.cat([x_prev, x_ln1[:, :-1]], dim=1)
        
        xk = x_ln1 * self.att_time_mix_k + x_prev * (1 - self.att_time_mix_k)
        xv = x_ln1 * self.att_time_mix_v + x_prev * (1 - self.att_time_mix_v)
        xr = x_ln1 * self.att_time_mix_r + x_prev * (1 - self.att_time_mix_r)
        
        k = self.att_key(xk)
        v = self.att_value(xv)
        r = self.att_receptance(xr)
        
        # Simplified RWKV attention computation
        rwkv = torch.sigmoid(r) * v  # Simplified version
        rwkv = self.att_output(rwkv)
        
        x = x + rwkv
        
        # Feed forward
        x_ln2 = self.ln2(x)
        
        # Time mixing for FFN
        if state is not None and 'ffn' in state:
            x_prev_ffn = state['ffn']
        else:
            x_prev_ffn = torch.zeros_like(x_ln2[:, :1])
            x_prev_ffn = torch.cat([x_prev_ffn, x_ln2[:, :-1]], dim=1)
        
        xk_ffn = x_ln2 * self.ffn_time_mix_k + x_prev_ffn * (1 - self.ffn_time_mix_k)
        xr_ffn = x_ln2 * self.ffn_time_mix_r + x_prev_ffn * (1 - self.ffn_time_mix_r)
        
        k_ffn = self.ffn_key(xk_ffn)
        r_ffn = self.ffn_receptance(xr_ffn)
        
        # Squared ReLU activation
        k_ffn = torch.relu(k_ffn) ** 2
        ffn_out = torch.sigmoid(r_ffn) * self.ffn_value(k_ffn)
        
        x = x + ffn_out
        
        return x


class RWKVModel(nn.Module):
    """RWKV Model"""
    def __init__(self, config: RWKVConfig):
        super().__init__()
        self.config = config
        
        self.emb = nn.Embedding(config.vocab_size, config.n_embd)
        self.blocks = nn.ModuleList([RWKVLayer(config, i) for i in range(config.n_layer)])
        self.ln_out = nn.LayerNorm(config.n_embd)
        self.head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(self, input_ids, state=None):
        x = self.emb(input_ids)
        
        for block in self.blocks:
            x = block(x, state)
        
        x = self.ln_out(x)
        logits = self.head(x)
        
        return logits


class FineWebDataset:
    """Simple dataset for FineWeb-edu JSONL format"""
    def __init__(self, data_path: str, tokenizer, max_length: int = 8192):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = []
        
        print(f"Loading dataset from {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    if 'text' in item:
                        self.data.append(item['text'])
                except json.JSONDecodeError:
                    continue
        
        print(f"Loaded {len(self.data)} samples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        text = self.data[idx]
        
        # Tokenize
        tokens = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        input_ids = tokens['input_ids'].squeeze(0)
        
        # For language modeling, labels are the same as input_ids shifted by 1
        labels = input_ids.clone()
        labels[:-1] = input_ids[1:]
        labels[-1] = -100  # Ignore last token for loss computation
        
        return {
            'input_ids': input_ids,
            'labels': labels
        }


def setup_distributed():
    """Setup distributed training"""
    if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
        rank = int(os.environ['RANK'])
        world_size = int(os.environ['WORLD_SIZE'])
        local_rank = int(os.environ.get('LOCAL_RANK', 0))
        
        torch.cuda.set_device(local_rank)
        dist.init_process_group(backend='nccl', rank=rank, world_size=world_size)
        
        return rank, world_size, local_rank
    else:
        return 0, 1, 0


def train_step(model, batch, optimizer, criterion, device):
    """Single training step"""
    model.train()
    
    input_ids = batch['input_ids'].to(device)
    labels = batch['labels'].to(device)
    
    # Forward pass
    logits = model(input_ids)
    
    # Compute loss
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    
    loss = criterion(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
    
    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    
    return loss.item()


def main():
    parser = argparse.ArgumentParser(description='RWKV training for EfficientLLM benchmark')
    parser.add_argument('--model_size', type=str, required=True, choices=['0.5B', '1.5B', '3B'])
    parser.add_argument('--data_path', type=str, required=True, help='Path to FineWeb-edu JSONL dataset')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for checkpoints')
    parser.add_argument('--batch_size', type=int, default=8, help='Per-device batch size')
    parser.add_argument('--max_length', type=int, default=8192, help='Maximum sequence length')
    parser.add_argument('--learning_rate', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--num_epochs', type=int, default=1, help='Number of training epochs')
    parser.add_argument('--save_interval', type=int, default=1000, help='Save checkpoint every N steps')
    parser.add_argument('--log_interval', type=int, default=10, help='Log every N steps')
    parser.add_argument('--max_steps', type=int, default=None, help='Maximum training steps')
    
    args = parser.parse_args()
    
    # Setup distributed training
    rank, world_size, local_rank = setup_distributed()
    device = torch.device(f'cuda:{local_rank}' if torch.cuda.is_available() else 'cpu')
    
    if rank == 0:
        print(f"Starting RWKV {args.model_size} training")
        print(f"Device: {device}, World size: {world_size}")
    
    # Model configuration based on size
    model_configs = {
        '0.5B': RWKVConfig(n_layer=24, n_embd=1024, ctx_len=args.max_length),
        '1.5B': RWKVConfig(n_layer=32, n_embd=2048, ctx_len=args.max_length),
        '3B': RWKVConfig(n_layer=40, n_embd=2560, ctx_len=args.max_length)
    }
    
    config = model_configs[args.model_size]
    
    # Create model
    model = RWKVModel(config)
    model.to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    if rank == 0:
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
    
    # Initialize EfficientLLM metrics
    if rank == 0:
        initialize_efficientllm_metrics(trainable_params)
        metrics_collector = get_metrics_collector()
    
    # Setup distributed model
    if world_size > 1:
        model = nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
    
    # Load dataset
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B", trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    dataset = FineWebDataset(args.data_path, tokenizer, args.max_length)
    
    # Create dataloader
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank) if world_size > 1 else None
    dataloader = DataLoader(
        dataset, 
        batch_size=args.batch_size,
        sampler=sampler,
        shuffle=(sampler is None),
        num_workers=4,
        pin_memory=True
    )
    
    # Setup optimizer and loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.1)
    criterion = nn.CrossEntropyLoss(ignore_index=-100)
    
    # Setup tensorboard
    writer = None
    if rank == 0:
        os.makedirs(args.output_dir, exist_ok=True)
        log_dir = os.path.join(args.output_dir, 'tensorboard')
        writer = SummaryWriter(log_dir)
    
    # Training loop
    global_step = 0
    total_loss = 0.0
    
    if rank == 0:
        print("Starting training...")
    
    for epoch in range(args.num_epochs):
        if sampler:
            sampler.set_epoch(epoch)
            
        for step, batch in enumerate(dataloader):
            if rank == 0:
                metrics_collector.record_iteration_start()
            
            # Training step
            step_start_time = time.time()
            loss = train_step(model, batch, optimizer, criterion, device)
            step_time = time.time() - step_start_time
            
            # Metrics tracking
            if rank == 0:
                # Calculate tokens processed
                batch_size = batch['input_ids'].size(0)
                seq_len = batch['input_ids'].size(1)
                tokens_processed = batch_size * seq_len
                
                metrics_collector.record_iteration_end(
                    tokens_processed=tokens_processed,
                    samples_processed=batch_size
                )
            
            total_loss += loss
            global_step += 1
            
            # Logging
            if rank == 0 and (step + 1) % args.log_interval == 0:
                avg_loss = total_loss / args.log_interval
                
                print(f"Epoch {epoch+1}, Step {global_step}: Loss = {avg_loss:.6f}, Time = {step_time:.3f}s")
                
                if writer:
                    writer.add_scalar('train/loss', avg_loss, global_step)
                    writer.add_scalar('train/step_time', step_time, global_step)
                
                # Log EfficientLLM metrics
                if should_log_metrics(global_step):
                    metrics_collector.log_metrics(global_step, avg_loss, writer)
                
                total_loss = 0.0
            
            # Save checkpoint
            if rank == 0 and (step + 1) % args.save_interval == 0:
                checkpoint_path = os.path.join(args.output_dir, f'checkpoint-{global_step}.pt')
                torch.save({
                    'model_state_dict': model.state_dict() if world_size == 1 else model.module.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'step': global_step,
                    'loss': avg_loss,
                    'config': config.__dict__
                }, checkpoint_path)
                print(f"Saved checkpoint: {checkpoint_path}")
            
            # Early stopping
            if args.max_steps and global_step >= args.max_steps:
                if rank == 0:
                    print(f"Reached maximum steps ({args.max_steps}), stopping training")
                break
        
        if args.max_steps and global_step >= args.max_steps:
            break
    
    # Final metrics and cleanup
    if rank == 0:
        print("Training completed!")
        
        # Final metrics log
        final_metrics = metrics_collector.get_all_metrics()
        print("\nFinal EfficientLLM Metrics:")
        print(f"  AMU (GB): {final_metrics.amu:.2f}")
        print(f"  PCU (Ratio): {final_metrics.pcu:.3f}")
        print(f"  AL (Seconds): {final_metrics.al:.4f}")
        print(f"  TT (Tokens/Param/Sec): {final_metrics.tt:.2e}")
        print(f"  AEC (Watts): {final_metrics.aec:.2f}")
        
        # Save final metrics
        metrics_path = os.path.join(args.output_dir, 'efficientllm_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump({
                'model_type': 'rwkv',
                'model_size': args.model_size,
                'parameters': trainable_params,
                'context_length': args.max_length,
                'metrics': {
                    'ppl': None,  # Would need validation set to compute
                    'amu_gb': final_metrics.amu,
                    'al_seconds': final_metrics.al,
                    'tt_tokens_per_param_per_sec': final_metrics.tt,
                    'aec_watts': final_metrics.aec
                }
            }, f, indent=2)
        
        print(f"Metrics saved to: {metrics_path}")
        
        if writer:
            writer.close()
    
    # Cleanup distributed
    if world_size > 1:
        dist.destroy_process_group()


if __name__ == '__main__':
    main()