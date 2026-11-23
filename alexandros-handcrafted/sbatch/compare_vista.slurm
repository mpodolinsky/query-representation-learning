#!/bin/bash
#SBATCH -J qrl_compare
#SBATCH -p gh                      # TACC Vista: GH200 node (72 Grace cores); gh-dev for a 2 h test
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00
#SBATCH -A BCS25105
#SBATCH -o results_compare/logs/%x-%j.out
#SBATCH -e results_compare/logs/%x-%j.err
# The unified comparison of every query representation (alexandros-handcrafted/compare_representations.py).
# Submit from the repo root:  mkdir -p results_compare/logs && sbatch alexandros-handcrafted/sbatch/compare_vista.slurm
# Resubmit to resume (finished shards are skipped). Steps: 1) sentence vectors on the GPU, once; 2) six CPU processes
# (benchmark x split), 12 BLAS threads each, that train the MLPs and run the harness; 3) views, paired tests, report.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Environment: a python with numpy>=2, scikit-learn, pandas, pyarrow, matplotlib, tiktoken, torch, sentence-transformers
# (alexandros-handcrafted/sbatch/setup_env.sh creates $SCRATCH/envs/qrl with CUDA torch). The encoder must be on disk:
# alexandros-handcrafted/sbatch/download_encoder.sh (login node, needs the network) puts it in results/learned/cache/encoder.
PY="${PY:-$SCRATCH/envs/qrl/bin/python}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false TIKTOKEN_CACHE_DIR="${TIKTOKEN_CACHE_DIR:-$SCRATCH/tiktoken_cache}"
EXTRA="${EXTRA:-}"                                   # extra compare_representations.py arguments, e.g. "--seen-only"
OUT="${OUT:-results_compare}"                        # results folder; a run with another protocol needs its own, e.g.
ANALYSIS="${ANALYSIS:-alexandros-handcrafted/analysis_compare}"   # OUT=results_compare_k200 EXTRA="--k-grid 5 10 20 50 100 200"
mkdir -p "$OUT/logs"                                  # ANALYSIS=alexandros-handcrafted/analysis_compare_k200

echo "== $(date) job $SLURM_JOB_ID on $(hostname)"
$PY -c "import torch, sentence_transformers, sklearn, numpy; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'numpy', numpy.__version__)"

echo "== 1/3 sentence vectors (GPU)"
$PY alexandros-handcrafted/compare_representations.py --encode-only --device cuda --batch-size 256 --output "$OUT"

echo "== 2/3 the grid: six processes"
PY="$PY" THREADS=12 OUT="$OUT" bash alexandros-handcrafted/run_compare_all.sh $EXTRA
sleep 30
while pgrep -f "compare_representations.py --benchmarks" > /dev/null; do
    sleep 120
    $PY alexandros-handcrafted/compare_representations.py --dry-run --encoder stub --output "$OUT" $EXTRA 2>/dev/null | grep "shards done" || true
done
echo "== grid finished at $(date)"

echo "== 3/3 views, paired tests, report"
$PY alexandros-handcrafted/embedding_views.py --embeddings "$OUT/embeddings" --out "$ANALYSIS" || echo "views failed (rc=$?)"
OMP_NUM_THREADS=1 $PY alexandros-handcrafted/paired_tests.py --compare-root "$OUT" --reference handcrafted --n-probes 5 50 500 --workers 48 --out "$ANALYSIS" || echo "paired tests failed (rc=$?)"
$PY alexandros-handcrafted/k_unseen_check.py --out "$ANALYSIS" || echo "k check failed (rc=$?)"
$PY alexandros-handcrafted/build_report.py --unified "$OUT/metrics.csv" --analysis "$ANALYSIS"
echo "== $(date) done"
