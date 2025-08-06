#!/bin/bash

# EfficientLLM Metrics Configuration
# This script sets up environment variables for EfficientLLM metrics collection

# Enable/disable EfficientLLM metrics collection (default: enabled)
export EFFICIENTLLM_METRICS_ENABLED=${EFFICIENTLLM_METRICS_ENABLED:-true}

# Metrics collection interval in seconds (default: 1.0)
export EFFICIENTLLM_COLLECTION_INTERVAL=${EFFICIENTLLM_COLLECTION_INTERVAL:-1.0}

# Metrics history size (default: 1000)
export EFFICIENTLLM_HISTORY_SIZE=${EFFICIENTLLM_HISTORY_SIZE:-1000}

# Metrics logging interval (default: log every 10 iterations)
export EFFICIENTLLM_LOG_INTERVAL=${EFFICIENTLLM_LOG_INTERVAL:-10}

echo "EfficientLLM Metrics Configuration:"
echo "  EFFICIENTLLM_METRICS_ENABLED=$EFFICIENTLLM_METRICS_ENABLED"
echo "  EFFICIENTLLM_COLLECTION_INTERVAL=$EFFICIENTLLM_COLLECTION_INTERVAL"
echo "  EFFICIENTLLM_HISTORY_SIZE=$EFFICIENTLLM_HISTORY_SIZE"
echo "  EFFICIENTLLM_LOG_INTERVAL=$EFFICIENTLLM_LOG_INTERVAL"