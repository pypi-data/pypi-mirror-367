#!/bin/bash

# EfficientLLM PEFT Benchmark Runner
# Runs comprehensive PEFT method evaluation across multiple models and datasets

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LLAMAFACTORY_PATH="$( cd "$SCRIPT_DIR/.." && pwd )"
BENCHMARK_DIR="$LLAMAFACTORY_PATH/examples/peft_benchmark"
RESULTS_DIR="$LLAMAFACTORY_PATH/results/peft_benchmark"

# Create results directory
mkdir -p "$RESULTS_DIR"/{lora_results,freeze_full_results,logs,tables}

echo "==========================================="
echo "EfficientLLM PEFT Benchmark Runner"
echo "==========================================="
echo "LLaMA-Factory Path: $LLAMAFACTORY_PATH"
echo "Benchmark Dir: $BENCHMARK_DIR"
echo "Results Dir: $RESULTS_DIR"
echo "==========================================="

# Function to run benchmark configuration
run_benchmark() {
    local config_type="$1"
    local config_name="$2"
    local timeout_minutes="${3:-60}"
    
    echo ""
    echo "Running benchmark: $config_name"
    echo "Type: $config_type"
    echo "Timeout: ${timeout_minutes}m"
    
    local config_file="$BENCHMARK_DIR/$config_type/$config_name"
    local log_file="$RESULTS_DIR/logs/${config_name%.yaml}.log"
    local metrics_file="$RESULTS_DIR/logs/${config_name%.yaml}_metrics.txt"
    
    if [ ! -f "$config_file" ]; then
        echo "❌ Config file not found: $config_file"
        return 1
    fi
    
    cd "$LLAMAFACTORY_PATH"
    
    # Run the training with timeout
    echo "Command: llamafactory-cli train $config_file"
    if timeout "${timeout_minutes}m" llamafactory-cli train "$config_file" > "$log_file" 2>&1; then
        echo "✅ Completed: $config_name"
        
        # Extract EfficientLLM metrics
        extract_efficientllm_metrics "$log_file" > "$metrics_file"
        
        # Move results to appropriate directory
        local result_type="lora_results"
        if [[ "$config_type" == "freeze_full" ]]; then
            result_type="freeze_full_results"
        fi
        
        local model_dataset_method=$(basename "$config_file" .yaml)
        mkdir -p "$RESULTS_DIR/$result_type/$model_dataset_method"
        
        # Copy training logs and metrics
        cp "$log_file" "$RESULTS_DIR/$result_type/$model_dataset_method/"
        cp "$metrics_file" "$RESULTS_DIR/$result_type/$model_dataset_method/"
        
        # Copy model outputs if they exist
        local save_dir="./saves/peft_benchmark/$model_dataset_method"
        if [ -d "$save_dir" ]; then
            echo "Moving model outputs to results directory..."
            mv "$save_dir" "$RESULTS_DIR/$result_type/"
        fi
        
    else
        echo "❌ Failed or timed out: $config_name"
        echo "   Check log: $log_file"
        return 1
    fi
}

