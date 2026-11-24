#!/bin/bash
# Create $SCRATCH/envs/qrl: an aarch64 python with everything the unified comparison needs (run once, login node).
# Uses uv (the repo's own .venv was made the same way): `python -m venv` of the uv-managed interpreter in
# ~/.local/bin fails with "Could not find platform independent libraries" / "No module named 'encodings'".
# CUDA torch for the GPU encoder step; CPU-only torch also works (the MLPs are tiny): set TORCH_INDEX accordingly.
set -euo pipefail
ENV="${ENV:-$SCRATCH/envs/qrl}"
PYTHON="${PYTHON:-$HOME/.local/bin/python3.11}"     # any python >= 3.10 that uv can use
UV="${UV:-/scratch/11034/atzanakak/p2-cism/bin/uv}"
TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cu130}"   # or .../whl/cpu
if [ ! -x "$UV" ]; then
    command -v uv > /dev/null || { echo "uv not found: set UV=/path/to/uv (or: pip install uv)"; exit 2; }
    UV=$(command -v uv)
fi
if [ -e "$ENV" ]; then echo "removing the previous $ENV"; rm -rf "$ENV"; fi
"$UV" venv --python "$PYTHON" "$ENV"
"$UV" pip install --python "$ENV/bin/python" --index-url "$TORCH_INDEX" torch
"$UV" pip install --python "$ENV/bin/python" "numpy>=2" scikit-learn scipy threadpoolctl pandas pyarrow matplotlib tiktoken pytest sentence-transformers markdown
"$ENV/bin/python" -c "import torch, sentence_transformers; print('ok', torch.__version__, 'cuda build', torch.version.cuda, 'cuda available here', torch.cuda.is_available())"
echo "env: $ENV/bin/python"
