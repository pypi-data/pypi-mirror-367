#!/bin/bash

# EfficientLLM Comprehensive Benchmark Runner
# This script runs all variants and collects EfficientLLM metrics for table generation

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MEGATRON_PATCH_PATH="$( cd "$SCRIPT_DIR/.." && pwd )"
BENCHMARK_DIR="$MEGATRON_PATCH_PATH/examples/efficientllm_benchmark"
RESULTS_DIR="$MEGATRON_PATCH_PATH/results/efficientllm_benchmark"

# Create results directory
mkdir -p "$RESULTS_DIR"/{attention_results,positional_encoding_results,moe_results}

# Enable EfficientLLM metrics
export EFFICIENTLLM_METRICS_ENABLED=true
export EFFICIENTLLM_COLLECTION_INTERVAL=1.0
export EFFICIENTLLM_LOG_INTERVAL=10
export EFFICIENTLLM_HISTORY_SIZE=1000

# Dataset configuration (set your paths here)
export DATASET_PATH="${DATASET_PATH:-/path/to/your/dataset}"
export VALID_DATASET_PATH="${VALID_DATASET_PATH:-/path/to/your/valid_dataset}"
export OUTPUT_BASEPATH="${OUTPUT_BASEPATH:-$RESULTS_DIR}"

echo "=========================================="
echo "EfficientLLM Comprehensive Benchmark"
echo "=========================================="
echo "Benchmark Directory: $BENCHMARK_DIR"
echo "Results Directory: $RESULTS_DIR"
echo "Dataset Path: $DATASET_PATH"
echo "=========================================="

# Function to run benchmark and collect metrics
run_benchmark() {
    local variant_type="$1"
    local script_name="$2"
    local output_name="$3"
    
    echo "Running benchmark: $script_name"
    echo "Output will be saved to: $RESULTS_DIR/${variant_type}_results/${output_name}.log"
    
    cd "$BENCHMARK_DIR/$variant_type"
    
    # Run the benchmark and capture output
    if timeout 3600 ./"$script_name" dsw > "$RESULTS_DIR/${variant_type}_results/${output_name}.log" 2>&1; then
        echo "✅ Completed: $script_name"
        
        # Extract key metrics from the log
        extract_metrics "$RESULTS_DIR/${variant_type}_results/${output_name}.log" > "$RESULTS_DIR/${variant_type}_results/${output_name}_metrics.txt"
    else
        echo "❌ Failed or timed out: $script_name"
        echo "Check log: $RESULTS_DIR/${variant_type}_results/${output_name}.log"
    fi
}

# Function to extract key metrics from logs
extract_metrics() {
    local log_file="$1"
    
    echo "=== EfficientLLM Metrics Summary ==="
    
    # Extract final metrics (last occurrence of each metric)
    local amu=$(grep "AMU (GB):" "$log_file" | tail -1 | grep -o "AMU (GB): [0-9.]*" | cut -d' ' -f3)
    local pcu=$(grep "PCU (Ratio):" "$log_file" | tail -1 | grep -o "PCU (Ratio): [0-9.]*" | cut -d' ' -f3)
    local al=$(grep "AL (Seconds):" "$log_file" | tail -1 | grep -o "AL (Seconds): [0-9.]*" | cut -d' ' -f3)
    local tt=$(grep "TT (Tokens/Param/Sec):" "$log_file" | tail -1 | grep -o "TT (Tokens/Param/Sec): [0-9.e+-]*" | cut -d' ' -f3)
    local st=$(grep "ST (Samples/Param/Sec):" "$log_file" | tail -1 | grep -o "ST (Samples/Param/Sec): [0-9.e+-]*" | cut -d' ' -f3)
    local aec=$(grep "AEC (Watts):" "$log_file" | tail -1 | grep -o "AEC (Watts): [0-9.]*" | cut -d' ' -f3)
    
    # Extract perplexity (validation loss)
    local ppl=$(grep "validation loss" "$log_file" | tail -1 | grep -o "[0-9.]*" | head -1)
    
    # Extract training time
    local gpu_hours=$(grep "elapsed time per iteration (ms):" "$log_file" | tail -1 | grep -o "[0-9.]*" | head -1)
    
    echo "AMU (GB): ${amu:-N/A}"
    echo "PCU (Ratio): ${pcu:-N/A}"
    echo "AL (Seconds): ${al:-N/A}"
    echo "TT (Tokens/Param/Sec): ${tt:-N/A}"
    echo "ST (Samples/Param/Sec): ${st:-N/A}"
    echo "AEC (Watts): ${aec:-N/A}"
    echo "PPL: ${ppl:-N/A}"
    echo "GPU Hours: ${gpu_hours:-N/A}"
}

