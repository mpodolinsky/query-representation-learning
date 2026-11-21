#!/usr/bin/env bash
# Launch the unified comparison (compare_representations.py) as six detached processes, one per benchmark and split,
# sharing one output folder (shards are per unit, so the processes never collide). Logs in results_compare/logs/.
#   PY=/path/to/python bash run_compare_all.sh                      # defaults: all representations, all instances
#   PY=... THREADS=4 bash run_compare_all.sh --representations handcrafted frozen combined regression contrastive
#   PY=... bash run_compare_all.sh --seen-only                       # the final pool only (quick first look)
# Run `$PY compare_representations.py --encode-only` first so the sentence vectors are cached once, not six times.
# Resumable: relaunching skips finished shards. Commit first: the harness records the git commit in every folder.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-python}
THREADS=${THREADS:-4}
OUT=${OUT:-$HERE/../results_compare}
mkdir -p "$OUT/logs"
for b in llmrouterbench routerbench; do
  for s in 0 1 2; do
    log="$OUT/logs/${b}_split${s}.log"
    OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS \
      setsid nohup "$PY" -s "$HERE/compare_representations.py" --benchmarks "$b" --split-seeds "$s" --threads "$THREADS" \
      --output "$OUT" "$@" > "$log" 2>&1 < /dev/null &
    echo "$b split $s -> $log (pid $!)"
  done
done
