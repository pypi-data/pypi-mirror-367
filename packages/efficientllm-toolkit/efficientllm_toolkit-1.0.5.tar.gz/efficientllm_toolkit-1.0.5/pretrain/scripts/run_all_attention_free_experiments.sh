#!/bin/bash

# Run all attention-free mechanism experiments
# This script executes all model configurations and collects results

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
PRETRAIN_DIR="$( dirname "$SCRIPT_DIR" )"
EXPERIMENT_DIR="${PRETRAIN_DIR}/experiments/attention_free_benchmark"
RESULTS_DIR="${EXPERIMENT_DIR}/results"
LOGS_DIR="${EXPERIMENT_DIR}/logs"

# Environment setup
ENV=${1:-dsw}  # dsw or dlc
DEVICE=${2:-cuda:0}
MAX_STEPS=${3:-1000}  # For quick testing, increase for full runs

# Models and sizes to run
MODELS=("qwen2.5" "mamba" "pythia" "rwkv")
SIZES=("0.5B" "1.5B" "3B")

# Create directories
mkdir -p "${RESULTS_DIR}"
mkdir -p "${LOGS_DIR}"

echo "=========================================="
echo "EfficientLLM Attention-Free Benchmark Runner"
echo "=========================================="
echo "Environment: ${ENV}"
echo "Device: ${DEVICE}"
echo "Max Steps: ${MAX_STEPS}"
echo "Results Dir: ${RESULTS_DIR}"
echo "=========================================="

# Check if dataset is prepared
DATASET_PATH="${PRETRAIN_DIR}/Pai-Megatron-Patch/data/fineweb_edu/processed/fineweb_edu_train.jsonl"
if [ ! -f "${DATASET_PATH}" ]; then
    echo "Dataset not found at: ${DATASET_PATH}"
    echo "Please run prepare_fineweb_dataset.sh first"
    exit 1
fi

echo "Using dataset: ${DATASET_PATH}"

# Function to run individual experiment
run_experiment() {
    local model=$1
    local size=$2
    local batch_size=$3
    
    echo "Running ${model} ${size} experiment..."
    
    # Create output directory
    local output_dir="${RESULTS_DIR}/${model}_${size}"
    mkdir -p "${output_dir}"
    
    # Log file
    local log_file="${LOGS_DIR}/${model}_${size}.log"
    
    # Get model parameters
    local model_params
    case $size in
        "0.5B") model_params=518000000 ;;
        "1.5B") model_params=1500000000 ;;
        "3B") model_params=3000000000 ;;
    esac
    
    # Set training script based on model
    local train_script
    case $model in
        "qwen2.5")
            train_script="${PRETRAIN_DIR}/Pai-Megatron-Patch/examples/qwen2/pretrain_qwen2_moe.py"
            ;;
        "mamba")
            train_script="${PRETRAIN_DIR}/mamba/train_mamba_fineweb.py"
            ;;
        "pythia")
            train_script="${PRETRAIN_DIR}/pythia/train_pythia_fineweb.py"
            ;;
        "rwkv")
            train_script="${PRETRAIN_DIR}/RWKV-LM/train_rwkv_fineweb.py"
            ;;
    esac
    
    # Common arguments
    local common_args="--model_size ${size} --data_path ${DATASET_PATH} --output_dir ${output_dir} --batch_size ${batch_size} --max_length 8192 --learning_rate 1e-4 --max_steps ${MAX_STEPS} --log_interval 10 --save_interval 500"
    
    # Run training
    echo "Starting ${model} ${size} training..."
    echo "Command: python ${train_script} ${common_args}"
    echo "Log file: ${log_file}"
    
    if [ "${model}" = "qwen2.5" ]; then
        # For Qwen2.5, use the existing Megatron training script with custom arguments
        run_qwen_experiment "${size}" "${batch_size}" "${output_dir}" "${log_file}"
    else
        # For other models, use the custom training scripts
        python "${train_script}" ${common_args} 2>&1 | tee "${log_file}"
    fi
    
    echo "Completed ${model} ${size} experiment"
    echo "Results saved to: ${output_dir}"
    echo "Logs saved to: ${log_file}"
    echo ""
}

