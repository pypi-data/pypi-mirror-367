# EfficientLLM Inference Benchmark Evaluation

这个项目实现了论文中提到的推理量化基准测试系统，包括性能评估和效率指标监控。

## 主要组件

### 1. 批量评测脚本 (`batch_eval.py`)
- 支持多个模型和精度配置的批量评测
- 基于 lm-evaluation-harness 的 leaderboard 任务
- 支持 bfloat16, float16, int4 等精度
- 可并行执行和断点续传

### 2. 结果处理脚本 (`process_results.py`)
- 收集和处理评测结果
- 生成 LaTeX 格式的论文表格
- 输出 CSV 格式便于查看

### 3. 性能监控器 (`lm_eval/performance/monitor.py`)
- 实现 EfficientLLM 论文中的所有效率指标：
  - **AMU**: Average Memory Utilization
  - **PCU**: Peak Compute Utilization  
  - **AL**: Average Latency
  - **TT/ST/IT**: Token/Sample/Inference Throughput
  - **AEC**: Average Energy Consumption
  - **MCR**: Model Compression Rate

## 使用方法

### 1. 环境准备

```bash
# 安装依赖
pip install -e .
pip install pynvml psutil pandas

# 确保模型路径正确
mkdir -p model/
# 将你的模型放在 model/ 目录下
```

### 2. 运行完整评测

```bash
# 运行所有模型和精度的评测
python batch_eval.py --output_dir ./results --max_workers 1

# 运行特定模型和任务
python batch_eval.py \
    --models DeepSeek-R1-Distill-Qwen-1.5B Qwen2.5-7B \
    --precisions bfloat16 float16 int4 \
    --tasks MMLU-Pro BBH GPQA \
    --output_dir ./results
```

### 3. 处理结果并生成表格

```bash
# 生成论文格式的表格
python process_results.py \
    --results_dir ./results \
    --output_dir ./tables
```

这将生成：
- `benchmark_table.tex`: LaTeX 表格（论文格式）
- `benchmark_results.csv`: CSV 结果表格
- `benchmark_report.txt`: 评测总结报告

### 4. 性能监控使用

```python
from lm_eval.performance.monitor import PerformanceMonitorContext

# 在推理评测中使用
with PerformanceMonitorContext("inference", save_path="perf_metrics.json") as monitor:
    # 你的推理代码
    for request in eval_requests:
        start_time = time.time()
        output = model.generate(request)
        computation_time = time.time() - start_time
        
        monitor.record_request(
            generated_tokens=len(output),
            computation_time=computation_time
        )

# 在训练中使用
with PerformanceMonitorContext("pretraining", model_parameters=1500000000) as monitor:
    for batch in training_data:
        # 训练代码
        monitor.record_request(
            tokens=batch_tokens,
            computation_time=iter_time
        )
```

## 模型配置

目前支持的模型配置：

```python
MODEL_CONFIGS = {
    "DeepSeek-R1-Distill-Qwen-1.5B": {
        "model_path": "./model/DeepSeek-R1-Distill-Qwen-1.5B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"}, 
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    # ... 其他模型
}
```

## 任务配置

支持的评测任务：

- **MMLU-Pro**: `leaderboard_mmlu_pro`
- **BBH**: `leaderboard_bbh`
- **GPQA**: `leaderboard_gpqa`
- **IFEval**: `leaderboard_ifeval`
- **MATH**: `leaderboard_math_hard`
- **MUSR**: `leaderboard_musr`

## 效率指标说明

### 计算系统利用率指标

1. **AMU (Average Memory Utilization)**
   ```
   AMU = (1/T) * ∫[0,T] Memory_Used(t) dt
   ```

2. **PCU (Peak Compute Utilization)**
   ```
   PCU = (1/T) * ∫[0,T] (Actual_GPU_Util(t) / Peak_GPU_Util) dt
   ```

3. **AL (Average Latency)**
   ```
   AL = Σ[i=1,N] (Computation_Time_i + Communication_Time_i) / N
   ```

### 吞吐量指标

4. **TT (Token Throughput)** - 用于预训练
   ```
   TT = Σ[i=1,N](Tokens_i / Model_Params) / Σ[i=1,N]Time_i
   ```

5. **ST (Sample Throughput)** - 用于微调
   ```
   ST = Σ[i=1,N](Samples_i / Model_Params) / Σ[i=1,N]Time_i
   ```

6. **IT (Inference Throughput)** - 用于推理
   ```
   IT = Σ[i=1,N]Generated_Tokens_i / Σ[i=1,N]Time_i
   ```

### 能耗和压缩指标

7. **AEC (Average Energy Consumption)**
   ```
   AEC = (1/T) * ∫[0,T] P(t) dt
   ```

8. **MCR (Model Compression Rate)**
   ```
   MCR = (Size_original / Size_compressed) * (Perf_compressed / Perf_original)
   ```

## 示例输出

运行评测后会生成类似论文表格的结果：

```
Model                        | Precision | MMLU-Pro | BBH    | GPQA   | IFEval | MATH   | MUSR
DeepSeek-R1-Distill-Qwen-1.5B | bfloat16 | 0.1656   | 0.3471 | 0.269  | 0.1955 | 0.1192 | 0.3553
                             | float16  | 0.1668   | 0.3505 | 0.2754 | 0.1995 | 0.1213 | 0.3567
                             | int4     | 0.1496   | 0.3337 | 0.2529 | 0.1937 | 0.1043 | 0.3702
```

## 注意事项

1. 确保有足够的 GPU 内存运行大模型
2. int4 量化需要对应的量化模型或量化库支持
3. 能耗监控需要 NVIDIA GPU 和 pynvml 库
4. 建议在评测前先运行示例验证环境配置

## 故障排除

- 如果 GPU 监控失败，检查 pynvml 安装和 GPU 驱动
- 如果模型加载失败，检查模型路径和格式
- 如果评测超时，可以调整 `--max_workers` 或增加超时时间