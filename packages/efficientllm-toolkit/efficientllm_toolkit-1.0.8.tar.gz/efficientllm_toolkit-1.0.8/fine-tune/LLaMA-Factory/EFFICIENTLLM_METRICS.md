# EfficientLLM Metrics Integration for LLaMA-Factory

这个文档介绍了如何在LLaMA-Factory中使用EfficientLLM效率评估指标进行fine-tuning。

## 概述

EfficientLLM指标系统为LLaMA-Factory提供了全面的效率评估，包括：

1. **Average Memory Utilization (AMU)** - 平均内存利用率
2. **Peak Compute Utilization (PCU)** - 峰值计算利用率
3. **Average Latency (AL)** - 平均延迟
4. **Token Throughput (TT)** - 令牌吞吐量（预训练场景）
5. **Sample Throughput (ST)** - 样本吞吐量（微调场景）
6. **Inference Throughput (IT)** - 推理吞吐量
7. **Average Energy Consumption (AEC)** - 平均能耗

## 支持的训练类型

- ✅ **SFT (Supervised Fine-tuning)** - 监督微调
- ✅ **LoRA (Low-Rank Adaptation)** - 低秩适应
- ✅ **Full Fine-tuning** - 全参数微调

## 使用方法

### 1. 基础使用

#### Full Fine-tuning (全参数微调)
```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory

# 单GPU训练
bash scripts/train_with_efficientllm.sh examples/train_full/llama3_1_full_sft_efficientllm.yaml 1

# 多GPU训练
bash scripts/train_with_efficientllm.sh examples/train_full/llama3_1_full_sft_efficientllm.yaml 4
```

#### LoRA Fine-tuning (LoRA微调)
```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/fine-tune/LLaMA-Factory

# 单GPU训练
bash scripts/train_with_efficientllm.sh examples/train_lora/llama3_1_lora_sft_efficientllm.yaml 1

# 多GPU训练
bash scripts/train_with_efficientllm.sh examples/train_lora/llama3_1_lora_sft_efficientllm.yaml 4
```

### 2. 环境变量配置

通过环境变量控制EfficientLLM指标收集：

```bash
# 启用/禁用指标收集（默认：true）
export EFFICIENTLLM_METRICS_ENABLED=true

# 数据收集间隔，单位秒（默认：1.0）
export EFFICIENTLLM_COLLECTION_INTERVAL=1.0

# 历史数据缓存大小（默认：1000）
export EFFICIENTLLM_HISTORY_SIZE=1000

# 指标日志间隔，单位步数（默认：10）
export EFFICIENTLLM_LOG_INTERVAL=10
```

或者修改 `efficientllm_config.sh` 设置默认值。

### 3. 配置文件设置

确保你的YAML配置文件包含以下设置以启用TensorBoard日志：

```yaml
### output
output_dir: saves/llama3_1-8b/full/sft_efficientllm
logging_steps: 10
report_to: tensorboard  # 启用TensorBoard记录EfficientLLM指标
```

## 输出结果

### 控制台输出
训练过程中会看到EfficientLLM指标日志：
```
[EfficientLLM Metrics] Step 100:
  Loss: 2.345678
  AMU (GB): 23.45
  PCU (Ratio): 0.987
  AL (Seconds): 0.1234
  TT (Tokens/Param/Sec): 1.23e-06
  ST (Samples/Param/Sec): 4.56e-09
  AEC (Watts): 342.5
```

### TensorBoard可视化
指标会记录到TensorBoard的 `efficientllm/` 命名空间下：
- `efficientllm/amu_gb` - 平均内存利用率
- `efficientllm/pcu_ratio` - 峰值计算利用率
- `efficientllm/al_seconds` - 平均延迟
- `efficientllm/tt_tokens_per_param_per_sec` - 令牌吞吐量
- `efficientllm/st_samples_per_param_per_sec` - 样本吞吐量
- `efficientllm/aec_watts` - 平均能耗

查看TensorBoard：
```bash
tensorboard --logdir=saves/llama3_1-8b/full/sft_efficientllm/runs
```

## 配置文件示例

### LLaMA3.1 Full Fine-tuning
```yaml
### model
model_name_or_path: meta-llama/Meta-Llama-3.1-8B-Instruct
trust_remote_code: true

### method
stage: sft
do_train: true
finetuning_type: full

### dataset
dataset: identity,alpaca_en_demo
template: llama3
cutoff_len: 2048
max_samples: 1000

### output
output_dir: saves/llama3_1-8b/full/sft_efficientllm
logging_steps: 10
report_to: tensorboard  # 启用EfficientLLM指标

### train
per_device_train_batch_size: 1
gradient_accumulation_steps: 2
learning_rate: 1.0e-5
num_train_epochs: 3.0
bf16: true
```

### LLaMA3.1 LoRA Fine-tuning
```yaml
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
dataset: identity,alpaca_en_demo
template: llama3
cutoff_len: 2048
max_samples: 1000

### output
output_dir: saves/llama3_1-8b/lora/sft_efficientllm
logging_steps: 10
report_to: tensorboard  # 启用EfficientLLM指标

### train
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 1.0e-4
num_train_epochs: 3.0
bf16: true
```

## 指标定义

### Average Memory Utilization (AMU)
```
AMU = (1/T) * ∫₀ᵀ Memory_Used(t) dt
```
测量训练过程中GPU内存的平均使用情况。

### Peak Compute Utilization (PCU)
```
PCU = (1/T) * ∫₀ᵀ (Actual_GPU_Utilization(t) / Peak_GPU_Utilization) dt
```
测量GPU计算资源的平均利用率与理论峰值的比率。

### Average Latency (AL)
```
AL = Σᵢ(Computation_Time_i + Communication_Time_i) / N
```
测量每个训练步骤的平均时间。

### Sample Throughput (ST)
```
ST = Σᵢ(Samples_Processed_i / Model_Parameters) / Σᵢ Time_i
```
微调场景的归一化吞吐量指标。

### Average Energy Consumption (AEC)
```
AEC = (1/T) * ∫₀ᵀ P(t) dt
```
训练过程中的平均功耗。

## 系统要求

- NVIDIA GPU（nvidia-smi支持）
- PyTorch with CUDA
- psutil库

## 故障排除

### GPU指标显示为0
确保：
- 安装了NVIDIA驱动
- nvidia-smi命令可用
- GPU未处于独占计算模式

### 内存使用过高
指标收集器维护历史缓冲区，如果内存使用是问题，可以减少 `EFFICIENTLLM_HISTORY_SIZE`。

### 性能影响
后台监控的开销很小（约0.1% CPU）。如果需要，可以调整 `EFFICIENTLLM_COLLECTION_INTERVAL` 来降低收集频率。

## 与原有训练的对比

EfficientLLM指标系统提供了比传统指标（如FLOPS、参数数量、原始推理速度）更全面的评估：

- **AMU** vs 峰值内存使用 - 提供内存使用波动的全貌
- **PCU** vs 理论FLOPS - 反映真实GPU利用率，考虑通信开销
- **AL** vs 简单时间测量 - 明确测量响应性
- **ST** vs 原始吞吐量 - 提供不同模型大小间的归一化比较
- **AEC** vs 功耗忽略 - 量化实际能效