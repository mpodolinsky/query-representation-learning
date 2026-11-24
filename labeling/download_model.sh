#!/usr/bin/env bash
# Download Qwen/Qwen3-32B (bf16 safetensors, ~62 GB) to a local directory. Run on a LOGIN node (compute nodes have
# no internet). Needs the huggingface_hub CLI (`hf` or `huggingface-cli`): pip install -U huggingface_hub
#   bash labeling/download_model.sh [$SCRATCH/models/Qwen3-32B]
# A copy of this exact model (revision 9216db57) is already on this account from October 2026; to reuse it instead
# of downloading 62 GB again:
#   mkdir -p $SCRATCH/models && ln -s /scratch/11034/atzanakak/tmlr/hf_home/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137 $SCRATCH/models/Qwen3-32B
set -euo pipefail
REPO_ID="${REPO_ID:-Qwen/Qwen3-32B}"
REVISION="${REVISION:-}"          # e.g. 9216db5781bf21249d130ec9da846c4624c16137 to pin the snapshot already used here
DEST="${1:-$SCRATCH/models/Qwen3-32B}"

if [ -f "$DEST/config.json" ] && ls "$DEST"/*.safetensors >/dev/null 2>&1; then
    echo "already present: $DEST"; exit 0
fi
mkdir -p "$(dirname "$DEST")"
avail_gb=$(df -BG "$(dirname "$DEST")" | awk 'NR==2 {gsub("G","",$4); print $4}')
echo "destination $DEST (free: ${avail_gb} GB, need about 65 GB)"

if command -v hf >/dev/null 2>&1; then CLI="hf download";
elif command -v huggingface-cli >/dev/null 2>&1; then CLI="huggingface-cli download";
else
    echo "no 'hf' / 'huggingface-cli' on PATH. Options:"
    echo "  pip install -U huggingface_hub        (any python env)"
    echo "  /scratch/11034/atzanakak/biomni_vista/envs/biotaskbench/bin/hf download ...   (existing env)"
    exit 1
fi
export HF_HUB_ENABLE_HF_TRANSFER=0
$CLI "$REPO_ID" --local-dir "$DEST" ${REVISION:+--revision "$REVISION"}
echo "== done"; ls "$DEST"; du -sh "$DEST"
