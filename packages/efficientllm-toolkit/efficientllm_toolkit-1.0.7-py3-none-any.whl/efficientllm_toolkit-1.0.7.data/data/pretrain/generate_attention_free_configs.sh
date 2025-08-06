#!/bin/bash

# EfficientLLM Attention-Free Mechanisms Benchmark
# This script runs experiments for the four attention-free models on fine-webedu dataset

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
PRETRAIN_DIR="$( dirname "$SCRIPT_DIR" )"
OUTPUT_BASE_DIR="${PRETRAIN_DIR}/experiments/attention_free_benchmark/"

# Experiment configuration
MODELS=("qwen2.5" "mamba" "pythia" "rwkv")
SIZES=("0.5B" "1.5B" "3B")
CONTEXT_LENGTH=8192
TRAIN_TOKENS=100000000  # 100M tokens for benchmark

# Create output directories
mkdir -p "${OUTPUT_BASE_DIR}"
mkdir -p "${OUTPUT_BASE_DIR}/results"
mkdir -p "${OUTPUT_BASE_DIR}/logs"
mkdir -p "${OUTPUT_BASE_DIR}/configs"

echo "=========================================="
echo "EfficientLLM Attention-Free Benchmark"
echo "=========================================="
echo "Models: ${MODELS[@]}"
echo "Sizes: ${SIZES[@]}"
echo "Context Length: ${CONTEXT_LENGTH}"
echo "Training Tokens: ${TRAIN_TOKENS}"
echo "Output Directory: ${OUTPUT_BASE_DIR}"
echo "=========================================="

# Function to get model parameters for each size
get_model_params() {
    local size=$1
    case $size in
        "0.5B") echo "518000000" ;;  # ~518M parameters
        "1.5B") echo "1500000000" ;; # ~1.5B parameters  
        "3B")   echo "3000000000" ;; # ~3B parameters
        *) echo "0" ;;
    esac
}

# Function to get batch size based on model size
get_batch_size() {
    local size=$1
    case $size in
        "0.5B") echo "8" ;;
        "1.5B") echo "4" ;;
        "3B")   echo "2" ;;
        *) echo "1" ;;
    esac
}

# Generate configuration for each model
generate_qwen_config() {
    local size=$1
    local batch_size=$2
    local model_params=$3
    local config_file="${OUTPUT_BASE_DIR}/configs/qwen2.5_${size}.sh"
    
    cat > "$config_file" << EOF
#!/bin/bash
# Qwen2.5 ${size} Configuration

export MODEL_TYPE="qwen2.5"
export MODEL_SIZE="${size}"
export MODEL_PARAMS="${model_params}"
export BATCH_SIZE=${batch_size}
export GLOBAL_BATCH_SIZE=\$((BATCH_SIZE * GPUS_PER_NODE))
export SEQ_LEN=${CONTEXT_LENGTH}
export TRAIN_TOKENS=${TRAIN_TOKENS}

# Model architecture settings based on size
EOF

    case $size in
        "0.5B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=24
export HIDDEN_SIZE=896
export NUM_ATTN_HEADS=14
export INTERMEDIATE_SIZE=4864
export NUM_KEY_VALUE_HEADS=2
EOF
            ;;
        "1.5B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=28
export HIDDEN_SIZE=1536
export NUM_ATTN_HEADS=12
export INTERMEDIATE_SIZE=8960
export NUM_KEY_VALUE_HEADS=2
EOF
            ;;
        "3B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=36
export HIDDEN_SIZE=2048
export NUM_ATTN_HEADS=16
export INTERMEDIATE_SIZE=11008
export NUM_KEY_VALUE_HEADS=2
EOF
            ;;
    esac

    cat >> "$config_file" << 'EOF'

# Training script
TRAINING_SCRIPT="${PRETRAIN_DIR}/Pai-Megatron-Patch/examples/qwen2/pretrain_qwen2_moe.py"
export EXPERIMENT_NAME="qwen2.5_${MODEL_SIZE}_fineweb"
EOF

    chmod +x "$config_file"
    echo "Generated Qwen2.5 ${size} configuration: $config_file"
}

