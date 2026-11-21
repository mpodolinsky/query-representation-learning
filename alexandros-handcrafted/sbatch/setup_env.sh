#!/bin/bash
# Create $SCRATCH/envs/qrl: an aarch64 python with everything the unified comparison needs (run once, login node).
# CUDA torch for the GPU encoder step; CPU-only torch also works (the MLPs are tiny): set TORCH_INDEX accordingly.
set -euo pipefail
ENV="${ENV:-$SCRATCH/envs/qrl}"
PYTHON="${PYTHON:-$HOME/.local/bin/python3.11}"     # any python >= 3.10
TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cu130}"   # or .../whl/cpu
"$PYTHON" -m venv "$ENV"
"$ENV/bin/python" -m pip install --upgrade pip
"$ENV/bin/python" -m pip install --index-url "$TORCH_INDEX" torch
"$ENV/bin/python" -m pip install "numpy>=2" scikit-learn scipy threadpoolctl pandas pyarrow matplotlib tiktoken pytest sentence-transformers
"$ENV/bin/python" -c "import torch, sentence_transformers; print('ok', torch.__version__, torch.cuda.is_available())"
echo "env: $ENV/bin/python"
