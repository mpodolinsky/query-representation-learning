#!/bin/bash
#SBATCH -J label_tasks
#SBATCH -p gh-dev                  # TACC Vista GH200 dev queue: 1 Hopper GPU (96 GB) + aarch64 Grace CPU per node
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00                # gh-dev limit
#SBATCH -A TODO_ACCOUNT            # TODO: your allocation (sacctmgr show assoc user=$USER format=account)
#SBATCH -o labeling/logs/%x-%j.out
#SBATCH -e labeling/logs/%x-%j.err
# Submit from the repo root:  mkdir -p labeling/logs && sbatch labeling/sbatch/label_gh_dev.slurm
# Resume after a time-out: resubmit the same command; finished shards are skipped (labeling/README.md).

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

MODEL_DIR="${MODEL_DIR:-$SCRATCH/models/Qwen3-32B}"   # labeling/download_model.sh (login node) puts it here
OUT_DIR="${OUT_DIR:-labeling/out}"                    # shards + metadata; gitignored
SMOKE="${SMOKE:-1}"                                   # 0 to skip the 50-query smoke test (saves one model load)

# ---------------------------------------------------------------------------------------------------- environment
# TODO: pick ONE of the three options, fill it in, delete the others. All of them must give an aarch64 python with
# vLLM >= 0.10 (structured outputs), torch with CUDA, transformers, pandas, pyarrow. check_env.sh verifies that.
#
# (a) TACC apptainer + a vLLM container (NGC publishes aarch64 vLLM images; pull on a login node, it is ~20 GB):
#     module load tacc-apptainer
#     export APPTAINER_CACHEDIR=$SCRATCH/apptainer_cache APPTAINER_TMPDIR=$SCRATCH/apptainer_tmp
#     IMG=$SCRATCH/containers/vllm.sif        # apptainer pull $IMG docker://nvcr.io/nvidia/vllm:25.10-py3   (TODO: tag)
#     PYTHON="apptainer exec --nv --bind /scratch,/work,/home1 $IMG python"
#     (the NGC PyTorch image already on this account, /work/11034/atzanakak/vista/containers/pytorch_2505_py3_aarch64.sif,
#      has no vLLM; it would need `pip install --user vllm` inside, which is slower to get right than (b)/(c))
#
# (b) conda/venv with aarch64 wheels (TODO):
#     module load gcc/14.2.0 cuda/12.6          # see `module avail`; match the torch CUDA build you install
#     source $SCRATCH/envs/vllm/bin/activate     # python -m venv $SCRATCH/envs/vllm && pip install vllm pandas pyarrow
#     PYTHON=python                              # vLLM ships linux_aarch64 wheels (it pulls a matching torch)
#
# (c) reuse an existing environment on this account (python 3.12, aarch64, vLLM 0.27.1, torch 2.13.0+cu130,
#     transformers 5.15, xgrammar 0.2.3; the GH200 driver here reports CUDA 13.1, so cu130 wheels run):
#     PYTHON=/scratch/11034/atzanakak/biomni_vista/envs/biotaskbench/bin/python
#     (alternative: .../envs/rl_harness312/bin/python = vLLM 0.24.0, torch 2.11.0+cu130)
PYTHON="${PYTHON:-TODO_SET_PYTHON}"
# ---------------------------------------------------------------------------------------------------------------

if [ "$PYTHON" = "TODO_SET_PYTHON" ]; then echo "set PYTHON (environment option a/b/c) in $0"; exit 2; fi
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 VLLM_NO_USAGE_STATS=1 TOKENIZERS_PARALLELISM=false
export VLLM_CACHE_ROOT="${VLLM_CACHE_ROOT:-$SCRATCH/vllm_cache}"     # torch.compile / cudagraph cache, reused across jobs
export TMPDIR="${TMPDIR:-$SCRATCH/tmp}"; mkdir -p "$TMPDIR" labeling/logs

echo "== $(date) job $SLURM_JOB_ID on $(hostname), ends at $(date -d @"$SLURM_JOB_END_TIME")"
echo "== 1/4 check_env"
MODEL_DIR="$MODEL_DIR" PYTHON="$PYTHON" bash labeling/check_env.sh

if [ "$SMOKE" = "1" ]; then
    echo "== 2/4 smoke test: 50 random RouterBench queries -> $OUT_DIR/routerbench_limit50"
    $PYTHON labeling/label_tasks.py --benchmark routerbench --model "$MODEL_DIR" --out-dir "$OUT_DIR" --limit 50 \
        --dtype bfloat16 --tp 1 --gpu-memory-utilization 0.90 --max-model-len 4096
    $PYTHON - <<PY
import pandas as pd, glob
df = pd.concat(pd.read_parquet(p) for p in glob.glob("$OUT_DIR/routerbench_limit50/shard_*.parquet"))
print(df[["theme", "level1", "level2", "level3", "consistent"]].to_string())
print("consistent:", df.consistent.mean(), "parse errors:", (df.level3 == "PARSE_ERROR").sum())
PY
else
    echo "== 2/4 smoke test skipped (SMOKE=0)"
fi

echo "== 3/4 full run, both benchmarks (shards of 1000, resumable)"
rc=0
$PYTHON labeling/label_tasks.py --benchmark all --model "$MODEL_DIR" --out-dir "$OUT_DIR" \
    --shard-size 1000 --max-query-chars 3000 --dtype bfloat16 --tp 1 --gpu-memory-utilization 0.90 \
    --max-model-len 4096 --max-tokens 64 || rc=$?
if [ "$rc" = "3" ]; then echo "== time budget reached before the last shard; resubmit this job to resume"; exit 3; fi
[ "$rc" = "0" ] || { echo "== labeling failed (rc=$rc)"; exit "$rc"; }

echo "== 4/4 merge: task_labels.parquet + reports"
$PYTHON labeling/merge_labels.py --benchmark all --out-dir "$OUT_DIR"
echo "== $(date) done"
