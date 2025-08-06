"""
EfficientLLM Core Module: Contains shared utilities and configurations
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

class EfficientLLMConfig:
    """Configuration manager for EfficientLLM"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.base_dir / "configs" / "default.yaml"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix == '.yaml':
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "datasets": {
                "fine_webedu": {
                    "version": "v1.2.0",
                    "sample": "350BT",
                    "path": "HuggingFace:fine-webedu-v1.2.0-sample-350BT"
                }
            },
            "models": {
                "qwen2.5": {
                    "base_model": "Qwen/Qwen2.5",
                    "attention_types": ["MQA", "GQA", "MLA", "NSA"]
                },
                "mamba": {
                    "base_model": "state-spaces/mamba",
                    "architecture": "ssm"
                },
                "pythia": {
                    "base_model": "EleutherAI/pythia",
                    "architecture": "gpt-neox"
                },
                "rwkv": {
                    "base_model": "RWKV/rwkv-4",
                    "architecture": "rwkv"
                }
            },
            "training": {
                "default_precision": "bfloat16",
                "context_length": 8192,
                "learning_rate": 1e-4,
                "weight_decay": 0.1,
                "warmup_steps": 100
            },
            "evaluation": {
                "metrics": ["AMU", "PCU", "AL", "TT", "ST", "IT", "AEC", "MCR"],
                "tasks": ["hellaswag", "piqa", "winogrande", "arc_easy", "arc_challenge"]
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file"""
        save_path = path or self.config_path
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            if save_path.suffix == '.yaml':
                yaml.dump(self.config, f, default_flow_style=False)
            else:
                json.dump(self.config, f, indent=2)


class ModelRegistry:
    """Registry for model configurations and architectures"""
    
    def __init__(self):
        self.models = {}
        self.register_default_models()
    
    def register_default_models(self):
        """Register default model configurations"""
        # Qwen2.5 configurations
        self.register_model("qwen2.5", {
            "0.5B": {
                "num_layers": 24,
                "hidden_size": 896,
                "num_attention_heads": 14,
                "num_key_value_heads": 2,
                "intermediate_size": 4864,
                "max_position_embeddings": 32768,
                "vocab_size": 151936
            },
            "1.5B": {
                "num_layers": 28,
                "hidden_size": 1536,
                "num_attention_heads": 12,
                "num_key_value_heads": 2,
                "intermediate_size": 8960,
                "max_position_embeddings": 32768,
                "vocab_size": 151936
            },
            "3B": {
                "num_layers": 36,
                "hidden_size": 2048,
                "num_attention_heads": 16,
                "num_key_value_heads": 2,
                "intermediate_size": 11008,
                "max_position_embeddings": 32768,
                "vocab_size": 151936
            }
        })
        
        # Mamba configurations
        self.register_model("mamba", {
            "0.5B": {
                "num_layers": 24,
                "d_model": 768,
                "d_state": 16,
                "d_conv": 4,
                "expand": 2
            },
            "1.5B": {
                "num_layers": 48,
                "d_model": 1536,
                "d_state": 16,
                "d_conv": 4,
                "expand": 2
            },
            "3B": {
                "num_layers": 64,
                "d_model": 2560,
                "d_state": 16,
                "d_conv": 4,
                "expand": 2
            }
        })
        
        # Pythia configurations
        self.register_model("pythia", {
            "0.5B": {
                "num_layers": 24,
                "hidden_size": 1024,
                "num_attention_heads": 16,
                "intermediate_size": 4096,
                "max_position_embeddings": 8192,
                "vocab_size": 50304
            },
            "1.5B": {
                "num_layers": 32,
                "hidden_size": 2048,
                "num_attention_heads": 16,
                "intermediate_size": 8192,
                "max_position_embeddings": 8192,
                "vocab_size": 50304
            },
            "3B": {
                "num_layers": 32,
                "hidden_size": 2560,
                "num_attention_heads": 32,
                "intermediate_size": 10240,
                "max_position_embeddings": 8192,
                "vocab_size": 50304
            }
        })
        
        # RWKV configurations
        self.register_model("rwkv", {
            "0.5B": {
                "num_layers": 24,
                "embed_dim": 1024,
                "context_length": 8192
            },
            "1.5B": {
                "num_layers": 32,
                "embed_dim": 2048,
                "context_length": 8192
            },
            "3B": {
                "num_layers": 40,
                "embed_dim": 2560,
                "context_length": 8192
            }
        })
    
    def register_model(self, name: str, configs: Dict[str, Dict[str, Any]]):
        """Register a model with its configurations"""
        self.models[name] = configs
    
    def get_model_config(self, name: str, size: str) -> Optional[Dict[str, Any]]:
        """Get model configuration"""
        if name in self.models and size in self.models[name]:
            return self.models[name][size].copy()
        return None
    
    def list_models(self) -> List[str]:
        """List available models"""
        return list(self.models.keys())
    
    def list_sizes(self, model: str) -> List[str]:
        """List available sizes for a model"""
        if model in self.models:
            return list(self.models[model].keys())
        return []


class MetricsCalculator:
    """Calculator for EfficientLLM metrics"""
    
    @staticmethod
    def calculate_amu(memory_usage_over_time: List[float]) -> float:
        """Calculate Average Memory Utilization (AMU)"""
        if not memory_usage_over_time:
            return 0.0
        return sum(memory_usage_over_time) / len(memory_usage_over_time)
    
    @staticmethod
    def calculate_pcu(peak_memory: float, total_memory: float) -> float:
        """Calculate Peak Capacity Utilization (PCU)"""
        if total_memory == 0:
            return 0.0
        return peak_memory / total_memory
    
    @staticmethod
    def calculate_al(computation_times: List[float], communication_times: List[float]) -> float:
        """Calculate Average Latency (AL)"""
        if not computation_times or not communication_times:
            return 0.0
        total_times = [comp + comm for comp, comm in zip(computation_times, communication_times)]
        return sum(total_times) / len(total_times)
    
    @staticmethod
    def calculate_tt(total_tokens: int, model_params: int, total_time: float) -> float:
        """Calculate Token Throughput (TT)"""
        if total_time == 0 or model_params == 0:
            return 0.0
        return total_tokens / (model_params * total_time)
    
    @staticmethod
    def calculate_aec(power_consumption_over_time: List[float]) -> float:
        """Calculate Average Energy Consumption (AEC)"""
        if not power_consumption_over_time:
            return 0.0
        return sum(power_consumption_over_time) / len(power_consumption_over_time)


# Global instances
config = EfficientLLMConfig()
model_registry = ModelRegistry()
metrics_calculator = MetricsCalculator()

__all__ = [
    "EfficientLLMConfig",
    "ModelRegistry", 
    "MetricsCalculator",
    "config",
    "model_registry",
    "metrics_calculator"
]