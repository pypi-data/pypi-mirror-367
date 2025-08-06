#!/bin/bash

# 简化的PEFT配置生成器 - 为EfficientLLM基准测试生成所有配置

set -e

CONFIG_DIR="/work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory/examples/peft_benchmark"
rm -rf "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR"/{lora_variants,freeze_full}

echo "开始生成PEFT基准配置..."

# 生成单个配置文件的函数
generate_single_config() {
    local model_key="$1"
    local model_path="$2" 
    local dataset="$3"
    local method="$4"
    local extra_config="$5"
    local finetuning_type="$6"
    
    # 根据模型大小设置参数
    local batch_size=1
    local grad_acc=8
    local learning_rate="2e-5"
    
    case "$model_key" in
        *"1b"*) batch_size=4; grad_acc=4; learning_rate="5e-5" ;;
        *"3b"*) batch_size=2; grad_acc=8; learning_rate="3e-5" ;;
    esac
    
    # 确定输出目录
    local config_type="lora_variants"
    if [[ "$method" == "freeze" || "$method" == "full" ]]; then
        config_type="freeze_full"
    fi
    
    local output_file="$CONFIG_DIR/${config_type}/${model_key}_${dataset}_${method}.yaml"
    
    cat > "$output_file" << EOF
# EfficientLLM PEFT基准: ${method}
# 模型: ${model_path}
# 数据集: ${dataset}

### model
model_name_or_path: ${model_path}
quantization_bit: 4
quantization_method: bitsandbytes

### method
stage: sft
do_train: true
finetuning_type: ${finetuning_type}
${extra_config}
lora_target: all
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.1

### dataset
dataset: ${dataset}
template: default
cutoff_len: 2048
max_samples: 1000
overwrite_cache: true
preprocessing_num_workers: 16

### output
output_dir: ./saves/peft_benchmark/${model_key}_${dataset}_${method}
logging_steps: 10
save_steps: 500
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: ${batch_size}
gradient_accumulation_steps: ${grad_acc}
learning_rate: ${learning_rate}
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

### EfficientLLM指标集成
callbacks:
  - llamafactory.train.efficientllm_callback.EfficientLLMCallback

### save
save_only_model: false

### logging
log_level: info
run_name: efficientllm_${model_key}_${dataset}_${method}
EOF

    echo "已生成: ${output_file}"
}

# 生成所有配置
count=0

# LLaMA-3.2-1B 配置
echo "生成 LLaMA-3.2-1B 配置..."
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "lora" "" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "lora_plus" "loraplus_lr_ratio: 16.0" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "rslora" "use_rslora: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "dora" "use_dora: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "pissa" "pissa_init: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "freeze" "freeze_trainable_layers: 2" "freeze"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "o1_sft" "full" "" "full"

generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "lora" "" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "lora_plus" "loraplus_lr_ratio: 16.0" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "rslora" "use_rslora: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "dora" "use_dora: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "pissa" "pissa_init: true" "lora"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "freeze" "freeze_trainable_layers: 2" "freeze"
generate_single_config "llama3_2_1b" "meta-llama/Llama-3.2-1B" "medical_o1" "full" "" "full"

# LLaMA-3.2-3B 配置
echo "生成 LLaMA-3.2-3B 配置..."
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "o1_sft" "lora" "" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "o1_sft" "lora_plus" "loraplus_lr_ratio: 16.0" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "o1_sft" "rslora" "use_rslora: true" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "o1_sft" "dora" "use_dora: true" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "o1_sft" "pissa" "pissa_init: true" "lora"

generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "medical_o1" "lora" "" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "medical_o1" "lora_plus" "loraplus_lr_ratio: 16.0" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "medical_o1" "rslora" "use_rslora: true" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "medical_o1" "dora" "use_dora: true" "lora"
generate_single_config "llama3_2_3b" "meta-llama/Llama-3.2-3B" "medical_o1" "pissa" "pissa_init: true" "lora"

# Qwen-2.5-7B 配置 (选择性生成)
echo "生成 Qwen-2.5-7B 配置..."
generate_single_config "qwen2_5_7b" "Qwen/Qwen2.5-7B" "o1_sft" "lora" "" "lora"
generate_single_config "qwen2_5_7b" "Qwen/Qwen2.5-7B" "o1_sft" "dora" "use_dora: true" "lora"
generate_single_config "qwen2_5_7b" "Qwen/Qwen2.5-7B" "medical_o1" "lora" "" "lora"
generate_single_config "qwen2_5_7b" "Qwen/Qwen2.5-7B" "medical_o1" "dora" "use_dora: true" "lora"

echo ""
echo "==========================================="
echo "PEFT配置生成完成！"
echo "==========================================="

# 统计生成的配置数量
lora_count=$(find "$CONFIG_DIR/lora_variants" -name "*.yaml" | wc -l)
freeze_full_count=$(find "$CONFIG_DIR/freeze_full" -name "*.yaml" | wc -l)
total_count=$((lora_count + freeze_full_count))

echo "已生成配置文件: $total_count 个"
echo "  - LoRA变体: $lora_count 个"
echo "  - Freeze/Full: $freeze_full_count 个"
echo ""
echo "配置目录: $CONFIG_DIR"
echo ""
echo "使用示例:"
echo "  llamafactory-cli train $CONFIG_DIR/lora_variants/llama3_2_1b_o1_sft_lora.yaml"
echo ""
echo "运行基准测试:"
echo "  bash scripts/run_peft_benchmark.sh quick"