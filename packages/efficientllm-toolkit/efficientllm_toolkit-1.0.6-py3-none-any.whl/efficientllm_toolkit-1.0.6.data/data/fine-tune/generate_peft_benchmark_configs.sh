#!/bin/bash

# PEFT Benchmark Configuration Generator for EfficientLLM
# Generates configurations for all PEFT methods across different models and datasets

set -e

# Base directory for configurations  
CONFIG_DIR="/work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory/examples/peft_benchmark"
mkdir -p "$CONFIG_DIR"/{lora_variants,freeze_full,results}

echo "==========================================="
echo "PEFT Benchmark Configuration Generator"
echo "==========================================="
echo "Generating configurations in: $CONFIG_DIR"

# Define models and datasets
MODELS=(
    "llama3_2_1b:meta-llama/Llama-3.2-1B"
    "llama3_2_3b:meta-llama/Llama-3.2-3B" 
    "llama3_1_8b:meta-llama/Llama-3.1-8B"
    "qwen2_5_7b:Qwen/Qwen2.5-7B"
    "qwen2_5_14b:Qwen/Qwen2.5-14B"
    "mistral_small_24b:mistralai/Mistral-Small-Instruct-2409"
    "mistral_7b:mistralai/Mistral-7B-v0.1"
)

DATASETS=("o1_sft" "medical_o1")

PEFT_METHODS=(
    "lora:LoRA baseline"
    "lora_plus:LoRA with LoRA+ optimization"
    "rslora:Rank-Stabilized LoRA"
    "dora:Weight-Decomposed LoRA (DoRA)"
    "pissa:Principal Singular values and Singular vectors Adaptation"
    "freeze:Freeze tuning (partial parameters)"
    "full:Full fine-tuning"
)

# Function to generate configuration file
generate_config() {
    local model_key="$1"
    local model_path="$2"
    local dataset="$3"
    local peft_method="$4"
    local description="$5"
    
    # Determine model size for batch size and other parameters
    local batch_size=1
    local gradient_accumulation_steps=8
    local max_samples=1000
    local learning_rate="2e-5"
    
    case "$model_key" in
        *"1b"*) batch_size=4; gradient_accumulation_steps=4; learning_rate="5e-5" ;;
        *"3b"*) batch_size=2; gradient_accumulation_steps=8; learning_rate="3e-5" ;;
        *"7b"*) batch_size=1; gradient_accumulation_steps=16; learning_rate="2e-5" ;;
        *"8b"*) batch_size=1; gradient_accumulation_steps=16; learning_rate="2e-5" ;;
        *"14b"*) batch_size=1; gradient_accumulation_steps=32; learning_rate="1e-5" ;;
        *"24b"*) batch_size=1; gradient_accumulation_steps=32; learning_rate="1e-5" ;;
    esac
    
    # Determine config type and parameters
    local config_type=""
    local finetuning_type="lora"
    local additional_params=""
    
    case "$peft_method" in
        "lora")
            config_type="lora_variants"
            additional_params=""
            ;;
        "lora_plus")
            config_type="lora_variants"
            additional_params="loraplus_lr_ratio: 16.0"
            ;;
        "rslora")
            config_type="lora_variants"
            additional_params="use_rslora: true"
            ;;
        "dora")
            config_type="lora_variants"
            additional_params="use_dora: true"
            ;;
        "pissa")
            config_type="lora_variants"
            additional_params="pissa_init: true"
            ;;
        "freeze")
            config_type="freeze_full"
            finetuning_type="freeze"
            additional_params="freeze_trainable_layers: 2"
            ;;
        "full")
            config_type="freeze_full"
            finetuning_type="full"
            additional_params=""
            batch_size=1
            gradient_accumulation_steps=$((gradient_accumulation_steps * 2))
            ;;
    esac
    
    local output_file="$CONFIG_DIR/${config_type}/${model_key}_${dataset}_${peft_method}.yaml"
    
    cat > "$output_file" << EOF
# EfficientLLM PEFT Benchmark: $description
# Model: $model_path
# Dataset: $dataset
# Method: $peft_method

### model
model_name_or_path: $model_path
quantization_bit: 4
quantization_method: bitsandbytes

### method
stage: sft
do_train: true
finetuning_type: $finetuning_type
$([ -n "$additional_params" ] && echo "$additional_params")
lora_target: all
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.1

### dataset
dataset: $dataset
template: default
cutoff_len: 2048
max_samples: $max_samples
overwrite_cache: true
preprocessing_num_workers: 16

### output
output_dir: ./saves/peft_benchmark/${model_key}_${dataset}_${peft_method}
logging_steps: 10
save_steps: 500
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: $batch_size
gradient_accumulation_steps: $gradient_accumulation_steps
learning_rate: $learning_rate
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
ddp_timeout: 7200

### eval
val_size: 0.1
per_device_eval_batch_size: 1
eval_strategy: steps
eval_steps: 500
dataloader_pin_memory: false

### EfficientLLM metrics integration
callbacks:
  - llamafactory.train.efficientllm_callback.EfficientLLMCallback

### save
save_only_model: false

### logging
log_level: info
run_name: efficientllm_${model_key}_${dataset}_${peft_method}
EOF

    echo "Generated: $output_file"
}

# Generate all configurations
echo ""
echo "Generating PEFT benchmark configurations..."
echo ""

config_count=0
for model_entry in "${MODELS[@]}"; do
    model_key="${model_entry%%:*}"
    model_path="${model_entry##*:}"
    
    for dataset in "${DATASETS[@]}"; do
        for peft_entry in "${PEFT_METHODS[@]}"; do
            peft_method="${peft_entry%%:*}"
            description="${peft_entry##*:}"
            
            generate_config "$model_key" "$model_path" "$dataset" "$peft_method" "$description"
            ((config_count++))
        done
    done
done

echo ""
echo "==========================================="
echo "Configuration generation completed!"
echo "==========================================="
echo "Generated $config_count configurations in: $CONFIG_DIR"
echo ""

# Count configurations by type
lora_count=$(find "$CONFIG_DIR/lora_variants" -name "*.yaml" 2>/dev/null | wc -l)
freeze_full_count=$(find "$CONFIG_DIR/freeze_full" -name "*.yaml" 2>/dev/null | wc -l)

echo "LoRA Variants: $lora_count configs"
echo "Freeze/Full Methods: $freeze_full_count configs"
echo ""
echo "Models covered: ${#MODELS[@]}"
echo "Datasets covered: ${#DATASETS[@]} (${DATASETS[*]})"
echo ""
echo "Usage example:"
echo "  cd $CONFIG_DIR/lora_variants"
echo "  llamafactory-cli train llama3_2_1b_o1_sft_lora.yaml"
echo ""
echo "Or use the benchmark runner:"
echo "  bash /work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory/scripts/run_peft_benchmark.sh"