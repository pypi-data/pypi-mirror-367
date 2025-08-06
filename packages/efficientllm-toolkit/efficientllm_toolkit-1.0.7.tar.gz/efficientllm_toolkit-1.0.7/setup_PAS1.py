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
"""

# Read version from version file
version = "1.0.0"

setup(
    name="efficientllm",
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
)