# Function to extract EfficientLLM metrics from training logs
extract_efficientllm_metrics() {
    local log_file="$1"
    
    if [ ! -f "$log_file" ]; then
        echo "Log file not found: $log_file"
        return 1
    fi
    
    echo "=== EfficientLLM PEFT Metrics Summary ==="
    echo "Extracted from: $(basename "$log_file")"
    echo "Timestamp: $(date)"
    echo ""
    
    # Extract training metrics
    echo "=== Training Metrics ==="
    
    # Extract final training loss
    local final_loss=$(grep "{'train_loss':" "$log_file" | tail -1 | grep -o "'train_loss': [0-9.]*" | cut -d' ' -f2)
    echo "Final Training Loss: ${final_loss:-N/A}"
    
    # Extract training time
    local total_time=$(grep "Training completed in" "$log_file" | grep -o "[0-9.]*s" | head -1)
    echo "Total Training Time: ${total_time:-N/A}"
    
    # Extract validation metrics if available
    echo ""
    echo "=== Validation Metrics ==="
    local eval_loss=$(grep "eval_loss.*[0-9]" "$log_file" | tail -1 | grep -o "[0-9.]*" | head -1)
    echo "Final Validation Loss: ${eval_loss:-N/A}"
    
    # Extract EfficientLLM specific metrics if available
    echo ""
    echo "=== EfficientLLM Metrics ==="
    
    # Check if EfficientLLM callback was used
    if grep -q "EfficientLLM" "$log_file"; then
        echo "EfficientLLM Callback: Active ✓"
        
        # Extract specific metrics (these would be logged by our callback)
        local amu=$(grep "AMU (GB):" "$log_file" | tail -1 | grep -o "AMU (GB): [0-9.]*" | cut -d' ' -f3)
        local pcu=$(grep "PCU (Ratio):" "$log_file" | tail -1 | grep -o "PCU (Ratio): [0-9.]*" | cut -d' ' -f3)
        local tt=$(grep "TT (Tokens/Param/Sec):" "$log_file" | tail -1 | grep -o "TT (Tokens/Param/Sec): [0-9.e+-]*" | cut -d' ' -f3)
        local st=$(grep "ST (Samples/Param/Sec):" "$log_file" | tail -1 | grep -o "ST (Samples/Param/Sec): [0-9.e+-]*" | cut -d' ' -f3)
        local aec=$(grep "AEC (Watts):" "$log_file" | tail -1 | grep -o "AEC (Watts): [0-9.]*" | cut -d' ' -f3)
        
        echo "AMU (Average Memory Utilization): ${amu:-N/A} GB"
        echo "PCU (Peak Compute Utilization): ${pcu:-N/A}"
        echo "TT (Token Throughput): ${tt:-N/A} tokens/param/sec"
        echo "ST (Sample Throughput): ${st:-N/A} samples/param/sec"
        echo "AEC (Average Energy Consumption): ${aec:-N/A} Watts"
    else
        echo "EfficientLLM Callback: Not detected"
    fi
    
    # Extract model parameters info
    echo ""
    echo "=== Model Info ==="
    local trainable_params=$(grep "trainable params:" "$log_file" | tail -1 | grep -o "[0-9,]*" | head -1)
    local all_params=$(grep "all params:" "$log_file" | tail -1 | grep -o "[0-9,]*" | head -1)
    local trainable_percentage=$(grep "trainable%:" "$log_file" | tail -1 | grep -o "[0-9.]*%" | head -1)
    
    echo "Trainable Parameters: ${trainable_params:-N/A}"
    echo "Total Parameters: ${all_params:-N/A}"
    echo "Trainable Percentage: ${trainable_percentage:-N/A}"
    
    # Extract memory usage
    echo ""
    echo "=== Memory Usage ==="
    local max_memory=$(grep -i "memory" "$log_file" | grep -o "[0-9.]*GB" | sort -n | tail -1)
    echo "Peak Memory Usage: ${max_memory:-N/A}"
}

