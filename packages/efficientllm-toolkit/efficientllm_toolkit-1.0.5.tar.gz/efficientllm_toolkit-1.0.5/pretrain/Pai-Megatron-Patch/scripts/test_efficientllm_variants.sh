#!/bin/bash

# EfficientLLM Quick Test Script
# This script runs a quick test of all variants with minimal training steps

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEGATRON_PATCH_PATH="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "=========================================="
echo "EfficientLLM Quick Test"
echo "=========================================="

# First, generate configurations
if [ ! -d "$MEGATRON_PATCH_PATH/examples/efficientllm_benchmark" ]; then
    echo "Generating benchmark configurations..."
    bash "$SCRIPT_DIR/generate_efficientllm_configs.sh"
fi

# Set minimal training parameters for quick testing
export EFFICIENTLLM_METRICS_ENABLED=true
export EFFICIENTLLM_COLLECTION_INTERVAL=2.0
export EFFICIENTLLM_LOG_INTERVAL=5

# Create test dataset paths (using dummy data)
export DATASET_PATH="/tmp/dummy_dataset"
export VALID_DATASET_PATH="/tmp/dummy_dataset"
export OUTPUT_BASEPATH="$MEGATRON_PATCH_PATH/test_output"

echo "Test configuration:"
echo "  - Minimal training steps (10 iterations)"
echo "  - Small batch sizes"
echo "  - EfficientLLM metrics enabled"
echo "  - Output: $OUTPUT_BASEPATH"
echo ""

# Create dummy dataset if it doesn't exist
if [ ! -f "$DATASET_PATH" ]; then
    echo "Creating dummy dataset for testing..."
    mkdir -p "$(dirname $DATASET_PATH)"
    # Create a minimal dummy dataset (this is just for testing)
    echo "Warning: Using dummy dataset. Replace with real data for actual benchmarking."
fi

# Function to run quick test
run_quick_test() {
    local variant_type="$1"
    local script_name="$2"
    local test_name="$3"
    
    echo "Testing: $test_name"
    
    cd "$MEGATRON_PATCH_PATH/examples/efficientllm_benchmark/$variant_type"
    
    # Modify script for quick testing (override training parameters)
    local temp_script="/tmp/quick_test_${script_name}"
    cp "$script_name" "$temp_script"
    
    # Override training parameters for quick test
    sed -i 's/TRAIN_TOKENS=100000/TRAIN_TOKENS=1000/' "$temp_script"
    sed -i 's/WARMUP_TOKENS=10000/WARMUP_TOKENS=100/' "$temp_script"
    sed -i 's/--save-interval [0-9]*/--save-interval 100/' "$temp_script"
    sed -i 's/--eval-interval [0-9]*/--eval-interval 50/' "$temp_script"
    
    if timeout 300 bash "$temp_script" dsw > "$OUTPUT_BASEPATH/test_${test_name}.log" 2>&1; then
        echo "✅ $test_name: PASSED"
        
        # Extract basic metrics
        if grep -q "EfficientLLM Metrics" "$OUTPUT_BASEPATH/test_${test_name}.log"; then
            echo "   EfficientLLM metrics detected ✓"
        else
            echo "   EfficientLLM metrics missing ⚠️"
        fi
        
    else
        echo "❌ $test_name: FAILED (check $OUTPUT_BASEPATH/test_${test_name}.log)"
    fi
    
    rm -f "$temp_script"
    echo ""
}

# Create output directory
mkdir -p "$OUTPUT_BASEPATH"

echo "Running quick tests..."
echo ""

# Test one example from each variant type
echo "1. Testing Attention Mechanisms:"
run_quick_test "attention_variants" "run_mqa_0.5B.sh" "mqa_0.5B"
run_quick_test "attention_variants" "run_gqa_0.5B.sh" "gqa_0.5B"

echo "2. Testing Positional Encodings:"
run_quick_test "positional_encoding_variants" "run_gqa_rope_1.5B.sh" "rope_1.5B"
run_quick_test "positional_encoding_variants" "run_gqa_absolute_1.5B.sh" "absolute_1.5B"

echo "3. Testing MoE Variants:"
run_quick_test "moe_variants" "run_dense_1.5B.sh" "dense_1.5B"

echo "=========================================="
echo "Quick test completed!"
echo "=========================================="
echo ""
echo "Test results saved in: $OUTPUT_BASEPATH"
echo ""
echo "If all tests passed, you can run the full benchmark with:"
echo "  bash scripts/run_efficientllm_benchmark.sh"
echo ""
echo "Make sure to set proper dataset paths:"
echo "  export DATASET_PATH=/path/to/your/dataset"
echo "  export VALID_DATASET_PATH=/path/to/your/valid_dataset"