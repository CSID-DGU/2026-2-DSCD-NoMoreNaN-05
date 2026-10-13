#!/bin/bash
# conda env 3개를 만든다. 이미 있으면 생성은 건너뛰고 패키지만 맞춘다.
#   truead        audio · alignment  (audio/requirements.txt. qwen-asr가 transformers==4.57.6을 고정)
#   truead-visual visual             (visual/requirements.txt. Qwen3.5 · PaddleOCR-VL이 transformers>=5.3 필요)
#   truead-vllm   gpt-oss-120b 서버  (requirements-vllm.txt, serve_llm.sh와 같이 둠)
# 세 개로 나누는 이유: transformers 버전이 서로 맞지 않아 한 환경에 못 넣는다.
# 그 뒤 Qwen3.5-122B용 llama.cpp를 빌드하고 GGUF(72GB)를 받는다 (serve_vlm.sh가 씀).

set -e
cd "$(dirname "$0")"
source "$(conda info --base)/etc/profile.d/conda.sh"

make_env() {
    if conda env list | grep -q "^$1 "; then
        echo "  $1 이미 존재 - 생성 스킵"
    else
        conda create -n "$1" python=3.12 -y
    fi
}

make_env truead
conda activate truead
conda install -y -c conda-forge ffmpeg
pip install -U torch --index-url https://download.pytorch.org/whl/cu128
pip install -U -r audio/requirements.txt
python -c "import torch; print('[truead] torch', torch.__version__, 'cuda', torch.cuda.is_available())"
ffmpeg -version | head -1
conda deactivate

make_env truead-visual
conda activate truead-visual
conda install -y -c conda-forge ffmpeg
pip install -U torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -U -r visual/requirements.txt
python -c "import torch, transformers; print('[truead-visual] torch', torch.__version__, 'cuda', torch.cuda.is_available(), '| transformers', transformers.__version__)"
conda deactivate

make_env truead-vllm
conda activate truead-vllm
pip install -U -r requirements-vllm.txt
python -c "import vllm; print('[truead-vllm] vllm', vllm.__version__)"
conda deactivate