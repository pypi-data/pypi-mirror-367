#!/usr/bin/env python3
"""
Test script for the updated performance monitor
"""

import sys
import os
import time
import random

# Add the path to import the monitor
sys.path.append('/work/nvme/bemy/zyuan2/code/efficientllm/quantization/lm-evaluation-harness-main')

from lm_eval.performance.monitor import PerformanceMonitorContext, performance_monitor

def test_performance_monitor():
    """Test the performance monitor with different scenarios"""
    
    print("Testing EfficientLLM Performance Monitor")
    print("=" * 50)
    
    # Test 1: Inference scenario
    print("\n1. Testing Inference Scenario:")
    with PerformanceMonitorContext("inference", save_path="test_inference_metrics.json") as monitor:
        # Simulate some inference requests
        for i in range(10):
            # Simulate varying inference times and token generation
            computation_time = random.uniform(0.1, 0.5)
            communication_time = random.uniform(0.01, 0.05)
            generated_tokens = random.randint(50, 200)
            
            time.sleep(computation_time)  # Simulate actual work
            
            monitor.record_request(
                generated_tokens=generated_tokens,
                computation_time=computation_time,
                communication_time=communication_time
            )
    
    # Test 2: Pretraining scenario
    print("\n2. Testing Pretraining Scenario:")
    model_params = 1500000000  # 1.5B parameters
    with PerformanceMonitorContext("pretraining", model_parameters=model_params, 
                                  save_path="test_pretraining_metrics.json") as monitor:
        # Simulate training iterations
        for i in range(5):
            computation_time = random.uniform(0.5, 1.0)
            communication_time = random.uniform(0.1, 0.2)
            tokens_processed = random.randint(1000, 2000)
            
            time.sleep(computation_time * 0.1)  # Simulate work (scaled down for testing)
            
            monitor.record_request(
                tokens=tokens_processed,
                computation_time=computation_time,
                communication_time=communication_time
            )
    
    # Test 3: Fine-tuning scenario
    print("\n3. Testing Fine-tuning Scenario:")
    with PerformanceMonitorContext("finetuning", model_parameters=model_params,
                                  save_path="test_finetuning_metrics.json") as monitor:
        # Simulate fine-tuning iterations
        for i in range(8):
            computation_time = random.uniform(0.2, 0.8)
            communication_time = random.uniform(0.05, 0.15)
            samples_processed = random.randint(16, 64)  # batch size
            
            time.sleep(computation_time * 0.1)  # Simulate work
            
            monitor.record_request(
                samples=samples_processed,
                computation_time=computation_time,
                communication_time=communication_time
            )
    
    # Test 4: Model compression scenario
    print("\n4. Testing Model Compression Rate:")
    monitor_comp = performance_monitor.__class__()
    
    # Set compression information
    original_size = 3000000000  # 3GB
    compressed_size = 750000000  # 750MB (4x compression)
    original_perf = 0.85        # 85% accuracy
    compressed_perf = 0.82      # 82% accuracy (slight degradation)
    
    monitor_comp.set_compression_info(
        original_size, compressed_size, 
        original_perf, compressed_perf
    )
    
    # Simulate a short evaluation
    monitor_comp.start_monitoring()
    time.sleep(0.5)
    monitor_comp.record_request(generated_tokens=100, computation_time=0.3)
    monitor_comp.stop_monitoring()
    
    metrics = monitor_comp.get_metrics()
    print(f"Model Compression Rate (MCR): {metrics.get('MCR', 'N/A'):.4f}")
    
    print("\n" + "=" * 50)
    print("All tests completed! Check the generated JSON files for detailed metrics.")

if __name__ == "__main__":
    test_performance_monitor()