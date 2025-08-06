# Copyright 2025 EfficientLLM Team and LlamaFactory team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
EfficientLLM Metrics Module for LLaMA-Factory

This module implements comprehensive efficiency metrics for evaluating large language models
during fine-tuning, including:
- Average Memory Utilization (AMU)
- Peak Compute Utilization (PCU)
- Average Latency (AL)
- Token Throughput (TT)
- Sample Throughput (ST) 
- Inference Throughput (IT)
- Average Energy Consumption (AEC)
"""

import os
import time
import threading
import psutil
import torch
import subprocess
from typing import Dict, List, Optional, Any, Union
from collections import deque
from dataclasses import dataclass

from ..extras.logging import get_logger


logger = get_logger(__name__)


@dataclass
class EfficientLLMMetrics:
    """Container for all EfficientLLM metrics"""
    amu: float = 0.0  # Average Memory Utilization
    pcu: float = 0.0  # Peak Compute Utilization
    al: float = 0.0   # Average Latency
    tt: float = 0.0   # Token Throughput
    st: float = 0.0   # Sample Throughput
    it: float = 0.0   # Inference Throughput
    aec: float = 0.0  # Average Energy Consumption


class EfficientLLMCollector:
    """
    EfficientLLM metrics collector for LLaMA-Factory fine-tuning
    """
    
    def __init__(self, collection_interval: float = 1.0, history_size: int = 1000):
        """
        Initialize the metrics collector
        
        Args:
            collection_interval: Interval in seconds for background metric collection
            history_size: Maximum number of historical data points to keep
        """
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # Data storage
        self.memory_history = deque(maxlen=history_size)
        self.gpu_utilization_history = deque(maxlen=history_size)
        self.latency_history = deque(maxlen=history_size)
        self.power_history = deque(maxlen=history_size)
        self.time_history = deque(maxlen=history_size)
        
        # Training state tracking
        self.training_start_time = None
        self.step_start_time = None
        self.total_tokens_processed = 0
        self.total_samples_processed = 0
        self.total_steps = 0
        self.model_parameters = 0
        
        # Background collection thread
        self._collecting = False
        self._collection_thread = None
        
        # NVIDIA GPU support
        self.has_nvidia_gpu = self._check_nvidia_gpu()
        
        # Fine-tuning specific tracking
        self.sequence_length = 0
        self.batch_size = 0
        
    def _check_nvidia_gpu(self) -> bool:
        """Check if NVIDIA GPU is available"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _get_gpu_utilization(self) -> float:
        """Get current GPU utilization percentage"""
        if not self.has_nvidia_gpu:
            return 0.0
            
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Handle multiple GPUs - return average
                utilizations = [float(x.strip()) for x in result.stdout.strip().split('\n') if x.strip()]
                return sum(utilizations) / len(utilizations) if utilizations else 0.0
        except (subprocess.SubprocessError, ValueError):
            pass
        return 0.0
    
    def _get_memory_utilization(self) -> float:
        """Get current memory utilization in GB"""
        if torch.cuda.is_available():
            # GPU memory
            total_memory = torch.cuda.get_device_properties(0).total_memory
            used_memory = torch.cuda.memory_allocated(0)
            return used_memory / (1024**3)  # Convert to GB
        else:
            # CPU memory fallback
            memory_info = psutil.virtual_memory()
            return memory_info.used / (1024**3)  # Convert to GB
    
    def _get_power_consumption(self) -> float:
        """Get current power consumption in Watts"""
        if not self.has_nvidia_gpu:
            return 0.0
            
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Handle multiple GPUs - return sum
                powers = [float(x.strip()) for x in result.stdout.strip().split('\n') if x.strip()]
                return sum(powers) if powers else 0.0
        except (subprocess.SubProcessError, ValueError):
            pass
        return 0.0
    
    def _background_collection(self):
        """Background thread for continuous metrics collection"""
        while self._collecting:
            current_time = time.time()
            
            # Collect metrics
            memory_util = self._get_memory_utilization()
            gpu_util = self._get_gpu_utilization()
            power_draw = self._get_power_consumption()
            
            # Store with timestamps
            self.memory_history.append(memory_util)
            self.gpu_utilization_history.append(gpu_util)
            self.power_history.append(power_draw)
            self.time_history.append(current_time)
            
            time.sleep(self.collection_interval)
    
    def start_collection(self):
        """Start background metrics collection"""
        if not self._collecting:
            self._collecting = True
            self.training_start_time = time.time()
            self._collection_thread = threading.Thread(target=self._background_collection, daemon=True)
            self._collection_thread.start()
            logger.info("[EfficientLLM] Metrics collection started")
    
    def stop_collection(self):
        """Stop background metrics collection"""
        self._collecting = False
        if self._collection_thread:
            self._collection_thread.join()
        logger.info("[EfficientLLM] Metrics collection stopped")
    
    def set_model_parameters(self, num_parameters: int):
        """Set the total number of model parameters"""
        self.model_parameters = num_parameters
        logger.info(f"[EfficientLLM] Model parameters set to {num_parameters:,}")
    
    def set_batch_config(self, sequence_length: int, batch_size: int):
        """Set batch configuration for throughput calculations"""
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        logger.info(f"[EfficientLLM] Batch config: seq_len={sequence_length}, batch_size={batch_size}")
    
    def record_step_start(self):
        """Record the start of a training step"""
        self.step_start_time = time.time()
    
    def record_step_end(self, tokens_processed: int = None, samples_processed: int = None):
        """
        Record the end of a training step
        
        Args:
            tokens_processed: Number of tokens processed in this step (calculated if None)
            samples_processed: Number of samples processed in this step (calculated if None)
        """
        if self.step_start_time is not None:
            step_time = time.time() - self.step_start_time
            self.latency_history.append(step_time)
            
            # Calculate tokens and samples if not provided
            if tokens_processed is None:
                tokens_processed = self.sequence_length * self.batch_size
            if samples_processed is None:
                samples_processed = self.batch_size
            
            self.total_tokens_processed += tokens_processed
            self.total_samples_processed += samples_processed
            self.total_steps += 1
            
            self.step_start_time = None
    
    def calculate_amu(self) -> float:
        """Calculate Average Memory Utilization (AMU)"""
        if not self.memory_history:
            return 0.0
        return sum(self.memory_history) / len(self.memory_history)
    
    def calculate_pcu(self) -> float:
        """Calculate Peak Compute Utilization (PCU)"""
        if not self.gpu_utilization_history:
            return 0.0
        # Peak GPU utilization is typically 100%
        peak_utilization = 100.0
        average_utilization = sum(self.gpu_utilization_history) / len(self.gpu_utilization_history)
        return average_utilization / peak_utilization
    
    def calculate_al(self) -> float:
        """Calculate Average Latency (AL)"""
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)
    
    def calculate_tt(self) -> float:
        """Calculate Token Throughput (TT) for pretraining"""
        if self.total_steps == 0 or self.model_parameters == 0:
            return 0.0
        
        total_time = sum(self.latency_history) if self.latency_history else 0.0
        if total_time == 0:
            return 0.0
        
        normalized_tokens = self.total_tokens_processed / self.model_parameters
        return normalized_tokens / total_time
    
    def calculate_st(self) -> float:
        """Calculate Sample Throughput (ST) for fine-tuning"""
        if self.total_steps == 0 or self.model_parameters == 0:
            return 0.0
        
        total_time = sum(self.latency_history) if self.latency_history else 0.0
        if total_time == 0:
            return 0.0
        
        normalized_samples = self.total_samples_processed / self.model_parameters
        return normalized_samples / total_time
    
    def calculate_it(self, tokens_generated: int, total_inference_time: float) -> float:
        """Calculate Inference Throughput (IT)"""
        if total_inference_time == 0:
            return 0.0
        return tokens_generated / total_inference_time
    
    def calculate_aec(self) -> float:
        """Calculate Average Energy Consumption (AEC)"""
        if not self.power_history:
            return 0.0
        return sum(self.power_history) / len(self.power_history)
    
    def get_all_metrics(self) -> EfficientLLMMetrics:
        """Calculate and return all EfficientLLM metrics"""
        return EfficientLLMMetrics(
            amu=self.calculate_amu(),
            pcu=self.calculate_pcu(),
            al=self.calculate_al(),
            tt=self.calculate_tt(),
            st=self.calculate_st(),
            it=0.0,  # IT is calculated separately for inference
            aec=self.calculate_aec()
        )
    
    def log_metrics(self, step: int, loss: float, tb_writer=None) -> Dict[str, float]:
        """
        Log current metrics to console and tensorboard
        
        Args:
            step: Current training step
            loss: Current training loss
            tb_writer: Tensorboard writer (optional)
            
        Returns:
            Dictionary of current metrics
        """
        metrics = self.get_all_metrics()
        
        # Create metrics dictionary
        metrics_dict = {
            'efficientllm/amu_gb': metrics.amu,
            'efficientllm/pcu_ratio': metrics.pcu,
            'efficientllm/al_seconds': metrics.al,
            'efficientllm/tt_tokens_per_param_per_sec': metrics.tt,
            'efficientllm/st_samples_per_param_per_sec': metrics.st,
            'efficientllm/aec_watts': metrics.aec,
        }
        
        # Log to console
        logger.info(f"[EfficientLLM Metrics] Step {step}:")
        logger.info(f"  Loss: {loss:.6f}")
        logger.info(f"  AMU (GB): {metrics.amu:.2f}")
        logger.info(f"  PCU (Ratio): {metrics.pcu:.3f}")
        logger.info(f"  AL (Seconds): {metrics.al:.4f}")
        logger.info(f"  TT (Tokens/Param/Sec): {metrics.tt:.2e}")
        logger.info(f"  ST (Samples/Param/Sec): {metrics.st:.2e}")
        logger.info(f"  AEC (Watts): {metrics.aec:.2f}")
        
        # Log to tensorboard if available
        if tb_writer is not None:
            for key, value in metrics_dict.items():
                tb_writer.add_scalar(key, value, step)
        
        return metrics_dict
    
    def reset(self):
        """Reset all metrics and counters"""
        self.memory_history.clear()
        self.gpu_utilization_history.clear()
        self.latency_history.clear()
        self.power_history.clear()
        self.time_history.clear()
        
        self.training_start_time = None
        self.step_start_time = None
        self.total_tokens_processed = 0
        self.total_samples_processed = 0
        self.total_steps = 0


