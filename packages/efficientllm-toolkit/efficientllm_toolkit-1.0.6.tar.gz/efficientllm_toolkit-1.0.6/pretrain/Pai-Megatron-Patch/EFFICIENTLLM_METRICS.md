# EfficientLLM Metrics Integration

This document describes the EfficientLLM metrics implementation integrated into the Pai-Megatron-Patch codebase for evaluating efficiency during training and inference.

## Overview

The EfficientLLM metrics system implements comprehensive efficiency evaluation metrics as described in the EfficientLLM paper:

1. **Average Memory Utilization (AMU)** - Memory usage over time
2. **Peak Compute Utilization (PCU)** - GPU utilization efficiency  
3. **Average Latency (AL)** - Training iteration latency
4. **Token Throughput (TT)** - Tokens processed per second per parameter (pretraining)
5. **Sample Throughput (ST)** - Samples processed per second per parameter (fine-tuning)
6. **Inference Throughput (IT)** - Tokens generated per second (inference)
7. **Average Energy Consumption (AEC)** - Power consumption during training

## Usage

### Basic Usage

The metrics are automatically integrated into the training pipeline. Simply run your existing training scripts:

```bash
cd examples/qwen2_5
./run_mcore_qwen.sh dsw 7B 4 32 5e-5 5e-6 2048 2048 bf16 1 1 1 false false false false full false 500 /path/to/dataset /path/to/valid none 1000000 50000 /path/to/output
```

### Configuration

Configure metrics collection using environment variables:

```bash
# Enable/disable metrics collection (default: true)
export EFFICIENTLLM_METRICS_ENABLED=true

# Collection interval in seconds (default: 1.0)  
export EFFICIENTLLM_COLLECTION_INTERVAL=1.0

# History buffer size (default: 1000)
export EFFICIENTLLM_HISTORY_SIZE=1000

# Logging interval in iterations (default: 10)
export EFFICIENTLLM_LOG_INTERVAL=10
```

Or modify `megatron_patch/efficientllm_config.sh` to set defaults.

### Output

#### Console Output
During training, you'll see EfficientLLM metrics logged to console:
```
[EfficientLLM Metrics] Iteration 100:
  Loss: 3.245678
  AMU (GB): 45.23
  PCU (Ratio): 0.987
  AL (Seconds): 0.1234
  TT (Tokens/Param/Sec): 1.23e-06
  ST (Samples/Param/Sec): 4.56e-09
  AEC (Watts): 342.5
```

#### TensorBoard Output
Metrics are also logged to TensorBoard under the `efficientllm/` namespace:
- `efficientllm/amu_gb` - Average Memory Utilization
- `efficientllm/pcu_ratio` - Peak Compute Utilization  
- `efficientllm/al_seconds` - Average Latency
- `efficientllm/tt_tokens_per_param_per_sec` - Token Throughput
- `efficientllm/st_samples_per_param_per_sec` - Sample Throughput
- `efficientllm/aec_watts` - Average Energy Consumption

## Implementation Details

### Core Components

1. **MetricsCollector Class** (`efficientllm_metrics.py`)
   - Background thread for continuous monitoring
   - GPU utilization tracking via nvidia-smi
   - Memory usage monitoring via PyTorch CUDA APIs
   - Power consumption tracking via nvidia-smi

2. **Integration Points** (`training.py`)
   - Model parameter counting and initialization
   - Iteration timing and token/sample counting
   - Tensorboard and console logging

### Metrics Definitions

#### Average Memory Utilization (AMU)
```
AMU = (1/T) * ∫₀ᵀ Memory_Used(t) dt
```
Measures average GPU memory usage over training time.

#### Peak Compute Utilization (PCU)  
```
PCU = (1/T) * ∫₀ᵀ (Actual_GPU_Utilization(t) / Peak_GPU_Utilization) dt
```
Measures average GPU compute utilization as ratio of theoretical peak.

#### Average Latency (AL)
```
AL = Σᵢ(Computation_Time_i + Communication_Time_i) / N
```
Measures average time per training iteration.

#### Token Throughput (TT)
```
TT = Σᵢ(Tokens_Processed_i / Model_Parameters) / Σᵢ Time_i
```
Normalized throughput for pretraining scenarios.

#### Sample Throughput (ST)
```
ST = Σᵢ(Samples_Processed_i / Model_Parameters) / Σᵢ Time_i  
```
Normalized throughput for fine-tuning scenarios.

#### Inference Throughput (IT)
```
IT = Σᵢ Tokens_Generated_i / Σᵢ Time_i
```
Token generation speed for inference.

#### Average Energy Consumption (AEC)
```
AEC = (1/T) * ∫₀ᵀ P(t) dt
```
Average power consumption over training time.

## Requirements

- NVIDIA GPU with nvidia-smi support
- PyTorch with CUDA support
- psutil library for system monitoring

## Troubleshooting

### No GPU Metrics
If GPU metrics show 0, ensure:
- NVIDIA drivers are installed
- nvidia-smi command is available
- GPU is not in exclusive compute mode

### High Memory Usage
The metrics collector maintains a history buffer. Reduce `EFFICIENTLLM_HISTORY_SIZE` if memory usage is a concern.

### Performance Impact
Background monitoring has minimal overhead (~0.1% CPU). Adjust `EFFICIENTLLM_COLLECTION_INTERVAL` to reduce frequency if needed.

## Integration in Other Models

To integrate EfficientLLM metrics in other model training scripts:

1. Import the metrics module:
   ```python
   from megatron_patch.efficientllm_metrics import (
       initialize_efficientllm_metrics,
       finalize_efficientllm_metrics, 
       get_metrics_collector
   )
   ```

2. Initialize after model creation:
   ```python
   initialize_efficientllm_metrics(total_model_parameters)
   ```

3. Add timing to training loop:
   ```python
   metrics_collector = get_metrics_collector()
   
   # Before each iteration
   metrics_collector.record_iteration_start()
   
   # Training step here...
   
   # After each iteration  
   metrics_collector.record_iteration_end(tokens_processed, samples_processed)
   
   # Log metrics periodically
   if should_log_metrics(iteration):
       metrics_collector.log_metrics(iteration, loss, tensorboard_writer)
   ```

4. Finalize at end of training:
   ```python
   finalize_efficientllm_metrics()
   ```