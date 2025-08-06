# EfficientLLM Attention-Free Mechanisms Benchmark

本实验系统实现了论文表格中四种attention-free机制的对比实验：Qwen2.5、Mamba、Pythia、RWKV。

## 实验目标

根据论文表格，我们需要评估以下模型在fine-webedu数据集上的效率指标：

| Method | Parameters | Context Length | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) |
|--------|------------|----------------|-----|----------|-------------|---------------------|---------|
| Qwen2.5 | 0.5B/1.5B/3B | 8K | 基准性能 | 内存使用 | 延迟 | 吞吐量 | 能耗 |
| Mamba | 0.5B/1.5B/3B | 8K | 高效架构 | 低内存 | 低延迟 | 线性复杂度 | 低能耗 |
| Pythia | 0.5B/1.5B/3B | 8K | 标准transformer | 标准内存 | 标准延迟 | 标准吞吐量 | 标准能耗 |
| RWKV | 0.5B/1.5B/3B | 8K | RNN-like | 常数内存 | 低延迟 | 线性复杂度 | 低能耗 |

## 目录结构

```
pretrain/
├── scripts/                                    # 实验脚本
│   ├── generate_attention_free_configs.sh      # 生成实验配置
│   ├── run_all_attention_free_experiments.sh   # 运行所有实验
│   ├── collect_attention_free_results.py       # 收集结果
│   ├── test_attention_free_setup.sh            # 快速测试
│   └── prepare_fineweb_dataset.sh              # 数据集准备
├── mamba/
│   └── train_mamba_fineweb.py                  # Mamba训练脚本
├── pythia/
│   └── train_pythia_fineweb.py                 # Pythia训练脚本
├── RWKV-LM/
│   └── train_rwkv_fineweb.py                   # RWKV训练脚本
├── Pai-Megatron-Patch/                         # Qwen2.5训练(现有)
└── experiments/attention_free_benchmark/       # 实验结果
    ├── results/                                # 模型输出
    ├── logs/                                   # 训练日志
    └── tables/                                 # 生成的表格
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install torch transformers datasets
pip install mamba-ssm  # For Mamba
pip install pandas numpy tensorboard

# 设置权限
chmod +x scripts/*.sh
```

### 2. 快速测试

在运行完整实验前，先进行快速测试验证环境：

```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/pretrain/scripts
./test_attention_free_setup.sh
```

这将：
- 创建小测试数据集
- 运行每个模型的短时间训练（10步）
- 验证EfficientLLM指标收集
- 测试结果处理脚本

### 3. 数据集准备

```bash
# 下载和预处理fine-webedu数据集
./prepare_fineweb_dataset.sh
```

### 4. 运行完整实验

```bash
# 运行所有模型和大小的实验
./run_all_attention_free_experiments.sh dsw cuda:0 10000

# 参数说明：
# dsw: 环境类型 (dsw/dlc)
# cuda:0: 设备
# 10000: 最大训练步数
```

### 5. 收集结果

```bash
# 生成论文格式表格
python collect_attention_free_results.py \
    --results_dir ./experiments/attention_free_benchmark/results \
    --output_dir ./experiments/attention_free_benchmark/tables
```

## 实验配置

### 模型架构配置

**Qwen2.5 (Transformer with GQA)**:
- 0.5B: 24层, 896隐藏维度, 14注意力头
- 1.5B: 28层, 1536隐藏维度, 12注意力头  
- 3B: 36层, 2048隐藏维度, 16注意力头

**Mamba (State Space Model)**:
- 0.5B: 24层, 768维度
- 1.5B: 48层, 1536维度
- 3B: 64层, 2560维度

**Pythia (Standard Transformer)**:
- 0.5B: 24层, 1024隐藏维度, 16注意力头
- 1.5B: 32层, 2048隐藏维度, 16注意力头
- 3B: 32层, 2560隐藏维度, 32注意力头

**RWKV (Receptance Weighted Key Value)**:
- 0.5B: 24层, 1024嵌入维度
- 1.5B: 32层, 2048嵌入维度
- 3B: 40层, 2560嵌入维度

