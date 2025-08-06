import os
import json
import psutil
import time
from datetime import datetime
import torch
import numpy as np
from typing import Dict, List, Optional, Union
import threading
import logging

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Performance monitor implementing EfficientLLM assessment metrics:
    - Average Memory Utilization (AMU)
    - Peak Compute Utilization (PCU)  
    - Average Latency (AL)
    - Token Throughput (TT), Sample Throughput (ST), Inference Throughput (IT)
    - Average Energy Consumption (AEC)
    - Model Compression Rate (MCR)
    """
    
    def __init__(self, device_id: int = 0):
        """Initialize performance monitor"""
        self.device_id = device_id
        self.reset()
        self.process = psutil.Process()
        
        # Initialize GPU monitoring
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available and NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                self.total_gpu_memory = pynvml.nvmlDeviceGetMemoryInfo(self.handle).total
                self.nvml_initialized = True
                logger.info(f"NVML initialized for GPU {device_id}")
            except Exception as e:
                self.nvml_initialized = False
                logger.warning(f"Failed to initialize NVML: {e}")
        else:
            self.nvml_initialized = False
            
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 0.1  # 100ms sampling
            
    def reset(self):
        """Reset all metrics"""
        self.metrics = {
            # Raw measurements
            "memory_utilization": [],  # For AMU calculation
            "compute_utilization": [], # For PCU calculation
            "power_consumption": [],   # For AEC calculation (Watts)
            "timestamps": [],
            
            # Request-level metrics
            "request_latencies": [],   # For AL calculation (seconds)
            "request_tokens": [],      # Token counts per request
            "request_samples": [],     # Sample counts per request (for fine-tuning)
            "generated_tokens": [],    # Generated tokens per request (for inference)
            "computation_times": [],   # Pure computation time per request
            "communication_times": [], # Communication overhead per request
        }
        
        # Session metadata
        self.start_time = None
        self.end_time = None
        self.scenario = None  # 'pretraining', 'finetuning', 'inference'
        self.model_parameters = None
        self.original_model_size = None
        self.compressed_model_size = None
        self.original_performance = None
        self.compressed_performance = None
        
    def set_scenario(self, scenario: str, model_parameters: Optional[int] = None):
        """Set evaluation scenario and model info"""
        self.scenario = scenario.lower()
        self.model_parameters = model_parameters
        
    def set_compression_info(self, original_size: int, compressed_size: int, 
                           original_perf: float, compressed_perf: float):
        """Set model compression information for MCR calculation"""
        self.original_model_size = original_size
        self.compressed_model_size = compressed_size
        self.original_performance = original_perf
        self.compressed_performance = compressed_perf
        
    def start_monitoring(self):
        """Start performance monitoring with background thread"""
        self.start_time = time.time()
        self.monitoring_active = True
        
        # Start background monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            self._sample_system_metrics()
            time.sleep(self.monitoring_interval)
            
    def _sample_system_metrics(self):
        """Sample system-level metrics (memory, compute, power)"""
        timestamp = time.time()
        self.metrics["timestamps"].append(timestamp)
        
        # Memory utilization
        if self.gpu_available and self.nvml_initialized:
            try:
                # GPU memory utilization
                gpu_memory = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
                gpu_memory_used = gpu_memory.used / self.total_gpu_memory
                self.metrics["memory_utilization"].append(float(gpu_memory_used))
                
                # GPU compute utilization 
                gpu_util = pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu / 100.0
                self.metrics["compute_utilization"].append(float(gpu_util))
                
                # GPU power consumption
                power_usage = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # Convert to Watts
                self.metrics["power_consumption"].append(float(power_usage))
                
            except Exception as e:
                logger.warning(f"GPU monitoring error: {e}")
                self.metrics["memory_utilization"].append(0.0)
                self.metrics["compute_utilization"].append(0.0)
                self.metrics["power_consumption"].append(0.0)
        else:
            # Fallback to CPU metrics
            memory_info = self.process.memory_info()
            cpu_memory_used = memory_info.rss / psutil.virtual_memory().total
            cpu_util = psutil.cpu_percent() / 100.0
            
            self.metrics["memory_utilization"].append(float(cpu_memory_used))
            self.metrics["compute_utilization"].append(float(cpu_util))
            self.metrics["power_consumption"].append(0.0)  # CPU power not easily measurable
            
    def record_request(self, tokens: int = 0, samples: int = 0, generated_tokens: int = 0,
                      computation_time: float = 0.0, communication_time: float = 0.0):
        """Record metrics for a single request/iteration"""
        total_latency = computation_time + communication_time
        
        self.metrics["request_latencies"].append(total_latency)
        self.metrics["request_tokens"].append(tokens)
        self.metrics["request_samples"].append(samples)
        self.metrics["generated_tokens"].append(generated_tokens)
        self.metrics["computation_times"].append(computation_time)
        self.metrics["communication_times"].append(communication_time)
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        self.end_time = time.time()
        logger.info("Performance monitoring stopped")
        
    def get_metrics(self) -> Dict[str, float]:
        """Calculate and return EfficientLLM assessment metrics"""
        if not self.start_time or not self.end_time:
            return {}
            
        total_time = self.end_time - self.start_time
        metrics = {}
        
        # 1. Average Memory Utilization (AMU)
        # AMU = (1/T) * ∫[0,T] Memory_Used(t) dt
        if self.metrics["memory_utilization"]:
            metrics["AMU"] = float(np.mean(self.metrics["memory_utilization"]))
        else:
            metrics["AMU"] = 0.0
            
        # 2. Peak Compute Utilization (PCU) 
        # PCU = (1/T) * ∫[0,T] (Actual_GPU_Util(t) / Peak_GPU_Util) dt
        if self.metrics["compute_utilization"]:
            # Use mean instead of peak as per the formula in the paper
            metrics["PCU"] = float(np.mean(self.metrics["compute_utilization"]))
        else:
            metrics["PCU"] = 0.0
            
        # 3. Average Latency (AL)
        # AL = Σ[i=1,N] (Computation_Time_i + Communication_Time_i) / N
        if self.metrics["request_latencies"]:
            metrics["AL"] = float(np.mean(self.metrics["request_latencies"]))
        else:
            metrics["AL"] = 0.0
            
        # 4. Throughput metrics (TT, ST, IT) - depends on scenario
        if self.scenario == "pretraining" and self.model_parameters:
            # Token Throughput (TT) = Σ[i=1,N](Tokens_i / Model_Params) / Σ[i=1,N]Time_i
            if self.metrics["request_tokens"] and self.metrics["request_latencies"]:
                total_normalized_tokens = sum(tokens / self.model_parameters 
                                           for tokens in self.metrics["request_tokens"])
                total_time_requests = sum(self.metrics["request_latencies"])
                if total_time_requests > 0:
                    metrics["TT"] = float(total_normalized_tokens / total_time_requests)
                else:
                    metrics["TT"] = 0.0
            else:
                metrics["TT"] = 0.0
                
        elif self.scenario == "finetuning" and self.model_parameters:
            # Sample Throughput (ST) = Σ[i=1,N](Samples_i / Model_Params) / Σ[i=1,N]Time_i
            if self.metrics["request_samples"] and self.metrics["request_latencies"]:
                total_normalized_samples = sum(samples / self.model_parameters 
                                            for samples in self.metrics["request_samples"])
                total_time_requests = sum(self.metrics["request_latencies"])
                if total_time_requests > 0:
                    metrics["ST"] = float(total_normalized_samples / total_time_requests)
                else:
                    metrics["ST"] = 0.0
            else:
                metrics["ST"] = 0.0
                
        elif self.scenario == "inference":
            # Inference Throughput (IT) = Σ[i=1,N]Generated_Tokens_i / Σ[i=1,N]Time_i
            if self.metrics["generated_tokens"] and self.metrics["request_latencies"]:
                total_generated = sum(self.metrics["generated_tokens"])
                total_time_requests = sum(self.metrics["request_latencies"])
                if total_time_requests > 0:
                    metrics["IT"] = float(total_generated / total_time_requests)
                else:
                    metrics["IT"] = 0.0
            else:
                metrics["IT"] = 0.0
        
        # 5. Average Energy Consumption (AEC)
        # AEC = (1/T) * ∫[0,T] P(t) dt
        if self.metrics["power_consumption"]:
            metrics["AEC"] = float(np.mean(self.metrics["power_consumption"]))
        else:
            metrics["AEC"] = 0.0
            
        # 6. Model Compression Rate (MCR)
        # MCR = (Size_original / Size_compressed) * (Perf_compressed / Perf_original)
        if all(x is not None for x in [self.original_model_size, self.compressed_model_size,
                                      self.original_performance, self.compressed_performance]):
            if self.compressed_model_size > 0 and self.original_performance > 0:
                compression_ratio = self.original_model_size / self.compressed_model_size
                performance_ratio = self.compressed_performance / self.original_performance
                metrics["MCR"] = float(compression_ratio * performance_ratio)
            else:
                metrics["MCR"] = 0.0
        else:
            metrics["MCR"] = None  # Not applicable if compression info not provided
            
        # Additional derived metrics
        metrics["total_time"] = float(total_time)
        metrics["num_requests"] = len(self.metrics["request_latencies"])
        
        return metrics
    
    def get_detailed_metrics(self) -> Dict[str, Union[float, List[float]]]:
        """Get detailed metrics including time series data"""
        basic_metrics = self.get_metrics()
        
        detailed = {
            **basic_metrics,
            "time_series": {
                "timestamps": self.metrics["timestamps"],
                "memory_utilization": self.metrics["memory_utilization"],
                "compute_utilization": self.metrics["compute_utilization"],
                "power_consumption": self.metrics["power_consumption"],
            },
            "request_level": {
                "latencies": self.metrics["request_latencies"],
                "tokens": self.metrics["request_tokens"],
                "samples": self.metrics["request_samples"],
                "generated_tokens": self.metrics["generated_tokens"],
                "computation_times": self.metrics["computation_times"],
                "communication_times": self.metrics["communication_times"],
            }
        }
        
        return detailed
    
    def save_metrics(self, filepath: str):
        """Save metrics to JSON file"""
        metrics = self.get_detailed_metrics()
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to {filepath}")
    
    def print_summary(self):
        """Print a summary of the metrics"""
        metrics = self.get_metrics()
        
        print("\n" + "="*50)
        print("EFFICIENTLLM PERFORMANCE METRICS SUMMARY")
        print("="*50)
        
        if metrics.get("AMU") is not None:
            print(f"Average Memory Utilization (AMU): {metrics['AMU']:.4f}")
        if metrics.get("PCU") is not None:
            print(f"Peak Compute Utilization (PCU): {metrics['PCU']:.4f}")
        if metrics.get("AL") is not None:
            print(f"Average Latency (AL): {metrics['AL']:.4f} seconds")
        if metrics.get("AEC") is not None:
            print(f"Average Energy Consumption (AEC): {metrics['AEC']:.2f} Watts")
            
        # Scenario-specific throughput
        if self.scenario == "pretraining" and metrics.get("TT") is not None:
            print(f"Token Throughput (TT): {metrics['TT']:.6f} tokens/s/param")
        elif self.scenario == "finetuning" and metrics.get("ST") is not None:
            print(f"Sample Throughput (ST): {metrics['ST']:.6f} samples/s/param")
        elif self.scenario == "inference" and metrics.get("IT") is not None:
            print(f"Inference Throughput (IT): {metrics['IT']:.2f} tokens/s")
            
        if metrics.get("MCR") is not None:
            print(f"Model Compression Rate (MCR): {metrics['MCR']:.4f}")
            
        print(f"Total evaluation time: {metrics.get('total_time', 0):.2f} seconds")
        print(f"Number of requests: {metrics.get('num_requests', 0)}")
        print("="*50)
        
    def __del__(self):
        """Cleanup NVML and stop monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'nvml_initialized') and self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Utility functions for easy integration
