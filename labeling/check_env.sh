#!/usr/bin/env bash
# Print what the labeling job needs (run first on the gh-dev node): architecture, GPU, python, vLLM/torch versions,
# and whether the model directory is there. Exits 1 if the model directory has no config.json.
#   MODEL_DIR=$SCRATCH/models/Qwen3-32B PYTHON=/path/to/python bash labeling/check_env.sh
MODEL_DIR="${MODEL_DIR:-${1:-$SCRATCH/models/Qwen3-32B}}"
PYTHON="${PYTHON:-python}"

echo "== host";   hostname; uname -m; date
echo "== SLURM";  env | grep -E '^SLURM_(JOB_ID|JOB_PARTITION|JOB_END_TIME|JOB_NODELIST|JOB_ACCOUNT)=' || echo "(not inside a SLURM job)"
if [ -n "${SLURM_JOB_END_TIME:-}" ]; then echo "job ends in $(( (SLURM_JOB_END_TIME - $(date +%s)) / 60 )) min"; fi
echo "== GPU";    nvidia-smi 2>/dev/null || echo "nvidia-smi not found (no GPU here?)"
echo "== python"; command -v "${PYTHON%% *}" || echo "python not found: $PYTHON"; $PYTHON --version 2>&1
echo "== build tools on PATH (FlashInfer JIT)"; command -v ninja || echo "ninja NOT on PATH"; command -v nvcc || echo "nvcc not on PATH (fine if VLLM_USE_FLASHINFER_SAMPLER=0)"
$PYTHON - <<'PY'
import importlib, platform
print("platform", platform.machine(), "python", platform.python_version())
for m in ("torch", "vllm", "transformers", "xgrammar", "pandas", "pyarrow"):
    try:
        mod = importlib.import_module(m); print(f"{m:14s} {getattr(mod, '__version__', '?')}")
    except Exception as e:
        print(f"{m:14s} MISSING ({type(e).__name__}: {e})")
try:
    import torch
    ok = torch.cuda.is_available()
    print("torch.cuda.is_available", ok, "| torch cuda", torch.version.cuda,
          "| device", torch.cuda.get_device_name(0) if ok else "-",
          "| mem GB", round(torch.cuda.get_device_properties(0).total_memory / 2**30) if ok else "-")
except Exception as e:
    print("torch cuda check failed:", e)
PY
echo "== model dir: $MODEL_DIR"
if [ -f "$MODEL_DIR/config.json" ]; then
    n=$(ls "$MODEL_DIR"/*.safetensors 2>/dev/null | wc -l)
    echo "config.json found; $n safetensors shard(s); size $(du -shL "$MODEL_DIR" 2>/dev/null | cut -f1)"
    grep -E '"(model_type|torch_dtype|dtype|max_position_embeddings|num_hidden_layers)"' "$MODEL_DIR/config.json" | tr -d ' ,' | paste -sd' '
    [ -f "$MODEL_DIR/tokenizer.json" ] || echo "WARNING: no tokenizer.json in $MODEL_DIR"
    [ "$n" -gt 0 ] || { echo "ERROR: no safetensors weights in $MODEL_DIR"; exit 1; }
else
    echo "ERROR: $MODEL_DIR/config.json missing. Download on a login node: bash labeling/download_model.sh $MODEL_DIR"
    exit 1
fi
echo "== ok"
