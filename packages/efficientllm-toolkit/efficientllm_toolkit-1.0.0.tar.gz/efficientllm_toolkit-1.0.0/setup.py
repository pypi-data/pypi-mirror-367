#!/usr/bin/env python3
"""
EfficientLLM: A Comprehensive Benchmark for Large Language Model Efficiency
"""

from setuptools import setup, find_packages
import os

# Read long description from README
long_description = """
EfficientLLM is a comprehensive benchmark suite for evaluating Large Language Model efficiency 
across different architectures, attention mechanisms, and training strategies. It provides 
unified metrics for memory utilization, computational efficiency, throughput, and energy consumption.

Key Features:
- Multi-architecture support (Transformer, Mamba, RWKV, Pythia)
- Attention mechanism evaluation (MQA, GQA, MLA, NSA)
- Comprehensive efficiency metrics (AMU, PCU, AL, TT, ST, IT, AEC, MCR)
- Unified CLI interface for easy experimentation
- Integration with popular frameworks (Megatron-Core, Transformers)
- Pre-configured datasets (Fine-WebEdu, C4, OpenWebText)
- Pre-trained checkpoint download support

Quick Start:
- Download pre-trained checkpoints: efficientllm --down
- Run attention mechanism benchmark: efficientllm --stage pretrain --model qwen2.5 --size 1.5B --attn_type MQA
- Reproduce paper experiments: efficientllm --reproduce_paper --experiment all
"""

# Read version from version file
version = "1.0.0"

setup(
    name="efficientllm-toolkit",
    version=version,
    author="EfficientLLM Team",
    author_email="contact@efficientllm.ai",
    description="A Comprehensive Benchmark for Large Language Model Efficiency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/efficientllm/efficientllm",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,
    package_data={
        "efficientllm": [
            "configs/**/*.yaml",
            "configs/**/*.json",
            "scripts/**/*.sh",
            "templates/**/*.py",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "torch>=1.12.0",
        "transformers>=4.21.0",
        "datasets>=2.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        
        # Training and optimization
        "accelerate>=0.20.0",
        "deepspeed>=0.9.0",
        "tensorboard>=2.8.0",
        "wandb>=0.13.0",
        
        # Evaluation and metrics
        "evaluate>=0.4.0",
        "scikit-learn>=1.0.0",
        "seaborn>=0.11.0",
        "matplotlib>=3.5.0",
        
        # Data processing
        "tokenizers>=0.13.0",
        "sentencepiece>=0.1.96",
        "protobuf>=3.20.0",
        
        # System utilities
        "psutil>=5.8.0",
        "pynvml>=11.4.0",
        "tqdm>=4.64.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jsonlines>=3.0.0",
        
        # Fine-tuning framework
        "llamafactory>=0.7.0",
        
        # Evaluation framework
        "lm_eval>=0.4.0",
        
        # Optional dependencies for specific features
        "flash-attn>=2.0.0;platform_machine=='x86_64'",
        "triton>=2.0.0;platform_machine=='x86_64'",
    ],
    extras_require={
        "megatron": [
            "megatron-core[dev]>=0.7.0",
            "apex>=0.1",
        ],
        "mamba": [
            "mamba-ssm>=1.2.0",
            "causal-conv1d>=1.4.0",
        ],
        "rwkv": [
            "rwkv>=0.8.0",
        ],
        "quantization": [
            "bitsandbytes>=0.41.0",
            "auto-gptq>=0.4.0",
            "optimum>=1.12.0",
        ],
        "inference": [
            "vllm>=0.2.0",
            "text-generation-inference>=1.0.0",
        ],
        "dev": [
            "pytest>=7.1.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "all": [
            "megatron-core[dev]>=0.7.0",
            "apex>=0.1",
            "mamba-ssm>=1.2.0",
            "causal-conv1d>=1.4.0",
            "rwkv>=0.8.0",
            "bitsandbytes>=0.41.0",
            "auto-gptq>=0.4.0",
            "optimum>=1.12.0",
            "vllm>=0.2.0",
            "text-generation-inference>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "efficientllm=efficientllm.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/efficientllm/efficientllm/issues",
        "Documentation": "https://efficientllm.readthedocs.io/",
        "Source": "https://github.com/efficientllm/efficientllm",
    },
    keywords=[
        "large language models",
        "efficiency",
        "benchmark",
        "attention mechanisms",
        "transformers",
        "mamba",
        "rwkv",
        "machine learning",
        "deep learning",
        "natural language processing",
    ],
)