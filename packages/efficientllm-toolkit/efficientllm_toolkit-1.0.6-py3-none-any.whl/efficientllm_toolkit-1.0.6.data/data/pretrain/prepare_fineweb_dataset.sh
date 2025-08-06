#!/bin/bash

# Dataset preparation script for EfficientLLM training
# Downloads and prepares HuggingFace fine-webedu v1.2.0 sample-350BT dataset

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
DATA_DIR="${SCRIPT_DIR}/../data/fineweb_edu"
CACHE_DIR="${DATA_DIR}/cache"
PROCESSED_DIR="${DATA_DIR}/processed"

# Create directories
mkdir -p "${DATA_DIR}"
mkdir -p "${CACHE_DIR}" 
mkdir -p "${PROCESSED_DIR}"

echo "=========================================="
echo "EfficientLLM Dataset Preparation"
echo "=========================================="
echo "Dataset: HuggingFaceFW/fineweb-edu"
echo "Config: sample-350BT"
echo "Version: 1.2.0"
echo "Cache Dir: ${CACHE_DIR}"
echo "Processed Dir: ${PROCESSED_DIR}"
echo "=========================================="

# Python script for dataset download and preprocessing
cat > "${SCRIPT_DIR}/prepare_dataset.py" << 'EOF'
#!/usr/bin/env python3
"""
Dataset preparation script for fine-webedu
Downloads and preprocesses the HuggingFace fine-webedu dataset for Megatron training
"""

import os
import sys
from datasets import load_dataset
from transformers import AutoTokenizer
import json
import argparse
from tqdm import tqdm
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Prepare fine-webedu dataset")
    parser.add_argument("--cache_dir", required=True, help="Cache directory")
    parser.add_argument("--output_dir", required=True, help="Output directory")
    parser.add_argument("--config", default="sample-350BT", help="Dataset config")
    parser.add_argument("--version", default="1.2.0", help="Dataset version")
    parser.add_argument("--tokenizer", default="Qwen/Qwen2.5-0.5B", help="Tokenizer to use")
    parser.add_argument("--max_seq_length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument("--num_samples", type=int, default=None, help="Number of samples to process (for testing)")
    
    args = parser.parse_args()
    
    print(f"Loading dataset: HuggingFaceFW/fineweb-edu")
    print(f"Config: {args.config}")
    print(f"Version: {args.version}")
    print(f"Cache dir: {args.cache_dir}")
    print(f"Output dir: {args.output_dir}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, trust_remote_code=True)
    
    # Add pad token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load dataset
    print("Loading dataset...")
    try:
        dataset = load_dataset(
            "HuggingFaceFW/fineweb-edu",
            name=args.config,
            revision=args.version,
            cache_dir=args.cache_dir,
            streaming=False  # Download full dataset for processing
        )
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Trying without revision specification...")
        dataset = load_dataset(
            "HuggingFaceFW/fineweb-edu", 
            name=args.config,
            cache_dir=args.cache_dir,
            streaming=False
        )
    
    print(f"Dataset loaded: {dataset}")
    
    # Process training split
    if 'train' in dataset:
        train_data = dataset['train']
        print(f"Training samples: {len(train_data)}")
        
        # Limit samples for testing if specified
        if args.num_samples:
            train_data = train_data.select(range(min(args.num_samples, len(train_data))))
            print(f"Using {len(train_data)} samples for processing")
        
        # Process and tokenize
        print("Processing and tokenizing data...")
        processed_data = []
        
        for i, example in enumerate(tqdm(train_data)):
            # Extract text
            text = example.get('text', '')
            if not text:
                continue
                
            # Tokenize
            tokens = tokenizer(
                text,
                max_length=args.max_seq_length,
                truncation=True,
                padding=False,
                return_tensors=None
            )
            
            # Store tokenized data
            processed_data.append({
                'input_ids': tokens['input_ids'],
                'attention_mask': tokens['attention_mask'],
                'text_length': len(text),
                'token_length': len(tokens['input_ids'])
            })
            
            # Save intermediate results periodically
            if (i + 1) % 10000 == 0:
                print(f"Processed {i + 1} samples...")
        
        # Save processed data
        print("Saving processed data...")
        
        # Save as JSON lines for Megatron
        jsonl_path = os.path.join(args.output_dir, "fineweb_edu_train.jsonl")
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for item in processed_data:
                json.dump({
                    'text': tokenizer.decode(item['input_ids'], skip_special_tokens=True),
                    'input_ids': item['input_ids'],
                    'length': item['token_length']
                }, f, ensure_ascii=False)
                f.write('\n')
        
        # Save statistics
        stats = {
            'total_samples': len(processed_data),
            'avg_text_length': np.mean([item['text_length'] for item in processed_data]),
            'avg_token_length': np.mean([item['token_length'] for item in processed_data]),
            'max_token_length': max([item['token_length'] for item in processed_data]),
            'min_token_length': min([item['token_length'] for item in processed_data]),
            'tokenizer': args.tokenizer,
            'max_seq_length': args.max_seq_length,
            'dataset_config': args.config,
            'dataset_version': args.version
        }
        
        stats_path = os.path.join(args.output_dir, "dataset_stats.json")
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Dataset processing completed!")
        print(f"JSONL file: {jsonl_path}")
        print(f"Statistics: {stats_path}")
        print(f"Total samples: {stats['total_samples']}")
        print(f"Average token length: {stats['avg_token_length']:.1f}")
        
    else:
        print("No 'train' split found in dataset")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x "${SCRIPT_DIR}/prepare_dataset.py"

# Run the dataset preparation
echo "Starting dataset preparation..."
python3 "${SCRIPT_DIR}/prepare_dataset.py" \
    --cache_dir "${CACHE_DIR}" \
    --output_dir "${PROCESSED_DIR}" \
    --config "sample-350BT" \
    --version "1.2.0" \
    --tokenizer "Qwen/Qwen2.5-0.5B" \
    --max_seq_length 2048 \
    --num_samples 1000  # For testing, remove this for full dataset

echo "=========================================="
echo "Dataset preparation completed!"
echo "=========================================="
echo "Processed data location: ${PROCESSED_DIR}"
echo "To use in training, set:"
echo "export DATASET_PATH=\"${PROCESSED_DIR}/fineweb_edu_train.jsonl\""
echo ""
echo "Or update your training script to use:"
echo "DATASET_PATH=\"${PROCESSED_DIR}/fineweb_edu_train.jsonl\""