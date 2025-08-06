#!/bin/bash

# EfficientLLM Benchmark Configuration Generator
# This script generates configurations for all attention mechanism and positional encoding variants

# Base directory for configurations
CONFIG_DIR="/work/nvme/bemy/zyuan2/code/efficientllm/pretrain/Pai-Megatron-Patch/examples/efficientllm_benchmark"
mkdir -p "$CONFIG_DIR"/{attention_variants,positional_encoding_variants,moe_variants}

# Base configuration template function
generate_base_script() {
    local variant_type="$1"
    local variant_name="$2"
    local model_size="$3"
    local batch_size="$4"
    local attention_type="$5"
    local pos_encoding="$6"
    local moe_config="$7"
    
    cat > "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh" << EOF
#!/bin/bash
set -e

# EfficientLLM Benchmark: $variant_name - $model_size
ENV=\$1
CURRENT_DIR="\$( cd "\$( dirname "\$0" )" && pwd )"
MEGATRON_PATCH_PATH=\$( dirname \$( dirname \$( dirname \${CURRENT_DIR})))

# Source EfficientLLM configuration
source \${MEGATRON_PATCH_PATH}/megatron_patch/efficientllm_config.sh

export PYTHONPATH=\${MEGATRON_PATCH_PATH}:\${MEGATRON_PATCH_PATH}/backends/megatron/Megatron-LM-250328:\$PYTHONPATH
export CUDA_DEVICE_MAX_CONNECTIONS=1
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=true

# Environment setup
if [ -z \${MP_DATASET_TYPE} ];then
    MP_DATASET_TYPE="idxmap"
fi

if [ -z \${MP_AC_LAYERS} ];then
    MP_AC_LAYERS=1
fi

if [ \$ENV = dsw ]; then
    MASTER_ADDR=localhost
    MASTER_PORT=\$(shuf -n 1 -i 10000-65535)
    NNODES=1
    NODE_RANK=0
    GPUS_PER_NODE=\`python -c "import torch; print(torch.cuda.device_count())"\`
elif [ \$ENV = dlc ]; then
    NNODES=\${WORLD_SIZE}
    NODE_RANK=\${RANK}
    GPUS_PER_NODE=\${KUBERNETES_CONTAINER_RESOURCE_GPU}
fi

DISTRIBUTED_ARGS="--nproc_per_node \$GPUS_PER_NODE --nnodes \$NNODES --node_rank \$NODE_RANK --master_addr \$MASTER_ADDR --master_port \$MASTER_PORT"

# Model configuration based on size
EOF

    # Add model size specific configurations
    case $model_size in
        "0.5B")
            cat >> "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh" << 'EOF'
NUM_LAYERS=24
HIDDEN_SIZE=896
NUM_ATTN_HEADS=14
INTERMEDIATE_SIZE=4864
NUM_KEY_VALUE_HEADS=2
MAX_POSITION_EMBEDDINGS=32768
EXTRA_VOCAB_SIZE=293
RMS_NORM_EPS=1e-6
EOF
            ;;
        "1.5B")
            cat >> "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh" << 'EOF'
NUM_LAYERS=28
HIDDEN_SIZE=1536
NUM_ATTN_HEADS=12
INTERMEDIATE_SIZE=8960
NUM_KEY_VALUE_HEADS=2
MAX_POSITION_EMBEDDINGS=32768
EXTRA_VOCAB_SIZE=293
RMS_NORM_EPS=1e-6
EOF
            ;;
        "3B")
            cat >> "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh" << 'EOF'
NUM_LAYERS=36
HIDDEN_SIZE=2048
NUM_ATTN_HEADS=16
INTERMEDIATE_SIZE=11008
NUM_KEY_VALUE_HEADS=2
MAX_POSITION_EMBEDDINGS=32768
EXTRA_VOCAB_SIZE=293
RMS_NORM_EPS=1e-6
EOF
            ;;
    esac

    # Add attention mechanism specific configuration
    cat >> "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh" << EOF

# Attention mechanism: $attention_type
gqa_options=""
if [ "$attention_type" = "mqa" ]; then
    # Multi-Query Attention: single K/V head
    NUM_KEY_VALUE_HEADS=1
    gqa_options=" \\
        --group-query-attention \\
        --num-query-groups 1"
elif [ "$attention_type" = "gqa" ]; then
    # Grouped-Query Attention: default Qwen2.5 setting
    gqa_options=" \\
        --group-query-attention \\
        --num-query-groups \${NUM_KEY_VALUE_HEADS}"
elif [ "$attention_type" = "mla" ]; then
    # Multi-Head Latent Attention
    gqa_options=" \\
        --use-mla-attention \\
        --mla-latent-dim \$((HIDDEN_SIZE / 8)) \\
        --mla-qk-head-dim 128"
elif [ "$attention_type" = "nsa" ]; then
    # Native Sparse Attention
    gqa_options=" \\
        --use-nsa-attention \\
        --nsa-sliding-window-size 128 \\
        --nsa-compress-block-size 64 \\
        --nsa-num-selected-blocks 4"
fi

# Positional encoding: $pos_encoding
pos_encoding_options=""
if [ "$pos_encoding" = "absolute" ]; then
    pos_encoding_options=" \\
        --position-embedding-type absolute"
elif [ "$pos_encoding" = "learnable_absolute" ]; then
    pos_encoding_options=" \\
        --position-embedding-type learnable_absolute"
elif [ "$pos_encoding" = "relative" ]; then
    pos_encoding_options=" \\
        --position-embedding-type relative"
elif [ "$pos_encoding" = "none" ]; then
    pos_encoding_options=" \\
        --position-embedding-type none"
else
    # Default: RoPE
    pos_encoding_options=" \\
        --position-embedding-type rope \\
        --use-rotary-position-embeddings \\
        --rotary-percent 1.0 \\
        --rotary-base 1000000"
fi

# MoE configuration
moe_options=""
$moe_config

# Training configuration
BATCH_SIZE=$batch_size
GLOBAL_BATCH_SIZE=\$((BATCH_SIZE * GPUS_PER_NODE))
LR=1.0e-4
MIN_LR=1.0e-5
SEQ_LEN=2048
PAD_LEN=2048
PR=bf16
TP=1
PP=1
CP=1
SP=false
DO=false
FL=false
SFT=false
AC=full
OPTIMIZER_OFFLOAD=false
SAVE_INTERVAL=500
TRAIN_TOKENS=100000
WARMUP_TOKENS=10000

# Dataset paths - HuggingFace fine-webedu v1.2.0 sample-350BT
# First run prepare_fineweb_dataset.sh to download and process the dataset
DATASET_BASE_DIR="\${MEGATRON_PATCH_PATH}/data/fineweb_edu"
DATASET_PATH="\${DATASET_PATH:-\${DATASET_BASE_DIR}/processed/fineweb_edu_train.jsonl}"
VALID_DATASET_PATH="\${VALID_DATASET_PATH:-\${DATASET_BASE_DIR}/processed/fineweb_edu_train.jsonl}"
DATASET_CONFIG="sample-350BT"
DATASET_VERSION="1.2.0"

# Check if dataset exists
if [ ! -f "\${DATASET_PATH}" ]; then
    echo "Dataset not found at: \${DATASET_PATH}"
    echo "Please run prepare_fineweb_dataset.sh first to download and process the dataset"
    echo "Usage: cd \${MEGATRON_PATCH_PATH}/scripts && ./prepare_fineweb_dataset.sh"
    exit 1
fi
PRETRAIN_CHECKPOINT_PATH="\${PRETRAIN_CHECKPOINT_PATH:-none}"
OUTPUT_BASEPATH="\${OUTPUT_BASEPATH:-./output/efficientllm_benchmark/${variant_name}_${model_size}}"

# Create output directories
mkdir -p "\${OUTPUT_BASEPATH}/tensorboard/"
mkdir -p "\${OUTPUT_BASEPATH}/checkpoint/"
mkdir -p "\${OUTPUT_BASEPATH}/log/"

current_time=\$(date "+%Y.%m.%d-%H.%M.%S")
TENSORBOARD_DIR="\${OUTPUT_BASEPATH}/tensorboard/${variant_name}_${model_size}_\${current_time}"
mkdir -p \${TENSORBOARD_DIR}
SAVED_PRETRAIN_CHECKPOINT_PATH="\${OUTPUT_BASEPATH}/checkpoint/${variant_name}_${model_size}"

PREFIX="efficientllm-${variant_name}-${model_size}-lr-\${LR}-bs-\${BATCH_SIZE}-gbs-\${GLOBAL_BATCH_SIZE}-seqlen-\${SEQ_LEN}"
NAME="\${PREFIX}-pr-\${PR}-tp-\${TP}-pp-\${PP}-cp-\${CP}-ac-\${AC}-do-\${DO}-sp-\${SP}"

# Common training options
megatron_options="  \\
        --save \${SAVED_PRETRAIN_CHECKPOINT_PATH} \\
        --lr \${LR} \\
        --min-lr \${MIN_LR} \\
        --lr-decay-style cosine \\
        --weight-decay 0.1 \\
        --adam-beta1 0.9 \\
        --adam-beta2 0.95 \\
        --clip-grad 1.0 \\
        --init-method-std 0.008 \\
        --attention-dropout 0.0 \\
        --hidden-dropout 0.0 \\
        --lr-decay-iters \$((TRAIN_TOKENS / GLOBAL_BATCH_SIZE / SEQ_LEN)) \\
        --lr-warmup-iters \$((WARMUP_TOKENS / GLOBAL_BATCH_SIZE / SEQ_LEN)) \\
        --train-iters \$((TRAIN_TOKENS / GLOBAL_BATCH_SIZE / SEQ_LEN)) \\
        --micro-batch-size \${BATCH_SIZE} \\
        --global-batch-size \${GLOBAL_BATCH_SIZE} \\
        --num-layers \${NUM_LAYERS} \\
        --hidden-size \${HIDDEN_SIZE} \\
        --num-attention-heads \${NUM_ATTN_HEADS} \\
        --ffn-hidden-size \${INTERMEDIATE_SIZE} \\
        --seq-length \${SEQ_LEN} \\
        --max-position-embeddings \${MAX_POSITION_EMBEDDINGS} \\
        --max-padding-length \${PAD_LEN} \\
        --log-interval 1 \\
        --log-throughput \\
        --eval-interval 1000 \\
        --eval-iters 10 \\
        --save-interval \${SAVE_INTERVAL} \\
        --tensorboard-queue-size 1 \\
        --tensorboard-dir \${TENSORBOARD_DIR} \\
        --log-timers-to-tensorboard \\
        --log-validation-ppl-to-tensorboard \\
        --tensor-model-parallel-size \${TP} \\
        --pipeline-model-parallel-size \${PP} \\
        --context-parallel-size \${CP} \\
        --no-load-optim \\
        --no-load-rng \\
        --num-workers 8 \\
        --extra-vocab-size \${EXTRA_VOCAB_SIZE} \\
        --patch-tokenizer-type Qwen2Tokenizer \\
        --swiglu \\
        --normalization RMSNorm \\
        --norm-epsilon \${RMS_NORM_EPS} \\
        --disable-bias-linear \\
        --add-qkv-bias \\
        --rotary-seq-len-interpolation-factor 1 \\
        --no-save-optim \\
        --data-path \${DATASET_PATH} \\
        --split 99,1,0 \\
        --dataset JSON \\
        --json-keys text \\
        --bf16"

# Run command
run_cmd="torchrun \$DISTRIBUTED_ARGS ../qwen2/pretrain_qwen2_moe.py \\
 \${megatron_options} \${gqa_options} \${pos_encoding_options} \${moe_options}"

echo "=========================================="
echo "EfficientLLM Benchmark: $variant_name - $model_size"
echo "=========================================="
echo "Attention: $attention_type"
echo "Positional Encoding: $pos_encoding"
echo "Output: \${OUTPUT_BASEPATH}"
echo "=========================================="

echo \${run_cmd}
eval \${run_cmd}
EOF

    chmod +x "$CONFIG_DIR/${variant_type}/run_${variant_name}_${model_size}.sh"
}

# Generate attention mechanism variants
echo "Generating attention mechanism configurations..."

# MQA variants
for size in "0.5B" "1.5B" "3B"; do
    case $size in
        "0.5B") batch_size=4 ;;
        "1.5B") batch_size=2 ;;
        "3B") batch_size=1 ;;
    esac
    generate_base_script "attention_variants" "mqa" "$size" "$batch_size" "mqa" "rope" ""
done

# GQA variants (default Qwen2.5)
for size in "0.5B" "1.5B" "3B"; do
    case $size in
        "0.5B") batch_size=4 ;;
        "1.5B") batch_size=2 ;;
        "3B") batch_size=1 ;;
    esac
    generate_base_script "attention_variants" "gqa" "$size" "$batch_size" "gqa" "rope" ""
done

# MLA variants
for size in "0.5B" "1.5B" "3B"; do
    case $size in
        "0.5B") batch_size=4 ;;
        "1.5B") batch_size=2 ;;
        "3B") batch_size=1 ;;
    esac
    generate_base_script "attention_variants" "mla" "$size" "$batch_size" "mla" "rope" ""
done

# NSA variants
for size in "0.5B" "1.5B" "3B"; do
    case $size in
        "0.5B") batch_size=4 ;;
        "1.5B") batch_size=2 ;;
        "3B") batch_size=1 ;;
    esac
    generate_base_script "attention_variants" "nsa" "$size" "$batch_size" "nsa" "rope" ""
done

# Generate positional encoding variants (using GQA as base attention)
echo "Generating positional encoding configurations..."

for encoding in "rope" "absolute" "learnable_absolute" "relative" "none"; do
    generate_base_script "positional_encoding_variants" "gqa_${encoding}" "1.5B" "2" "gqa" "$encoding" ""
done

# Generate MoE variants
echo "Generating MoE configurations..."

# Dense model baseline
generate_base_script "moe_variants" "dense" "1.5B" "2" "gqa" "rope" ""
generate_base_script "moe_variants" "dense" "3B" "1" "gqa" "rope" ""

# MoE models
moe_config_0_5B='
if [ "$variant_name" = "moe_0_5Bx8" ]; then
    moe_options=" \\
        --num-experts 8 \\
        --expert-model-parallel-size 1 \\
        --moe-router-topk 2 \\
        --moe-aux-loss-coeff 0.01"
fi'

moe_config_1_5B='
if [ "$variant_name" = "moe_1_5Bx8" ]; then
    moe_options=" \\
        --num-experts 8 \\
        --expert-model-parallel-size 1 \\
        --moe-router-topk 2 \\
        --moe-aux-loss-coeff 0.01"
fi'

generate_base_script "moe_variants" "moe_0_5Bx8" "0.5B" "4" "gqa" "rope" "$moe_config_0_5B"
generate_base_script "moe_variants" "moe_1_5Bx8" "1.5B" "2" "gqa" "rope" "$moe_config_1_5B"

echo "=========================================="
echo "Configuration generation completed!"
echo "=========================================="
echo "Generated configurations in: $CONFIG_DIR"
echo ""
echo "Attention Variants:"
echo "  - MQA (Multi-Query Attention): 0.5B, 1.5B, 3B"
echo "  - GQA (Grouped-Query Attention): 0.5B, 1.5B, 3B" 
echo "  - MLA (Multi-Head Latent Attention): 0.5B, 1.5B, 3B"
echo "  - NSA (Native Sparse Attention): 0.5B, 1.5B, 3B"
echo ""
echo "Positional Encoding Variants (1.5B model):"
echo "  - RoPE (Rotary Position Embedding)"
echo "  - Absolute Positional Encoding"
echo "  - Learnable Absolute Positional Encoding"
echo "  - Relative Positional Encoding"
echo "  - No Positional Encoding"
echo ""
echo "MoE Variants:"
echo "  - Dense: 1.5B, 3B"
echo "  - MoE: 0.5B×8, 1.5B×8"
echo ""
echo "Usage example:"
echo "  cd $CONFIG_DIR/attention_variants"
echo "  ./run_mqa_0.5B.sh dsw"