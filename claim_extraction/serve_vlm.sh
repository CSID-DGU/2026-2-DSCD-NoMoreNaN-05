#!/bin/bash
# Qwen3.5-122B-A10B GGUF를 llama-server로 띄운다 (GPU 1장 + 전문가 일부 CPU).
#   GPUS=3 [PORT=8002] [N_CPU_MOE=28] [THREADS=16] [CTX=8192] bash serve_vlm.sh
# N_CPU_MOE: 전문가를 CPU에 두는 층 수(0~48). 작을수록 GPU를 많이 쓰고 빠르다. 전체 main.py가 GPU 여유로 계산해 넘긴다.
set -e
LLAMA_SERVER="${LLAMA_SERVER:-$HOME/llama.cpp/build/bin/llama-server}"
GGUF_DIR="${GGUF_DIR:-$HOME/hf_cache/gguf/Qwen3.5-122B-A10B-GGUF}"
MODEL="$GGUF_DIR/UD-Q4_K_XL/Qwen3.5-122B-A10B-UD-Q4_K_XL-00001-of-00003.gguf"
MMPROJ="$GGUF_DIR/mmproj-F16.gguf"

echo "GPUS=${GPUS:?GPUS 필요}  PORT=${PORT:-8002}  N_CPU_MOE=${N_CPU_MOE:-28}  THREADS=${THREADS:-16}"
CUDA_VISIBLE_DEVICES="$GPUS" "$LLAMA_SERVER" \
    -m "$MODEL" --mmproj "$MMPROJ" \
    -ngl 99 --n-cpu-moe "${N_CPU_MOE:-28}" \
    -c "${CTX:-8192}" -t "${THREADS:-16}" \
    --host 127.0.0.1 --port "${PORT:-8002}"