# Special function for Qwen2.5 using Megatron
run_qwen_experiment() {
    local size=$1
    local batch_size=$2
    local output_dir=$3
    local log_file=$4
    
    # Set up Megatron environment
    export PYTHONPATH="${PRETRAIN_DIR}/Pai-Megatron-Patch:${PRETRAIN_DIR}/Pai-Megatron-Patch/backends/megatron/Megatron-LM-250328:$PYTHONPATH"
    export CUDA_DEVICE_MAX_CONNECTIONS=1
    
    # GPU setup
    GPUS_PER_NODE=$(python -c "import torch; print(torch.cuda.device_count())")
    GLOBAL_BATCH_SIZE=$((batch_size * GPUS_PER_NODE))
    
    # Model architecture based on size
    case $size in
        "0.5B")
            NUM_LAYERS=24
            HIDDEN_SIZE=896
            NUM_ATTN_HEADS=14
            INTERMEDIATE_SIZE=4864
            NUM_KEY_VALUE_HEADS=2
            ;;
        "1.5B")
            NUM_LAYERS=28
            HIDDEN_SIZE=1536
            NUM_ATTN_HEADS=12
            INTERMEDIATE_SIZE=8960
            NUM_KEY_VALUE_HEADS=2
            ;;
        "3B")
            NUM_LAYERS=36
            HIDDEN_SIZE=2048
            NUM_ATTN_HEADS=16
            INTERMEDIATE_SIZE=11008
            NUM_KEY_VALUE_HEADS=2
            ;;
    esac
    
    # Megatron training command
    local megatron_args="
        --num-layers ${NUM_LAYERS}
        --hidden-size ${HIDDEN_SIZE}
        --num-attention-heads ${NUM_ATTN_HEADS}
        --ffn-hidden-size ${INTERMEDIATE_SIZE}
        --seq-length 8192
        --max-position-embeddings 32768
        --micro-batch-size ${batch_size}
        --global-batch-size ${GLOBAL_BATCH_SIZE}
        --train-iters ${MAX_STEPS}
        --lr 1e-4
        --min-lr 1e-5
        --lr-decay-style cosine
        --weight-decay 0.1
        --adam-beta1 0.9
        --adam-beta2 0.95
        --clip-grad 1.0
        --init-method-std 0.008
        --attention-dropout 0.0
        --hidden-dropout 0.0
        --lr-warmup-iters 100
        --save-interval 500
        --log-interval 10
        --eval-interval 1000
        --eval-iters 10
        --tensorboard-dir ${output_dir}/tensorboard
        --save ${output_dir}/checkpoint
        --data-path ${DATASET_PATH}
        --split 99,1,0
        --dataset JSON
        --json-keys text
        --vocab-size 151936
        --extra-vocab-size 293
        --patch-tokenizer-type Qwen2Tokenizer
        --swiglu
        --normalization RMSNorm
        --norm-epsilon 1e-6
        --disable-bias-linear
        --add-qkv-bias
        --use-rotary-position-embeddings
        --rotary-percent 1.0
        --rotary-base 1000000
        --group-query-attention
        --num-query-groups ${NUM_KEY_VALUE_HEADS}
        --bf16
        --no-load-optim
        --no-load-rng
        --tensor-model-parallel-size 1
        --pipeline-model-parallel-size 1
        --context-parallel-size 1
        --num-workers 8
    "
    
    # Run Megatron training
    python "${PRETRAIN_DIR}/Pai-Megatron-Patch/examples/qwen2/pretrain_qwen2_moe.py" ${megatron_args} 2>&1 | tee "${log_file}"
}

# Main execution loop
total_experiments=$((${#MODELS[@]} * ${#SIZES[@]}))
current_experiment=0

for model in "${MODELS[@]}"; do
    for size in "${SIZES[@]}"; do
        current_experiment=$((current_experiment + 1))
        
        echo "=========================================="
        echo "Experiment ${current_experiment}/${total_experiments}: ${model} ${size}"
        echo "=========================================="
        
        # Get batch size based on model size
        case $size in
            "0.5B") batch_size=8 ;;
            "1.5B") batch_size=4 ;;
            "3B") batch_size=2 ;;
        esac
        
        # Run the experiment
        run_experiment "${model}" "${size}" "${batch_size}"
        
        # Brief pause between experiments
        sleep 5
    done
done

echo "=========================================="
echo "All experiments completed!"
echo "=========================================="
echo "Results directory: ${RESULTS_DIR}"
echo "Logs directory: ${LOGS_DIR}"
echo ""
echo "Next steps:"
echo "1. Generate results table: python collect_attention_free_results.py"
echo "2. View individual results: ls ${RESULTS_DIR}/*/"
echo "3. Check logs: ls ${LOGS_DIR}/"