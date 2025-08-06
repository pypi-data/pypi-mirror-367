# EfficientLLM Benchmark Suite for Qwen2.5

这个基准测试套件实现了论文中提到的各种高效注意力机制、位置编码方法和MoE变体，用于生成EfficientLLM评估表格。

## 📊 实现的变体

### 🔍 注意力机制
- **MQA (Multi-Query Attention)** - 单一K/V头，多个Q头
- **GQA (Grouped-Query Attention)** - Qwen2.5默认，分组查询注意力
- **MLA (Multi-Head Latent Attention)** - 基于DeepSeek-V2的潜在注意力
- **NSA (Native Sparse Attention)** - 原生稀疏注意力

### 📍 位置编码
- **RoPE** - 旋转位置嵌入（默认）
- **Absolute** - 绝对位置编码
- **Learnable Absolute** - 可学习绝对位置编码
- **Relative** - 相对位置编码
- **None** - 无位置编码

### 🎯 MoE变体
- **Dense** - 密集模型基线
- **MoE** - 专家混合模型（8个专家，Top-2路由）

## 🚀 快速开始

### 1. 生成配置文件
```bash
cd /work/nvme/bemy/zyuan2/code/efficientllm/pretrain/Pai-Megatron-Patch
bash scripts/generate_efficientllm_configs.sh
```

### 2. 快速测试（验证所有变体是否工作）
```bash
bash scripts/test_efficientllm_variants.sh
```

### 3. 运行完整基准测试
```bash
# 设置数据集路径
export DATASET_PATH=/path/to/your/dataset
export VALID_DATASET_PATH=/path/to/your/valid_dataset

# 运行所有基准测试
bash scripts/run_efficientllm_benchmark.sh

# 或者运行特定类型
bash scripts/run_efficientllm_benchmark.sh attention    # 注意力机制
bash scripts/run_efficientllm_benchmark.sh positional  # 位置编码
bash scripts/run_efficientllm_benchmark.sh moe         # MoE变体
```

## 📁 目录结构

```
examples/efficientllm_benchmark/
├── attention_variants/          # 注意力机制变体
│   ├── run_mqa_0.5B.sh         # MQA 0.5B
│   ├── run_mqa_1.5B.sh         # MQA 1.5B
│   ├── run_mqa_3B.sh           # MQA 3B
│   ├── run_gqa_*.sh            # GQA变体
│   ├── run_mla_*.sh            # MLA变体
│   └── run_nsa_*.sh            # NSA变体
├── positional_encoding_variants/ # 位置编码变体
│   ├── run_gqa_rope_1.5B.sh    # RoPE
│   ├── run_gqa_absolute_1.5B.sh # 绝对位置编码
│   └── ...                     # 其他编码方式
└── moe_variants/               # MoE变体
    ├── run_dense_1.5B.sh       # 密集模型
    ├── run_dense_3B.sh         # 密集模型
    ├── run_moe_0_5Bx8.sh       # MoE 0.5B×8
    └── run_moe_1_5Bx8.sh       # MoE 1.5B×8

results/efficientllm_benchmark/  # 结果输出
├── attention_results/           # 注意力机制结果
├── positional_encoding_results/ # 位置编码结果
├── moe_results/                # MoE结果
├── attention_mechanisms_table.txt    # 注意力机制汇总表
├── positional_encoding_table.txt     # 位置编码汇总表
└── moe_table.txt                     # MoE汇总表
```

## 🔧 核心实现文件

### 注意力机制实现
- `megatron_patch/model/qwen2/transformer/mqa_attention.py` - MQA实现
- `megatron_patch/model/qwen2/transformer/mla_attention.py` - MLA实现
- `megatron_patch/model/qwen2/transformer/nsa_attention.py` - NSA实现

### 位置编码实现
- `megatron_patch/model/qwen2/positional_encodings.py` - 各种位置编码

