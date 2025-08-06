#!/usr/bin/env python3
"""
Mamba model training script for EfficientLLM attention-free benchmark
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import DataLoader, DistributedSampler
from torch.utils.tensorboard import SummaryWriter

# Add mamba to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mamba'))

try:
    from mamba_ssm import Mamba
    from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
except ImportError:
    print("Mamba SSM not found. Please install: pip install mamba-ssm")
    sys.exit(1)

# EfficientLLM metrics integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Pai-Megatron-Patch'))
from megatron_patch.efficientllm_metrics import get_metrics_collector, initialize_efficientllm_metrics, should_log_metrics


class MambaConfig:
    """Mamba model configuration"""
    def __init__(self, 
                 d_model: int = 768,
                 n_layer: int = 24,
                 vocab_size: int = 151936,  # Qwen2.5 tokenizer
                 ssm_cfg: Dict[str, Any] = None,
                 rms_norm: bool = True,
                 residual_in_fp32: bool = True,
                 fused_add_norm: bool = True,
                 pad_vocab_size_multiple: int = 8):
        self.d_model = d_model
        self.n_layer = n_layer
        self.vocab_size = vocab_size
        self.ssm_cfg = ssm_cfg or {}
        self.rms_norm = rms_norm
        self.residual_in_fp32 = residual_in_fp32
        self.fused_add_norm = fused_add_norm
        self.pad_vocab_size_multiple = pad_vocab_size_multiple


class FineWebDataset:
    """Simple dataset for FineWeb-edu JSONL format"""
    def __init__(self, data_path: str, tokenizer, max_length: int = 8192):
        from transformers import AutoTokenizer
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


def create_model(config: MambaConfig) -> nn.Module:
    """Create Mamba model"""
    model = MambaLMHeadModel(
        d_model=config.d_model,
        n_layer=config.n_layer,
        vocab_size=config.vocab_size,
        ssm_cfg=config.ssm_cfg,
        rms_norm=config.rms_norm,
        residual_in_fp32=config.residual_in_fp32,
        fused_add_norm=config.fused_add_norm,
        pad_vocab_size_multiple=config.pad_vocab_size_multiple
    )
    
    return model


def train_step(model, batch, optimizer, criterion, device):
    """Single training step"""
    model.train()
    
    input_ids = batch['input_ids'].to(device)
    labels = batch['labels'].to(device)
    
    # Forward pass
    logits = model(input_ids).logits
    
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
    parser = argparse.ArgumentParser(description='Mamba training for EfficientLLM benchmark')
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
        print(f"Starting Mamba {args.model_size} training")
        print(f"Device: {device}, World size: {world_size}")
    
    # Model configuration based on size
    model_configs = {
        '0.5B': MambaConfig(d_model=768, n_layer=24),
        '1.5B': MambaConfig(d_model=1536, n_layer=48),
        '3B': MambaConfig(d_model=2560, n_layer=64)
    }
    
    config = model_configs[args.model_size]
    
    # Create model
    model = create_model(config)
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
                'model_type': 'mamba',
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