# Function to run specific benchmark type
run_benchmark_type() {
    local benchmark_type="$1"
    
    case "$benchmark_type" in
        "lora"|"lora_variants")
            echo "Running LoRA variants benchmarks..."
            for config in "$BENCHMARK_DIR/lora_variants"/*.yaml; do
                if [ -f "$config" ]; then
                    run_benchmark "lora_variants" "$(basename "$config")" 60
                fi
            done
            ;;
        "freeze_full")
            echo "Running Freeze/Full tuning benchmarks..."
            for config in "$BENCHMARK_DIR/freeze_full"/*.yaml; do
                if [ -f "$config" ]; then
                    local timeout=90  # Longer timeout for full training
                    if [[ "$(basename "$config")" == *"full"* ]]; then
                        timeout=120
                    fi
                    run_benchmark "freeze_full" "$(basename "$config")" $timeout
                fi
            done
            ;;
        "quick")
            echo "Running quick test benchmarks (small models only)..."
            for config in "$BENCHMARK_DIR"/lora_variants/*1b*.yaml "$BENCHMARK_DIR"/freeze_full/*1b*freeze*.yaml; do
                if [ -f "$config" ]; then
                    run_benchmark "$(dirname "$config" | xargs basename)" "$(basename "$config")" 30
                fi
            done
            ;;
        "all")
            run_benchmark_type "lora_variants"
            run_benchmark_type "freeze_full"
            ;;
        *)
            echo "Unknown benchmark type: $benchmark_type"
            echo "Available types: lora, freeze_full, quick, all"
            exit 1
            ;;
    esac
}

# Function to generate summary tables
generate_summary_tables() {
    echo ""
    echo "==========================================="
    echo "Generating Summary Tables"
    echo "==========================================="
    
    # Generate LoRA variants table
    cat > "$RESULTS_DIR/tables/lora_variants_summary.txt" << 'EOF'
EfficientLLM PEFT Benchmark - LoRA Variants Results
==================================================

Model | Dataset | Method | Trainable% | Final Loss | Training Time | AMU (GB) | TT | ST | AEC (W)
------|---------|--------|------------|------------|---------------|----------|----|----|--------
EOF
    
    # Process LoRA results
    for result_dir in "$RESULTS_DIR/lora_results"/*; do
        if [ -d "$result_dir" ]; then
            local name=$(basename "$result_dir")
            local metrics_file="$result_dir/${name}_metrics.txt"
            if [ -f "$metrics_file" ]; then
                # Parse metrics and add to table (simplified)
                echo "Processing LoRA result: $name"
            fi
        fi
    done
    
    # Generate Freeze/Full table
    cat > "$RESULTS_DIR/tables/freeze_full_summary.txt" << 'EOF'
EfficientLLM PEFT Benchmark - Freeze/Full Tuning Results
========================================================

Model | Dataset | Method | Trainable% | Final Loss | Training Time | AMU (GB) | TT | ST | AEC (W)
------|---------|--------|------------|------------|---------------|----------|----|----|--------
EOF
    
    echo "Summary tables generated in: $RESULTS_DIR/tables/"
}

# Main execution
main() {
    # Check if configurations exist
    if [ ! -d "$BENCHMARK_DIR" ]; then
        echo "Error: Benchmark configurations not found!"
        echo "Please run: bash scripts/generate_peft_benchmark_configs.sh"
        exit 1
    fi
    
    # Ensure EfficientLLM callback is available
    if [ ! -f "$LLAMAFACTORY_PATH/src/llamafactory/train/efficientllm_callback.py" ]; then
        echo "Warning: EfficientLLM callback not found. Metrics collection may be limited."
    fi
    
    local benchmark_type="${1:-quick}"
    
    echo "Starting PEFT benchmarks..."
    echo "Type: $benchmark_type"
    echo ""
    
    # Run benchmarks
    run_benchmark_type "$benchmark_type"
    
    # Generate summary tables
    generate_summary_tables
    
    echo ""
    echo "==========================================="
    echo "PEFT Benchmark completed!"
    echo "==========================================="
    echo "Results saved in: $RESULTS_DIR"
    echo ""
    echo "Summary tables:"
    echo "  - $RESULTS_DIR/tables/lora_variants_summary.txt"
    echo "  - $RESULTS_DIR/tables/freeze_full_summary.txt"
    echo ""
    echo "Individual results:"
    echo "  - LoRA variants: $RESULTS_DIR/lora_results/"
    echo "  - Freeze/Full: $RESULTS_DIR/freeze_full_results/"
    echo ""
    echo "Usage examples:"
    echo "  bash $0 quick      # Run small models only (fast)"
    echo "  bash $0 lora       # Run LoRA variants only"
    echo "  bash $0 freeze_full # Run Freeze/Full methods only"
    echo "  bash $0 all        # Run complete benchmark suite"
}

# Check command line arguments
if [ $# -gt 1 ]; then
    echo "Usage: $0 [quick|lora|freeze_full|all]"
    echo ""
    echo "Options:"
    echo "  quick      - Run quick tests (1B models only)"
    echo "  lora       - Run LoRA variants benchmarks"
    echo "  freeze_full - Run Freeze/Full tuning benchmarks"
    echo "  all        - Run complete benchmark suite (default)"
    exit 1
fi

# Run main function
main "$@"