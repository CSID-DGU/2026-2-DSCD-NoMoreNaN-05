#!/bin/bash

set -e
GPUS="${GPUS:-0,1,2,3}"
PP="${PP:-1}"
N=$(echo "$GPUS" | tr ',' '\n' | wc -l)
TP=$((N / PP))

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate truead-vllm

echo "GPUs=$GPUS  TP=$TP  PP=$PP"
CUDA_VISIBLE_DEVICES="$GPUS" vllm serve openai/gpt-oss-120b \
    --tensor-parallel-size "$TP" \
    --pipeline-parallel-size "$PP" \
    --gpu-memory-utilization "${MEM_UTIL:-0.85}" \
    --max-model-len "${MAX_LEN:-8192}" \
    --port "${PORT:-8000}"
