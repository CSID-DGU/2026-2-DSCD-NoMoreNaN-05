#!/bin/bash

set -e
source "$(conda info --base)/etc/profile.d/conda.sh"

make_env() {
    if conda env list | grep -q "^$1 "; then
        echo "  $1 이미 존재 - 스킵"
    else
        conda create -n "$1" python=3.12 -y
    fi
}

make_env truead
conda activate truead
conda install -y -c conda-forge ffmpeg
pip install -U torch --index-url https://download.pytorch.org/whl/cu128
pip install -U qwen-asr openai
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"
ffmpeg -version | head -1
conda deactivate

make_env truead-vllm
conda activate truead-vllm
pip install -U vllm
python -c "import vllm; print('vllm', vllm.__version__)"
conda deactivate
