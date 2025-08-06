#!/bin/bash

# Quick test script for EfficientLLM metrics integration
# This script runs a short training session to verify metrics collection

set -e

LLAMAFACTORY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$LLAMAFACTORY_DIR"

echo "========================================"
echo "EfficientLLM Metrics Integration Test"
echo "========================================"

# Source configuration
source "efficientllm_config.sh"

# Create a minimal test config
cat > test_efficientllm_config.yaml << EOF
### model
model_name_or_path: meta-llama/Meta-Llama-3.1-8B-Instruct
trust_remote_code: true

### method
stage: sft
do_train: true
finetuning_type: lora
lora_rank: 8
lora_target: all

### dataset
dataset: alpaca_en_demo
template: llama3
cutoff_len: 512
max_samples: 10
overwrite_cache: true
preprocessing_num_workers: 4

### output
output_dir: test_efficientllm_output
logging_steps: 1
save_steps: 5
plot_loss: true
overwrite_output_dir: true
report_to: tensorboard

### train
per_device_train_batch_size: 1
gradient_accumulation_steps: 1
learning_rate: 1.0e-4
num_train_epochs: 1.0
max_steps: 5
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
EOF

echo "Created test configuration with minimal data for quick validation"
echo "Running training for 5 steps to test EfficientLLM integration..."
echo ""

# Run test
python src/train.py test_efficientllm_config.yaml

echo ""
echo "========================================"
echo "Test completed!"
echo "========================================"
echo "Check for EfficientLLM metrics in the logs above."
echo "TensorBoard logs: test_efficientllm_output/runs"
echo ""
echo "Expected metrics to see:"
echo "  - [EfficientLLM Metrics] Step X: messages"
echo "  - AMU (GB), PCU (Ratio), AL (Seconds), etc."
echo ""
echo "Clean up test files:"
echo "  rm -rf test_efficientllm_output test_efficientllm_config.yaml"