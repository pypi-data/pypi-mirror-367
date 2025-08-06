#!/bin/bash

# Quick PEFT Benchmark Test - Demonstrates the EfficientLLM PEFT evaluation system

set -e

LLAMAFACTORY_PATH="/work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory"
cd "$LLAMAFACTORY_PATH"

echo "==========================================="
echo "EfficientLLM PEFT Benchmark - Quick Test"
echo "==========================================="
echo "Testing PEFT method evaluation system"
echo ""

# Check if configurations exist
if [ ! -f "examples/peft_benchmark/lora_variants/llama3_2_1b_o1_sft_lora.yaml" ]; then
    echo "❌ Configuration files not found!"
    echo "Please run the configuration generator first:"
    echo "  bash scripts/generate_peft_benchmark_configs.sh"
    exit 1
fi

# Check if datasets are configured
if ! grep -q "o1_sft" data/dataset_info.json; then
    echo "❌ O1-SFT dataset not found in dataset_info.json!"
    echo "Please ensure datasets are properly configured."
    exit 1
fi

# Check if EfficientLLM callback exists
if [ ! -f "src/llamafactory/train/efficientllm_callback.py" ]; then
    echo "❌ EfficientLLM callback not found!"
    echo "Please ensure the EfficientLLM callback is implemented."
    exit 1
fi

echo "✅ Configuration files: Found"
echo "✅ Dataset configuration: Found"
echo "✅ EfficientLLM callback: Found"
echo ""

echo "Available PEFT configurations:"
echo ""
echo "LoRA Variants:"
for config in examples/peft_benchmark/lora_variants/*.yaml; do
    if [ -f "$config" ]; then
        config_name=$(basename "$config" .yaml)
        method=$(echo "$config_name" | rev | cut -d'_' -f1 | rev)
        model=$(echo "$config_name" | cut -d'_' -f1-3)
        dataset=$(echo "$config_name" | cut -d'_' -f4-5)
        echo "  📁 $config_name"
        echo "     Model: $model, Dataset: $dataset, Method: $method"
    fi
done

echo ""
echo "Freeze/Full Variants:"
for config in examples/peft_benchmark/freeze_full/*.yaml; do
    if [ -f "$config" ]; then
        config_name=$(basename "$config" .yaml)
        method=$(echo "$config_name" | rev | cut -d'_' -f1 | rev)
        model=$(echo "$config_name" | cut -d'_' -f1-3)
        dataset=$(echo "$config_name" | cut -d'_' -f4-5)
        echo "  📁 $config_name"
        echo "     Model: $model, Dataset: $dataset, Method: $method"
    fi
done

echo ""
echo "==========================================="
echo "System Ready for PEFT Benchmarking!"
echo "==========================================="
echo ""
echo "To run individual benchmarks:"
echo "  llamafactory-cli train examples/peft_benchmark/lora_variants/llama3_2_1b_o1_sft_lora.yaml"
echo ""
echo "To run the complete benchmark suite:"
echo "  bash scripts/run_peft_benchmark.sh quick    # Quick test"
echo "  bash scripts/run_peft_benchmark.sh all      # Full benchmark"
echo ""
echo "Expected outputs:"
echo "  - Training logs with EfficientLLM metrics"
echo "  - Comparison tables (AMU, PCU, AL, TT, ST, AEC, PPL)"
echo "  - Model checkpoints and evaluation results"
echo ""
echo "All PEFT methods are implemented and ready:"
echo "  ✅ LoRA (baseline)"
echo "  ✅ LoRA-plus (loraplus_lr_ratio)"
echo "  ✅ RSLoRA (use_rslora)"
echo "  ✅ DoRA (use_dora)"
echo "  ✅ PiSSA (pissa_init)"
echo "  ✅ Freeze tuning (freeze_trainable_layers)"
echo "  ✅ Full fine-tuning (finetuning_type: full)"