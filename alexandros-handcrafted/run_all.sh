#!/usr/bin/env bash
# Launch the seen + unseen runs of both benchmarks and all three splits as six detached processes (one per
# benchmark and split; they survive the end of the login session), logs in results/logs/<benchmark>_split<s>.log.
#   PY=/path/to/python bash run_all.sh                       # everything, defaults of run_handcrafted.py
#   PY=... bash run_all.sh --skip-unseen                     # the seen setting only
#   PY=... THREADS=8 bash run_all.sh --probe-seeds 2         # any run_handcrafted.py argument is passed through
# Commit first: the harness writes the git commit (-dirty if the tree has changes) into every results folder.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-python}
THREADS=${THREADS:-5}            # BLAS threads per process (6 processes on a 32-core node)
mkdir -p "$HERE/../results/logs"
for b in llmrouterbench routerbench; do
  for s in 0 1 2; do
    log="$HERE/../results/logs/${b}_split${s}.log"
    OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS \
      setsid nohup "$PY" -s "$HERE/run_handcrafted.py" --benchmarks "$b" --split-seeds "$s" "$@" > "$log" 2>&1 < /dev/null &
    echo "$b split $s -> $log (pid $!)"
  done
done