def start_monitoring(scenario: str = "inference", model_parameters: Optional[int] = None):
    """Start performance monitoring"""
    performance_monitor.set_scenario(scenario, model_parameters)
    performance_monitor.start_monitoring()

def record_request(**kwargs):
    """Record a request with performance metrics"""
    performance_monitor.record_request(**kwargs)

def stop_monitoring_and_report(save_path: Optional[str] = None) -> Dict[str, float]:
    """Stop monitoring and return/save metrics"""
    performance_monitor.stop_monitoring()
    metrics = performance_monitor.get_metrics()
    
    if save_path:
        performance_monitor.save_metrics(save_path)
    
    return metrics

def get_current_metrics() -> Dict[str, float]:
    """Get current metrics without stopping monitoring"""
    return performance_monitor.get_metrics()

# Context manager for easy usage
class PerformanceMonitorContext:
    """Context manager for performance monitoring"""
    
    def __init__(self, scenario: str = "inference", model_parameters: Optional[int] = None,
                 save_path: Optional[str] = None, print_summary: bool = True):
        self.scenario = scenario
        self.model_parameters = model_parameters
        self.save_path = save_path
        self.print_summary = print_summary
        
    def __enter__(self):
        start_monitoring(self.scenario, self.model_parameters)
        return performance_monitor
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        metrics = stop_monitoring_and_report(self.save_path)
        if self.print_summary:
            performance_monitor.print_summary()
        return metrics

# Example usage:
# with PerformanceMonitorContext("inference", save_path="metrics.json") as monitor:
#     # Your evaluation code here
#     monitor.record_request(generated_tokens=100, computation_time=0.5)
#     pass 