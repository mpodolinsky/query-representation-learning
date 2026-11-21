#!/bin/bash
# Fetch sentence-transformers/all-MiniLM-L6-v2 (about 90 MB) into the cache folder learned.features.SentenceFeatures
# uses, so the compute node can run offline. Login node, once. Also warms tiktoken's cl100k table.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY="${PY:-$SCRATCH/envs/qrl/bin/python}"
CACHE="${CACHE:-results/learned/cache}"
mkdir -p "$CACHE/encoder"
$PY - <<PYEOF
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder="$CACHE/encoder")
print("encoder ok:", m.encode(["hello"]).shape)
import os, tiktoken
os.environ.setdefault("TIKTOKEN_CACHE_DIR", os.path.expandvars("$SCRATCH/tiktoken_cache"))
print("tiktoken ok:", len(tiktoken.get_encoding("cl100k_base").encode("hello world")))
PYEOF
echo "cached under $CACHE/encoder"