# Function to run attention mechanism benchmarks
run_attention_benchmarks() {
    echo "=========================================="
    echo "Running Attention Mechanism Benchmarks"
    echo "=========================================="
    
    # MQA variants
    run_benchmark "attention_variants" "run_mqa_0.5B.sh" "mqa_0.5B"
    run_benchmark "attention_variants" "run_mqa_1.5B.sh" "mqa_1.5B"
    run_benchmark "attention_variants" "run_mqa_3B.sh" "mqa_3B"
    
    # GQA variants (baseline)
    run_benchmark "attention_variants" "run_gqa_0.5B.sh" "gqa_0.5B"
    run_benchmark "attention_variants" "run_gqa_1.5B.sh" "gqa_1.5B"
    run_benchmark "attention_variants" "run_gqa_3B.sh" "gqa_3B"
    
    # MLA variants
    run_benchmark "attention_variants" "run_mla_0.5B.sh" "mla_0.5B"
    run_benchmark "attention_variants" "run_mla_1.5B.sh" "mla_1.5B"
    run_benchmark "attention_variants" "run_mla_3B.sh" "mla_3B"
    
    # NSA variants
    run_benchmark "attention_variants" "run_nsa_0.5B.sh" "nsa_0.5B"
    run_benchmark "attention_variants" "run_nsa_1.5B.sh" "nsa_1.5B"
    run_benchmark "attention_variants" "run_nsa_3B.sh" "nsa_3B"
}

# Function to run positional encoding benchmarks
run_positional_encoding_benchmarks() {
    echo "=========================================="
    echo "Running Positional Encoding Benchmarks"
    echo "=========================================="
    
    run_benchmark "positional_encoding_variants" "run_gqa_rope_1.5B.sh" "rope_1.5B"
    run_benchmark "positional_encoding_variants" "run_gqa_absolute_1.5B.sh" "absolute_1.5B"
    run_benchmark "positional_encoding_variants" "run_gqa_learnable_absolute_1.5B.sh" "learnable_absolute_1.5B"
    run_benchmark "positional_encoding_variants" "run_gqa_relative_1.5B.sh" "relative_1.5B"
    run_benchmark "positional_encoding_variants" "run_gqa_none_1.5B.sh" "none_1.5B"
}

# Function to run MoE benchmarks
run_moe_benchmarks() {
    echo "=========================================="
    echo "Running MoE Benchmarks"
    echo "=========================================="
    
    # Dense baselines
    run_benchmark "moe_variants" "run_dense_1.5B.sh" "dense_1.5B"
    run_benchmark "moe_variants" "run_dense_3B.sh" "dense_3B"
    
    # MoE variants
    run_benchmark "moe_variants" "run_moe_0_5Bx8.sh" "moe_0.5Bx8"
    run_benchmark "moe_variants" "run_moe_1_5Bx8.sh" "moe_1.5Bx8"
}

# Function to generate summary tables
generate_summary_tables() {
    echo "=========================================="
    echo "Generating Summary Tables"
    echo "=========================================="
    
    # Generate attention mechanisms table
    cat > "$RESULTS_DIR/attention_mechanisms_table.txt" << EOF
Attention Mechanisms Results Summary
====================================

Method | Parameters | Micro Batch Size | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) | GPU Hours
-------|------------|------------------|-----|----------|-------------|---------------------|---------|----------
EOF

    # Process attention results
    for result_file in "$RESULTS_DIR/attention_results"/*_metrics.txt; do
        if [ -f "$result_file" ]; then
            variant=$(basename "$result_file" _metrics.txt)
            echo "Processing: $variant"
            # Add row to table (you would need to parse the metrics file)
        fi
    done
    
    # Generate positional encoding table
    cat > "$RESULTS_DIR/positional_encoding_table.txt" << EOF
Positional Encoding Results Summary
===================================

Method | Parameters | Context Length | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) | GPU Hours
-------|------------|----------------|-----|----------|-------------|---------------------|---------|----------
EOF
    
    # Generate MoE table
    cat > "$RESULTS_DIR/moe_table.txt" << EOF
MoE Results Summary
===================

Method | Parameters | Top K | PPL | AMU (GB) | AL (s/iter) | TT (Tokens/param/s) | AEC (W) | GPU Hours
-------|------------|-------|-----|----------|-------------|---------------------|---------|----------
EOF
    
    echo "Summary tables generated in: $RESULTS_DIR"
}

# Main execution
main() {
    # Check if configurations exist
    if [ ! -d "$BENCHMARK_DIR" ]; then
        echo "Error: Benchmark configurations not found!"
        echo "Please run: bash scripts/generate_efficientllm_configs.sh"
        exit 1
    fi
    
    # Check dataset paths
    if [ "$DATASET_PATH" = "/path/to/your/dataset" ]; then
        echo "Warning: Please set DATASET_PATH and VALID_DATASET_PATH environment variables"
        echo "Example:"
        echo "  export DATASET_PATH=/path/to/your/dataset"
        echo "  export VALID_DATASET_PATH=/path/to/your/valid_dataset"
        echo ""
        read -p "Continue with dummy paths? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Run benchmarks based on command line arguments
    case "${1:-all}" in
        "attention")
            run_attention_benchmarks
            ;;
        "positional")
            run_positional_encoding_benchmarks
            ;;
        "moe")
            run_moe_benchmarks
            ;;
        "all")
            run_attention_benchmarks
            run_positional_encoding_benchmarks  
            run_moe_benchmarks
            ;;
        *)
            echo "Usage: $0 [attention|positional|moe|all]"
            exit 1
            ;;
    esac
    
    # Generate summary tables
    generate_summary_tables
    
    echo "=========================================="
    echo "Benchmark completed!"
    echo "=========================================="
    echo "Results saved in: $RESULTS_DIR"
    echo ""
    echo "Summary tables:"
    echo "  - $RESULTS_DIR/attention_mechanisms_table.txt"
    echo "  - $RESULTS_DIR/positional_encoding_table.txt"
    echo "  - $RESULTS_DIR/moe_table.txt"
}

# Run main function with command line arguments
main "$@"