### EfficientLLM指标
- `megatron_patch/efficientllm_metrics.py` - 效率指标收集
- 自动收集AMU、PCU、AL、TT、ST、AEC等指标

## 📊 生成的指标

每个基准测试会自动收集以下EfficientLLM指标：

1. **AMU (Average Memory Utilization)** - 平均内存利用率 (GB)
2. **PCU (Peak Compute Utilization)** - 峰值计算利用率 (比率)
3. **AL (Average Latency)** - 平均延迟 (秒/迭代)
4. **TT (Token Throughput)** - 令牌吞吐量 (令牌/参数/秒)
5. **ST (Sample Throughput)** - 样本吞吐量 (样本/参数/秒)
6. **AEC (Average Energy Consumption)** - 平均能耗 (瓦特)
7. **PPL (Perplexity)** - 困惑度
8. **GPU Hours** - GPU训练时间

## 🎯 模型配置

### 注意力机制基准测试
| 方法 | 参数量 | 微批量大小 | 描述 |
|------|--------|------------|------|
| MQA  | 0.5B/1.5B/3B | 4/2/1 | 单一K/V头 |
| GQA  | 0.5B/1.5B/3B | 4/2/1 | 分组查询（默认） |
| MLA  | 0.5B/1.5B/3B | 4/2/1 | 潜在注意力 |
| NSA  | 0.5B/1.5B/3B | 4/2/1 | 稀疏注意力 |

### 位置编码基准测试
所有位置编码变体使用1.5B GQA模型，上下文长度8K。

### MoE基准测试
| 方法 | 配置 | Top-K | 描述 |
|------|------|-------|------|
| Dense | 1.5B/3B | - | 密集基线 |
| MoE | 0.5B×8/1.5B×8 | 2 | 8个专家 |

## ⚙️ 自定义配置

### 修改训练参数
编辑生成的脚本文件，调整：
- `TRAIN_TOKENS` - 训练令牌数
- `BATCH_SIZE` - 批量大小
- `SEQ_LEN` - 序列长度
- `LR` - 学习率

### 自定义注意力参数
对于NSA：
```bash
--nsa-sliding-window-size 128
--nsa-compress-block-size 64
--nsa-num-selected-blocks 4
```

对于MLA：
```bash
--mla-latent-dim 192  # hidden_size/8
--mla-qk-head-dim 128
```

## 📈 结果分析

运行完成后，检查：

1. **控制台日志** - 实时EfficientLLM指标
2. **TensorBoard** - 可视化指标曲线
3. **汇总表格** - 所有变体的对比结果

```bash
# 查看TensorBoard
tensorboard --logdir results/efficientllm_benchmark/*/tensorboard/

# 查看汇总表格
cat results/efficientllm_benchmark/attention_mechanisms_table.txt
```

## 🐛 故障排除

### 常见问题

1. **内存不足**
   - 减小`BATCH_SIZE`
   - 启用激活检查点：`AC=full`

2. **GPU利用率低**
   - 检查数据加载是否为瓶颈
   - 调整`--num-workers`

3. **指标收集失败**
   - 确保nvidia-smi可用
   - 检查`EFFICIENTLLM_METRICS_ENABLED=true`

### 调试模式
```bash
# 启用详细日志
export EFFICIENTLLM_LOG_INTERVAL=1
export EFFICIENTLLM_COLLECTION_INTERVAL=0.5

# 运行单个变体进行调试
cd examples/efficientllm_benchmark/attention_variants
./run_mqa_0.5B.sh dsw
```

## 📚 参考

- [EfficientLLM论文](链接)
- [Qwen2.5模型](https://github.com/QwenLM/Qwen2.5)
- [Pai-Megatron-Patch](https://github.com/alibaba/Pai-Megatron-Patch)

## 🤝 贡献

如需添加新的注意力机制或位置编码方法：

1. 在相应目录下实现新的类
2. 更新配置生成脚本
3. 添加对应的基准测试配置
4. 更新文档

## 📄 许可证

本项目遵循Apache 2.0许可证。