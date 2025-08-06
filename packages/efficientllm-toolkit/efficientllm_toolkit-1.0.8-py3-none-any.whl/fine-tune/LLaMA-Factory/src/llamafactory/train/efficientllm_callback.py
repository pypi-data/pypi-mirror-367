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
EfficientLLM Callback for LLaMA-Factory

This module provides a Hugging Face Transformers callback to integrate
EfficientLLM metrics collection into the training process.
"""

from typing import TYPE_CHECKING
from transformers import TrainerCallback, TrainerControl, TrainerState

from ..extras.efficientllm_metrics import (
    get_efficientllm_collector,
    should_log_metrics,
    finalize_efficientllm_metrics
)
from ..extras.logging import get_logger


if TYPE_CHECKING:
    from transformers import TrainingArguments


logger = get_logger(__name__)


class EfficientLLMCallback(TrainerCallback):
    """
    Callback to integrate EfficientLLM metrics into LLaMA-Factory training
    """
    
    def __init__(self):
        super().__init__()
        self.collector = None
        self.initialized = False
    
    def on_train_begin(self, args: "TrainingArguments", state: TrainerState, control: TrainerControl, **kwargs):
        """Called at the beginning of training"""
        try:
            self.collector = get_efficientllm_collector()
            # Additional initialization if needed
            logger.info("[EfficientLLM] Callback initialized for training")
        except Exception as e:
            logger.warning(f"[EfficientLLM] Failed to initialize callback: {e}")
    
    def on_step_begin(self, args: "TrainingArguments", state: TrainerState, control: TrainerControl, **kwargs):
        """Called at the beginning of each training step"""
        if self.collector is not None:
            try:
                self.collector.record_step_start()
            except Exception:
                pass  # Silently continue if metrics collection fails
    
    def on_step_end(self, args: "TrainingArguments", state: TrainerState, control: TrainerControl, **kwargs):
        """Called at the end of each training step"""
        if self.collector is not None:
            try:
                # Calculate tokens and samples processed in this step
                per_device_batch_size = args.per_device_train_batch_size
                gradient_accumulation_steps = args.gradient_accumulation_steps
                world_size = args.world_size if hasattr(args, 'world_size') else 1
                
                effective_batch_size = per_device_batch_size * gradient_accumulation_steps * world_size
                
                # Estimate tokens processed (will be more accurate if we can get sequence length)
                # For now, use a default sequence length or try to get it from the model
                sequence_length = getattr(args, 'model_max_length', 2048)  # Default fallback
                
                tokens_processed = sequence_length * effective_batch_size
                samples_processed = effective_batch_size
                
                self.collector.record_step_end(tokens_processed, samples_processed)
            except Exception:
                pass  # Silently continue if metrics collection fails
    
    def on_log(self, args: "TrainingArguments", state: TrainerState, control: TrainerControl, logs=None, **kwargs):
        """Called when logging occurs"""
        if self.collector is not None and logs is not None and should_log_metrics(state.global_step):
            try:
                # Get current loss from logs
                current_loss = logs.get('train_loss', logs.get('loss', 0.0))
                
                # Get tensorboard writer if available
                tb_writer = None
                if hasattr(kwargs.get('model', None), 'tb_writer'):
                    tb_writer = kwargs['model'].tb_writer
                elif 'tb_writer' in kwargs:
                    tb_writer = kwargs['tb_writer']
                
                # Log EfficientLLM metrics
                metrics_dict = self.collector.log_metrics(state.global_step, current_loss, tb_writer)
                
                # Add metrics to the logs dictionary so they appear in other loggers
                if logs is not None:
                    logs.update(metrics_dict)
                    
            except Exception as e:
                logger.debug(f"[EfficientLLM] Failed to log metrics: {e}")
    
    def on_train_end(self, args: "TrainingArguments", state: TrainerState, control: TrainerControl, **kwargs):
        """Called at the end of training"""
        try:
            finalize_efficientllm_metrics()
        except Exception:
            pass  # Silently continue if metrics finalization fails