# Global metrics collector instance
_global_collector = None


def get_efficientllm_collector() -> EfficientLLMCollector:
    """Get the global EfficientLLM collector instance"""
    global _global_collector
    if _global_collector is None:
        _global_collector = EfficientLLMCollector()
    return _global_collector


def initialize_efficientllm_metrics(
    model_parameters: int, 
    sequence_length: int = 0,
    batch_size: int = 0,
    collection_interval: float = None
):
    """
    Initialize EfficientLLM metrics collection for LLaMA-Factory
    
    Args:
        model_parameters: Total number of model parameters
        sequence_length: Sequence length for batch configuration
        batch_size: Batch size for batch configuration
        collection_interval: Collection interval in seconds (uses env var if not specified)
    """
    # Check if metrics are enabled
    metrics_enabled = os.getenv('EFFICIENTLLM_METRICS_ENABLED', 'true').lower() == 'true'
    if not metrics_enabled:
        logger.info("[EfficientLLM] Metrics collection disabled via EFFICIENTLLM_METRICS_ENABLED=false")
        return
    
    # Get configuration from environment variables
    if collection_interval is None:
        collection_interval = float(os.getenv('EFFICIENTLLM_COLLECTION_INTERVAL', '1.0'))
    
    history_size = int(os.getenv('EFFICIENTLLM_HISTORY_SIZE', '1000'))
    
    # Initialize collector with environment configuration
    global _global_collector
    _global_collector = EfficientLLMCollector(
        collection_interval=collection_interval,
        history_size=history_size
    )
    
    collector = get_efficientllm_collector()
    collector.set_model_parameters(model_parameters)
    if sequence_length > 0 and batch_size > 0:
        collector.set_batch_config(sequence_length, batch_size)
    collector.start_collection()
    
    logger.info(f"[EfficientLLM] Metrics collection initialized for model with {model_parameters:,} parameters")
    logger.info(f"[EfficientLLM] Collection interval: {collection_interval}s, History size: {history_size}")


def should_log_metrics(step: int) -> bool:
    """Check if metrics should be logged at this step based on environment config"""
    log_interval = int(os.getenv('EFFICIENTLLM_LOG_INTERVAL', '10'))
    return step % log_interval == 0


def finalize_efficientllm_metrics():
    """Finalize EfficientLLM metrics collection"""
    collector = get_efficientllm_collector()
    collector.stop_collection()
    logger.info("[EfficientLLM] Metrics collection finalized")