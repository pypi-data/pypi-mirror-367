#!/bin/bash

# Quick test script for attention-free mechanisms
# This script runs short training sessions to verify all components work

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
PRETRAIN_DIR="$( dirname "$SCRIPT_DIR" )"

echo "=========================================="
echo "EfficientLLM Attention-Free Quick Test"
echo "=========================================="

# Test parameters
TEST_STEPS=10
TEST_BATCH_SIZE=2
TEST_SEQ_LEN=512

# Create test dataset (small sample)
TEST_DATA_DIR="${PRETRAIN_DIR}/test_data"
mkdir -p "${TEST_DATA_DIR}"

TEST_DATASET="${TEST_DATA_DIR}/test_fineweb.jsonl"

# Generate small test dataset if not exists
if [ ! -f "${TEST_DATASET}" ]; then
    echo "Creating test dataset..."
    cat > "${TEST_DATASET}" << 'EOF'
{"text": "The quick brown fox jumps over the lazy dog. This is a test sentence for language model training."}
{"text": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models."}
{"text": "Natural language processing involves the interaction between computers and human language."}
{"text": "Deep learning uses neural networks with multiple layers to learn representations of data."}
{"text": "Transformers have revolutionized the field of natural language processing in recent years."}
EOF
fi

echo "Test dataset created at: ${TEST_DATASET}"

# Test results directory
TEST_RESULTS_DIR="${PRETRAIN_DIR}/test_results"
mkdir -p "${TEST_RESULTS_DIR}"

# Function to test individual model
test_model() {
    local model=$1
    local size=$2
    
    echo "Testing ${model} ${size}..."
    
    local output_dir="${TEST_RESULTS_DIR}/${model}_${size}_test"
    mkdir -p "${output_dir}"
    
    case $model in
        "mamba")
            python "${PRETRAIN_DIR}/mamba/train_mamba_fineweb.py" \
                --model_size "${size}" \
                --data_path "${TEST_DATASET}" \
                --output_dir "${output_dir}" \
                --batch_size "${TEST_BATCH_SIZE}" \
                --max_length "${TEST_SEQ_LEN}" \
                --max_steps "${TEST_STEPS}" \
                --log_interval 2 \
                --learning_rate 1e-4
            ;;
        "pythia")
            python "${PRETRAIN_DIR}/pythia/train_pythia_fineweb.py" \
                --model_size "${size}" \
                --data_path "${TEST_DATASET}" \
                --output_dir "${output_dir}" \
                --batch_size "${TEST_BATCH_SIZE}" \
                --max_length "${TEST_SEQ_LEN}" \
                --max_steps "${TEST_STEPS}" \
                --log_interval 2 \
                --learning_rate 1e-4
            ;;
        "rwkv")
            python "${PRETRAIN_DIR}/RWKV-LM/train_rwkv_fineweb.py" \
                --model_size "${size}" \
                --data_path "${TEST_DATASET}" \
                --output_dir "${output_dir}" \
                --batch_size "${TEST_BATCH_SIZE}" \
                --max_length "${TEST_SEQ_LEN}" \
                --max_steps "${TEST_STEPS}" \
                --log_interval 2 \
                --learning_rate 1e-4
            ;;
    esac
    
    # Check if metrics file was generated
    if [ -f "${output_dir}/efficientllm_metrics.json" ]; then
        echo "✓ ${model} ${size} test completed successfully"
        echo "  Metrics file: ${output_dir}/efficientllm_metrics.json"
    else
        echo "✗ ${model} ${size} test failed - no metrics file generated"
        return 1
    fi
}

# Test models (skip Qwen2.5 for now as it requires more complex setup)
MODELS=("mamba" "pythia" "rwkv")
SIZES=("0.5B")  # Test only smallest size for quick verification

echo "Starting quick tests..."
echo "Models: ${MODELS[@]}"
echo "Size: ${SIZES[@]}"
echo "Test steps: ${TEST_STEPS}"
echo ""

# Run tests
failed_tests=0
total_tests=0

for model in "${MODELS[@]}"; do
    for size in "${SIZES[@]}"; do
        total_tests=$((total_tests + 1))
        
        echo "=========================================="
        echo "Test ${total_tests}: ${model} ${size}"
        echo "=========================================="
        
        if test_model "${model}" "${size}"; then
            echo "Test passed ✓"
        else
            echo "Test failed ✗"
            failed_tests=$((failed_tests + 1))
        fi
        
        echo ""
    done
done

# Test results collection
echo "=========================================="
echo "Testing results collection..."
echo "=========================================="

python "${SCRIPT_DIR}/collect_attention_free_results.py" \
    --results_dir "${TEST_RESULTS_DIR}" \
    --output_dir "${TEST_RESULTS_DIR}/tables"

if [ -f "${TEST_RESULTS_DIR}/tables/attention_free_table.tex" ]; then
    echo "✓ Results collection test passed"
    echo "  LaTeX table: ${TEST_RESULTS_DIR}/tables/attention_free_table.tex"
    echo "  CSV table: ${TEST_RESULTS_DIR}/tables/attention_free_results.csv"
else
    echo "✗ Results collection test failed"
    failed_tests=$((failed_tests + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "Quick Test Summary"
echo "=========================================="
echo "Total tests: ${total_tests}"
echo "Passed: $((total_tests - failed_tests))"
echo "Failed: ${failed_tests}"

if [ ${failed_tests} -eq 0 ]; then
    echo "🎉 All tests passed! The attention-free benchmark is ready to use."
    echo ""
    echo "Next steps:"
    echo "1. Prepare full dataset: cd ${SCRIPT_DIR} && ./prepare_fineweb_dataset.sh"
    echo "2. Run full experiments: ./run_all_attention_free_experiments.sh"
    echo "3. Collect results: python collect_attention_free_results.py"
else
    echo "❌ Some tests failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "Test results directory: ${TEST_RESULTS_DIR}"
echo "Cleanup: rm -rf ${TEST_RESULTS_DIR} ${TEST_DATA_DIR}"