### 训练配置

- **数据集**: HuggingFace fine-webedu v1.2.0 sample-350BT
- **上下文长度**: 8192 tokens
- **批大小**: 根据模型大小自适应 (0.5B:8, 1.5B:4, 3B:2)
- **学习率**: 1e-4
- **优化器**: AdamW (weight_decay=0.1)
- **精度**: bfloat16

## EfficientLLM指标说明

系统自动收集以下效率指标：

### 1. Average Memory Utilization (AMU)
- **公式**: `AMU = (1/T) * ∫[0,T] Memory_Used(t) dt`
- **单位**: GB
- **说明**: 平均内存使用量，越低越好

### 2. Average Latency (AL)  
- **公式**: `AL = Σ[i=1,N] (Computation_Time_i + Communication_Time_i) / N`
- **单位**: 秒/迭代
- **说明**: 平均每次迭代时间，越低越好

### 3. Token Throughput (TT)
- **公式**: `TT = Σ[i=1,N](Tokens_i / Model_Params) / Σ[i=1,N]Time_i`
- **单位**: Tokens/参数/秒
- **说明**: 标准化吞吐量，越高越好

### 4. Average Energy Consumption (AEC)
- **公式**: `AEC = (1/T) * ∫[0,T] P(t) dt`
- **单位**: 瓦特
- **说明**: 平均功耗，越低越好

### 5. Perplexity (PPL)
- **计算**: `PPL = exp(loss)`
- **说明**: 模型性能指标，越低越好

## 结果文件

实验完成后会生成：

1. **LaTeX表格** (`attention_free_table.tex`): 论文格式的表格
2. **CSV结果** (`attention_free_results.csv`): 便于查看的表格
3. **汇总报告** (`attention_free_report.txt`): 实验总结
4. **模型检查点**: 每个模型的训练checkpoint
5. **TensorBoard日志**: 训练过程可视化

## 预期结果分析

根据理论分析，预期结果：

**性能 (PPL, 越低越好)**:
- Qwen2.5: 最优（基准Transformer）
- Pythia: 标准Transformer性能
- Mamba: 接近Transformer
- RWKV: 略低于Transformer

**效率 (AMU/AL/AEC, 越低越好)**:
- Mamba: 内存和计算效率最优
- RWKV: 常数空间复杂度
- Qwen2.5: GQA优化的Transformer
- Pythia: 标准Transformer效率

**吞吐量 (TT, 越高越好)**:
- Mamba: 线性复杂度优势
- RWKV: RNN-like并行训练
- Qwen2.5: GQA优化
- Pythia: 标准性能

## 故障排除

### 常见问题

1. **内存不足**:
   ```bash
   # 减少批大小或序列长度
   ./run_all_attention_free_experiments.sh dsw cuda:0 5000
   ```

2. **Mamba安装失败**:
   ```bash
   pip install causal-conv1d>=1.4.0
   pip install mamba-ssm
   ```

3. **数据集下载失败**:
   ```bash
   # 手动设置HuggingFace缓存
   export HF_HOME=/path/to/cache
   export HF_DATASETS_CACHE=/path/to/datasets_cache
   ```

4. **GPU利用率监控失败**:
   ```bash
   # 确保nvidia-smi可用
   nvidia-smi
   ```

### 调试模式

```bash
# 运行单个模型测试
python mamba/train_mamba_fineweb.py \
    --model_size 0.5B \
    --data_path /path/to/test_data.jsonl \
    --output_dir ./debug_output \
    --max_steps 10 \
    --batch_size 1
```

## 扩展实验

### 添加新模型

1. 在对应目录创建训练脚本
2. 集成EfficientLLM指标收集
3. 更新配置生成脚本
4. 添加到运行脚本中

### 自定义指标

修改 `megatron_patch/efficientllm_metrics.py` 添加新的效率指标。

## 引用

如果使用此benchmark，请引用相关论文：

```bibtex
@article{efficientllm2024,
  title={EfficientLLM: A Comprehensive Benchmark for Large Language Model Efficiency},
  author={...},
  year={2024}
}
```