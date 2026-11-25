#!/bin/bash
# gpt-oss-120b GGUF(UD-Q4_K_XL)를 llama-server로 띄운다 (GPU 1장 + 전문가 일부 CPU).
#   GPUS=0 [PORT=8000] [N_CPU_MOE=20] [THREADS=16] [CTX=32768] bash serve_llm.sh
# N_CPU_MOE: 전문가를 CPU에 두는 층 수(0~36). 작을수록 GPU를 많이 쓰고 빠르다. 전체 main.py가 GPU 여유로 계산해 넘긴다.
set -e
source "$(dirname "$0")/../../paths.sh"
GGUF_DIR="${GGUF_DIR:-$GGUF_ROOT/gpt-oss-120b-GGUF}"
MODEL="$GGUF_DIR/UD-Q4_K_XL/gpt-oss-120b-UD-Q4_K_XL-00001-of-00002.gguf"

echo "GPUS=${GPUS:?GPUS 필요}  PORT=${PORT:-8000}  N_CPU_MOE=${N_CPU_MOE:-20}  THREADS=${THREADS:-16}  CTX=${CTX:-32768}"
CUDA_VISIBLE_DEVICES="$GPUS" "$LLAMA_SERVER" \
    -m "$MODEL" -a gpt-oss-120b \
    -ngl 99 --n-cpu-moe "${N_CPU_MOE:-20}" \
    -c "${CTX:-32768}" -t "${THREADS:-16}" \
    --host 127.0.0.1 --port "${PORT:-8000}"
