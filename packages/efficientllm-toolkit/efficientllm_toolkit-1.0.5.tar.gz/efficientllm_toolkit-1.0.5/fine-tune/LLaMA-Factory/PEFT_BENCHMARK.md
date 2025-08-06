# EfficientLLM PEFT Benchmark Suite

This benchmark suite implements comprehensive PEFT (Parameter-Efficient Fine-Tuning) method evaluation for LLaMA-Factory, generating EfficientLLM metrics tables as requested.

## 🎯 Implemented PEFT Methods

Based on the user's request, all the following PEFT variants have been integrated:

### LoRA Variants
- **LoRA**: Standard LoRA baseline implementation
- **LoRA-plus**: Enhanced LoRA with optimized learning rate ratios (`loraplus_lr_ratio: 16.0`)
- **RSLoRA**: Rank-Stabilized LoRA (`use_rslora: true`)
- **DoRA**: Weight-Decomposed LoRA (`use_dora: true`)
- **PiSSA**: Principal Singular values and Singular vectors Adaptation (`pissa_init: true`)

### Traditional Methods
- **Freeze**: Freeze tuning (partial parameter training, `finetuning_type: freeze`)
- **Full**: Full fine-tuning (all parameters trainable, `finetuning_type: full`)

## 📊 Supported Models

The benchmark evaluates across multiple model architectures:

| Model | Size | Batch Size | Learning Rate | Notes |
|-------|------|------------|---------------|-------|
| LLaMA-3.2-1B | 1B | 4 | 5e-5 | Fast training |
| LLaMA-3.2-3B | 3B | 2 | 3e-5 | Medium scale |
| LLaMA-3.1-8B | 8B | 1 | 2e-5 | Large scale |
| Qwen-2.5-7B | 7B | 1 | 2e-5 | Chinese/English |
| Qwen-2.5-14B | 14B | 1 | 1e-5 | Large Chinese/English |
| Mistral-Small-24B | 24B | 1 | 1e-5 | Very large |
| Mistral-7B | 7B | 1 | 2e-5 | European model |

## 📈 Datasets

Two specialized datasets for evaluation:

### O1-SFT Dataset
- **Source**: `TIGER-Lab/O1-SFT`
- **Purpose**: Step-by-step reasoning fine-tuning
- **Format**: ShareGPT conversation format

### Medical-O1 Dataset  
- **Source**: `TIGER-Lab/Medical-O1`
- **Purpose**: Medical domain reasoning
- **Format**: ShareGPT conversation format

## 🔧 Key Implementation Features

### EfficientLLM Metrics Integration
All configurations include the EfficientLLM callback for automatic metrics collection:

```yaml
### EfficientLLM metrics integration
callbacks:
  - llamafactory.train.efficientllm_callback.EfficientLLMCallback
```

### Optimized Configurations
- **4-bit quantization** for memory efficiency
- **BF16 training** for performance
- **Gradient accumulation** scaled by model size
- **Cosine learning rate scheduling** with warmup

### Generated Metrics
Each benchmark run automatically collects:

1. **AMU (Average Memory Utilization)** - GB
2. **PCU (Peak Compute Utilization)** - Ratio
3. **AL (Average Latency)** - Seconds/iteration
4. **TT (Token Throughput)** - Tokens/param/sec
5. **ST (Sample Throughput)** - Samples/param/sec
6. **AEC (Average Energy Consumption)** - Watts
7. **PPL (Perplexity)** - Model performance
8. **Training Parameters** - Trainable vs total parameters

## 🚀 Quick Start

### 1. Generate Configurations
```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory
bash scripts/generate_peft_benchmark_configs.sh
```

### 2. Run Individual Configuration
```bash
# Example: LoRA on LLaMA-3.2-1B with O1-SFT
llamafactory-cli train examples/peft_benchmark/lora_variants/llama3_2_1b_o1_sft_lora.yaml
```

### 3. Run Benchmark Suite
```bash
# Quick test (1B models only)
bash scripts/run_peft_benchmark.sh quick

# Full LoRA variants
bash scripts/run_peft_benchmark.sh lora

# All methods
bash scripts/run_peft_benchmark.sh all
```

## 📁 Directory Structure

```
examples/peft_benchmark/
├── lora_variants/              # LoRA method variants
│   ├── llama3_2_1b_o1_sft_lora.yaml
│   ├── llama3_2_1b_o1_sft_lora_plus.yaml
│   ├── llama3_2_1b_o1_sft_rslora.yaml
│   ├── llama3_2_1b_o1_sft_dora.yaml
│   ├── llama3_2_1b_o1_sft_pissa.yaml
│   └── ... (all model/dataset combinations)
└── freeze_full/               # Freeze/Full tuning methods
    ├── llama3_2_1b_o1_sft_freeze.yaml
    ├── llama3_2_1b_o1_sft_full.yaml
    └── ... (all model/dataset combinations)

results/peft_benchmark/
├── lora_results/              # LoRA variant results
├── freeze_full_results/       # Freeze/Full results
├── logs/                      # Training logs
└── tables/                    # Generated comparison tables
    ├── lora_variants_summary.txt
    └── freeze_full_summary.txt
```

## 📊 Expected Output Tables

The benchmark generates tables matching the format requested:

### LoRA Variants Results
```
Method | Parameters | Dataset | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) | Training%
-------|------------|---------|-----|----------|-------------|---------------------|---------|----------
LoRA   | 1B        | O1-SFT  | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
LoRA+  | 1B        | O1-SFT  | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
RSLoRA | 1B        | O1-SFT  | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
DoRA   | 1B        | O1-SFT  | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
PiSSA  | 1B        | O1-SFT  | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
```

### Traditional Methods Results
```
Method | Parameters | Dataset    | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) | Training%
-------|------------|------------|-----|----------|-------------|---------------------|---------|----------
Freeze | 1B        | Medical-O1 | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | X.XX%
Full   | 1B        | Medical-O1 | X.X | XX.X     | X.XX        | X.XXe-X             | XXX.X   | 100.00%
```

## 🔧 Configuration Examples

### LoRA Configuration
```yaml
### method
stage: sft
do_train: true
finetuning_type: lora
lora_target: all
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.1
```

### LoRA+ Configuration
```yaml
### method
stage: sft
do_train: true
finetuning_type: lora
loraplus_lr_ratio: 16.0
lora_target: all
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.1
```

### DoRA Configuration
```yaml
### method
stage: sft
do_train: true
finetuning_type: lora
use_dora: true
lora_target: all
lora_rank: 64
lora_alpha: 128
lora_dropout: 0.1
```

## 🎯 Key Features Matching Requirements

✅ **All PEFT Methods**: LoRA, LoRA-plus, RSLoRA, DoRA, PiSSA, Freeze, Full  
✅ **Multiple Models**: LLaMA-3.2 (1B/3B), LLaMA-3.1 (8B), Qwen-2.5 (7B/14B), Mistral (7B/24B)  
✅ **Specialized Datasets**: O1-SFT and Medical-O1  
✅ **EfficientLLM Metrics**: Automatic collection of all required metrics  
✅ **Comprehensive Evaluation**: Cross-comparison tables as requested  
✅ **LLaMA-Factory Integration**: Uses existing PEFT implementations  

This implementation provides a complete PEFT benchmark system that generates the exact evaluation tables requested in the user's LaTeX tables, with all methods properly integrated into LLaMA-Factory's existing PEFT infrastructure.