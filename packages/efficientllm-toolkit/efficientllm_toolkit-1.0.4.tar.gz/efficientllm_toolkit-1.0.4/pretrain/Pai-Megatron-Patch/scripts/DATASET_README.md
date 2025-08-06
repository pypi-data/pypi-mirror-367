# EfficientLLM Training with Fine-WebEdu Dataset

本文档说明如何使用HuggingFace fine-webedu v1.2.0 sample-350BT数据集进行EfficientLLM实验。

## 数据集信息

- **数据集**: HuggingFaceFW/fineweb-edu  
- **配置**: sample-350BT
- **版本**: v1.2.0
- **大小**: 约350B tokens的采样版本
- **内容**: 高质量教育网页内容，经过FineWeb过滤和去重

## 准备步骤

### 1. 下载和预处理数据集

```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/pretrain/Pai-Megatron-Patch/scripts
./prepare_fineweb_dataset.sh
```

这个脚本会：
- 从HuggingFace下载fine-webedu数据集
- 使用Qwen2.5分词器进行预处理
- 转换为JSONL格式供Megatron使用
- 生成数据集统计信息

### 2. 生成训练配置

```bash
./generate_efficientllm_configs.sh
```

这将在`../examples/efficientllm_benchmark/`目录下生成所有实验配置文件。

### 3. 运行训练实验

选择要运行的实验配置：

```bash
cd ../examples/efficientllm_benchmark/attention_variants
./run_gqa_1.5B.sh dsw
```

## 实验配置

### 注意力机制变体
- **MQA** (Multi-Query Attention): 0.5B, 1.5B, 3B
- **GQA** (Grouped-Query Attention): 0.5B, 1.5B, 3B  
- **MLA** (Multi-Head Latent Attention): 0.5B, 1.5B, 3B
- **NSA** (Native Sparse Attention): 0.5B, 1.5B, 3B

### 位置编码变体 (1.5B模型)
- **RoPE** (Rotary Position Embedding)
- **Absolute** Positional Encoding
- **Learnable Absolute** Positional Encoding
- **Relative** Positional Encoding
- **None** (无位置编码)

### MoE变体
- **Dense**: 1.5B, 3B
- **MoE**: 0.5B×8, 1.5B×8

## 训练参数

### 数据集配置
- **序列长度**: 2048
- **分词器**: Qwen2.5
- **数据分割**: 99% train, 1% validation, 0% test
- **训练token数**: 100,000 (可调整)

### 模型配置
根据模型大小自动设置：

**0.5B模型**:
- 层数: 24, 隐藏维度: 896, 注意力头: 14
- 批大小: 4

**1.5B模型**:
- 层数: 28, 隐藏维度: 1536, 注意力头: 12  
- 批大小: 2

**3B模型**:
- 层数: 36, 隐藏维度: 2048, 注意力头: 16
- 批大小: 1

### 优化器配置
- **学习率**: 1e-4 → 1e-5 (cosine decay)
- **优化器**: AdamW (β1=0.9, β2=0.95)
- **权重衰减**: 0.1
- **梯度裁剪**: 1.0
- **精度**: bfloat16

## 输出结果

训练结果保存在：
```
./output/efficientllm_benchmark/{variant_name}_{model_size}/
├── checkpoint/     # 模型检查点
├── tensorboard/    # TensorBoard日志  
└── log/           # 训练日志
```

## 监控训练过程

### TensorBoard
```bash
tensorboard --logdir ./output/efficientllm_benchmark/*/tensorboard/
```

### 日志查看
```bash
tail -f ./output/efficientllm_benchmark/*/log/*.log
```

## 性能监控

所有训练脚本都集成了EfficientLLM性能监控器，会自动收集：

- **AMU**: Average Memory Utilization
- **PCU**: Peak Compute Utilization  
- **AL**: Average Latency
- **TT**: Token Throughput (pretraining场景)
- **AEC**: Average Energy Consumption

## 故障排除

### 数据集下载失败
```bash
# 手动设置HuggingFace缓存目录
export HF_HOME=/path/to/cache
export HF_DATASETS_CACHE=/path/to/datasets_cache
```

### GPU内存不足
- 减小批大小
- 启用gradient checkpointing
- 使用更小的模型变体

### 分词器错误
确保安装了最新版本的transformers：
```bash
pip install transformers>=4.35.0
```

## 实验建议

1. **小规模测试**: 先用较少的训练tokens验证配置
2. **逐步扩展**: 从小模型开始，验证后再扩展到大模型
3. **监控资源**: 使用性能监控器跟踪效率指标
4. **对比实验**: 使用相同超参数对比不同注意力机制

## 数据集引用

```bibtex
@misc{fineweb-edu,
  title={FineWeb-Edu: A Filtered Educational Web Dataset for Language Model Training},
  author={HuggingFace Team},
  year={2024},
  url={https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu}
}
```