generate_mamba_config() {
    local size=$1
    local batch_size=$2
    local model_params=$3
    local config_file="${OUTPUT_BASE_DIR}/configs/mamba_${size}.sh"
    
    cat > "$config_file" << EOF
#!/bin/bash
# Mamba ${size} Configuration

export MODEL_TYPE="mamba"
export MODEL_SIZE="${size}"
export MODEL_PARAMS="${model_params}"
export BATCH_SIZE=${batch_size}
export GLOBAL_BATCH_SIZE=\$((BATCH_SIZE * GPUS_PER_NODE))
export SEQ_LEN=${CONTEXT_LENGTH}
export TRAIN_TOKENS=${TRAIN_TOKENS}

# Mamba-specific settings
export D_MODEL=\$(python -c "
size='${size}'
if size == '0.5B':
    print(768)
elif size == '1.5B':
    print(1536)
elif size == '3B':
    print(2560)
")

export N_LAYER=\$(python -c "
size='${size}'
if size == '0.5B':
    print(24)
elif size == '1.5B':
    print(48)
elif size == '3B':
    print(64)
")

export D_STATE=16
export D_CONV=4
export EXPAND=2

# Training script - using custom Mamba training implementation
TRAINING_SCRIPT="${PRETRAIN_DIR}/mamba/train_mamba_fineweb.py"
export EXPERIMENT_NAME="mamba_\${MODEL_SIZE}_fineweb"
EOF

    chmod +x "$config_file"
    echo "Generated Mamba ${size} configuration: $config_file"
}

generate_pythia_config() {
    local size=$1
    local batch_size=$2
    local model_params=$3
    local config_file="${OUTPUT_BASE_DIR}/configs/pythia_${size}.sh"
    
    cat > "$config_file" << EOF
#!/bin/bash
# Pythia ${size} Configuration

export MODEL_TYPE="pythia"
export MODEL_SIZE="${size}"
export MODEL_PARAMS="${model_params}"
export BATCH_SIZE=${batch_size}
export GLOBAL_BATCH_SIZE=\$((BATCH_SIZE * GPUS_PER_NODE))
export SEQ_LEN=${CONTEXT_LENGTH}
export TRAIN_TOKENS=${TRAIN_TOKENS}

# Pythia architecture settings
EOF

    case $size in
        "0.5B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=24
export HIDDEN_SIZE=1024
export NUM_ATTN_HEADS=16
export INTERMEDIATE_SIZE=4096
EOF
            ;;
        "1.5B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=32
export HIDDEN_SIZE=2048
export NUM_ATTN_HEADS=16
export INTERMEDIATE_SIZE=8192
EOF
            ;;
        "3B")
            cat >> "$config_file" << 'EOF'
export NUM_LAYERS=32
export HIDDEN_SIZE=2560
export NUM_ATTN_HEADS=32
export INTERMEDIATE_SIZE=10240
EOF
            ;;
    esac

    cat >> "$config_file" << 'EOF'

# Training script - using GPT-NeoX style training
TRAINING_SCRIPT="${PRETRAIN_DIR}/pythia/train_pythia_fineweb.py"
export EXPERIMENT_NAME="pythia_${MODEL_SIZE}_fineweb"
EOF

    chmod +x "$config_file"
    echo "Generated Pythia ${size} configuration: $config_file"
}

generate_rwkv_config() {
    local size=$1
    local batch_size=$2
    local model_params=$3
    local config_file="${OUTPUT_BASE_DIR}/configs/rwkv_${size}.sh"
    
    cat > "$config_file" << EOF
#!/bin/bash
# RWKV ${size} Configuration

export MODEL_TYPE="rwkv"
export MODEL_SIZE="${size}"
export MODEL_PARAMS="${model_params}"
export BATCH_SIZE=${batch_size}
export GLOBAL_BATCH_SIZE=\$((BATCH_SIZE * GPUS_PER_NODE))
export SEQ_LEN=${CONTEXT_LENGTH}
export TRAIN_TOKENS=${TRAIN_TOKENS}

# RWKV architecture settings
EOF

    case $size in
        "0.5B")
            cat >> "$config_file" << 'EOF'
export N_LAYER=24
export N_EMBD=1024
export CTX_LEN=8192
EOF
            ;;
        "1.5B")
            cat >> "$config_file" << 'EOF'
export N_LAYER=32
export N_EMBD=2048
export CTX_LEN=8192
EOF
            ;;
        "3B")
            cat >> "$config_file" << 'EOF'
export N_LAYER=40
export N_EMBD=2560
export CTX_LEN=8192
EOF
            ;;
    esac

    cat >> "$config_file" << 'EOF'

# RWKV-specific settings
export N_HEAD=-1  # RWKV doesn't use multi-head attention
export HEAD_SIZE_A=64
export HEAD_SIZE_DIVISOR=8

# Training script
TRAINING_SCRIPT="${PRETRAIN_DIR}/RWKV-LM/RWKV-v7/train.py"
export EXPERIMENT_NAME="rwkv_${MODEL_SIZE}_fineweb"
EOF

    chmod +x "$config_file"
    echo "Generated RWKV ${size} configuration: $config_file"
}

# Generate all configurations
echo "Generating model configurations..."
for model in "${MODELS[@]}"; do
    for size in "${SIZES[@]}"; do
        model_params=$(get_model_params "$size")
        batch_size=$(get_batch_size "$size")
        
        case $model in
            "qwen2.5") generate_qwen_config "$size" "$batch_size" "$model_params" ;;
            "mamba")   generate_mamba_config "$size" "$batch_size" "$model_params" ;;
            "pythia")  generate_pythia_config "$size" "$batch_size" "$model_params" ;;
            "rwkv")    generate_rwkv_config "$size" "$batch_size" "$model_params" ;;
        esac
    done
done

echo "=========================================="
echo "Configuration generation completed!"
echo "Generated configurations in: ${OUTPUT_BASE_DIR}/configs/"
echo ""
echo "Next steps:"
echo "1. Ensure datasets are prepared: cd ${SCRIPT_DIR} && ./prepare_fineweb_dataset.sh"
echo "2. Run individual experiments:"
echo "   cd ${OUTPUT_BASE_DIR} && bash configs/qwen2.5_0.5B.sh"
echo "3. Or run all experiments: bash run_all_attention_free_experiments.sh"