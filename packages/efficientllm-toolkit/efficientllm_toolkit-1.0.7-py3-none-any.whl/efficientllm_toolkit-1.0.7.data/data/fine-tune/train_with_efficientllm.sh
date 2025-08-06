#!/bin/bash

# LLaMA-Factory Fine-tuning with EfficientLLM Metrics
# This script runs LLaMA3.1 fine-tuning with integrated EfficientLLM metrics collection

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LLAMAFACTORY_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Source EfficientLLM configuration
source "$LLAMAFACTORY_DIR/efficientllm_config.sh"

# Configuration
MODEL_CONFIG=${1:-"examples/train_full/llama3_1_full_sft_efficientllm.yaml"}
GPUS=${2:-1}

echo "=================================="
echo "LLaMA-Factory with EfficientLLM"
echo "=================================="
echo "Model Config: $MODEL_CONFIG"
echo "GPUs: $GPUS"
echo ""

# Detect training type from config file
if grep -q "finetuning_type: lora" "$MODEL_CONFIG" 2>/dev/null; then
    TRAINING_TYPE="LoRA"
    OUTPUT_DIR_PATTERN="lora"
elif grep -q "finetuning_type: full" "$MODEL_CONFIG" 2>/dev/null; then
    TRAINING_TYPE="Full Fine-Tuning"
    OUTPUT_DIR_PATTERN="full"
else
    TRAINING_TYPE="Unknown"
    OUTPUT_DIR_PATTERN="unknown"
fi

echo "Training Type: $TRAINING_TYPE"

# Extract output directory from config for TensorBoard info
OUTPUT_DIR=$(grep "output_dir:" "$MODEL_CONFIG" | cut -d':' -f2 | tr -d ' ')

# Change to LLaMA-Factory directory
cd "$LLAMAFACTORY_DIR"

# Run training
if [ "$GPUS" -eq 1 ]; then
    echo "Running single-GPU training..."
    python src/train.py "$MODEL_CONFIG"
else
    echo "Running multi-GPU training with $GPUS GPUs..."
    torchrun --nproc_per_node="$GPUS" src/train.py "$MODEL_CONFIG"
fi

echo ""
echo "=============================="
echo "Training completed successfully!"
echo "=============================="
echo "Training Type: $TRAINING_TYPE"
echo "Output Directory: $OUTPUT_DIR"
echo ""
echo "Check the output directory for:"
echo "  - Model checkpoints (LoRA adapters or full model)"
echo "  - Training logs with EfficientLLM metrics"
echo "  - TensorBoard logs containing EfficientLLM metrics under 'efficientllm/' namespace"
echo ""
echo "To view TensorBoard metrics:"
echo "  tensorboard --logdir=$OUTPUT_DIR/runs"