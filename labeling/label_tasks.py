#!/usr/bin/env python
"""Offline task-type labeling of every query with a local LLM through vLLM (domain -> subdomain -> task).

    python labeling/label_tasks.py --benchmark all --model $SCRATCH/models/Qwen3-32B --out-dir labeling/out
    python labeling/label_tasks.py --benchmark all --model <path> --dry-run        # CPU: prompts + token stats only
    python labeling/label_tasks.py --benchmark routerbench --model <path> --limit 50   # smoke test (GPU)

Input: preproc/data/<benchmark>/queries.parquet (query_id, theme, subtask, query, prompt, n_chars). The model sees the
bare `query` (middle-truncated to --max-query-chars) plus `theme`/`subtask` as hints, and must answer with JSON
{"level1", "level2", "level3"} constrained to labeling/taxonomy.py by guided decoding.

Output: out_dir/<benchmark>/shard_XXXXX.parquet (shards of --shard-size rows in sorted query_id order, written as
.tmp + rename), out_dir/<benchmark>/metadata.json (model, config sha, taxonomy version, prompt hash, vLLM version,
args; a resume with different values is refused). Existing shards are skipped on start; no new shard is started when
less than --min-remaining-sec remain before $SLURM_JOB_END_TIME. Identical query strings are labeled once.
With --limit N the output folder is out_dir/<benchmark>_limitN so a smoke test never masks a full-run shard.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_DATA_ROOT = REPO / "preproc" / "data"
DEFAULT_OUT_DIR = HERE / "out"
BENCHMARKS = ("llmrouterbench", "routerbench")
OUTPUT_COLUMNS = ["query_id", "theme", "subtask", "level1", "level2", "level3", "consistent", "raw_output", "truncated"]
PARSE_ERROR = "PARSE_ERROR"
TRUNCATION_MARKER = "\n[... {n} characters omitted ...]\n"

# ------------------------------------------------------------------------------------------------------ prompt

SYSTEM_PROMPT = f"""You label user queries with a task type from a fixed taxonomy. For each query, return one JSON object
{{"level1": <domain>, "level2": <subdomain>, "level3": <specific task>}} and nothing else.

Rules:
1. level1 must be one of the domain names below, and level2 one of the subdomains listed under THAT domain.
2. Label what the query asks the responder to do. For a text task (summarize, classify, extract, translate, write,
   rewrite, role-play) use language_writing with the task as level2, whatever the topic of the text. For a question
   that needs knowledge of a field, use that field's domain.
3. Ignore answer-format boilerplate such as "Print only a single choice from A/B/C/D", "Answer:", option letters,
   or "please answer with the letter".
4. The hints (source dataset, dataset subcategory) are context. They are usually right but sometimes wrong (for
   example ArenaHard's "math" subcategory contains code-debugging prompts, and MMLU "miscellaneous" spans
   everything). Decide from the query text.
5. level3 is a short, specific, lower-case phrase of 2-5 words naming the task, e.g. "matrix multiplication",
   "shortest-path search", "drug side effect recall", "poem title identification", "fix matlab runtime error".
6. A query truncated in the middle is marked "[... N characters omitted ...]"; label it from what is visible.
7. If the query is in a language other than English, still label the task; use chinese_language only for tasks
   about the Chinese language or classical Chinese culture.

Taxonomy (level1: description, then its level2 list):
{taxonomy.taxonomy_text()}

Source datasets (what the theme hint refers to):
{taxonomy.glossary_text()}"""

USER_TEMPLATE = """Hints: this query comes from dataset "{theme}", labeled subcategory "{subtask}".

Query:
<<<
{query}
>>>"""


def prompt_hash() -> str:
    """sha256 over everything that shapes the prompt: system prompt, user template, schema, taxonomy version."""
    h = hashlib.sha256()
    for part in (SYSTEM_PROMPT, USER_TEMPLATE, json.dumps(taxonomy.json_schema(), sort_keys=True), taxonomy.VERSION):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:16]


def truncate_middle(text: str, max_chars: int) -> tuple[str, bool]:
    """Keep the head (60%) and the tail (40%) of a long text with a marker in between. Returns (text, truncated)."""
    text = str(text)
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    head = int(max_chars * 0.6)
    tail = max(0, max_chars - head)
    omitted = len(text) - head - tail
    marker = TRUNCATION_MARKER.format(n=omitted)
    return text[:head].rstrip() + marker + text[len(text) - tail:].lstrip(), True


def build_messages(query: str, theme: str, subtask: str, max_query_chars: int) -> tuple[list[dict], bool]:
    """Chat messages for one query (system + user). Returns (messages, truncated)."""
    q, truncated = truncate_middle(query, max_query_chars)
    user = USER_TEMPLATE.format(theme=theme, subtask=subtask, query=q)
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}], truncated


def fit_messages(query: str, theme: str, subtask: str, max_query_chars: int, labeler=None) -> tuple[list[dict], bool]:
    """build_messages, then shrink the query (x0.8 per step) until the rendered prompt fits the model's context.
    Uses `labeler.prompt_tokens(messages)` and `labeler.max_prompt_tokens` when the labeler provides them (vLLM);
    a labeler without them (tests, stubs) gets the plain character truncation. Returns (messages, truncated)."""
    msgs, truncated = build_messages(query, theme, subtask, max_query_chars)
    count = getattr(labeler, "prompt_tokens", None)
    limit = getattr(labeler, "max_prompt_tokens", None)
    if count is None or limit is None:
        return msgs, truncated
    chars = max_query_chars if max_query_chars > 0 else len(query)
    n = count(msgs)
    while n > limit and chars > 50:
        chars = int(chars * 0.8)
        msgs, truncated = build_messages(query, theme, subtask, chars)
        n = count(msgs)
    if n > limit:
        raise RuntimeError(f"prompt still {n} tokens > {limit} after shrinking the query to {chars} chars; raise --max-model-len")
    return msgs, truncated


# ------------------------------------------------------------------------------------------------ output parsing

@dataclass
class Label:
    level1: str
    level2: str
    level3: str
    consistent: bool
    raw_output: str
    truncated: bool = False


_JSON_RE = re.compile(r"\{.*\}", re.S)


def parse_output(raw: str) -> Label:
    """Parse the model's JSON. Unknown names fall back to `other`; a parse failure gives level3=PARSE_ERROR.
    `consistent` is True only when the JSON parsed and level2 belongs to level1."""
    raw = "" if raw is None else str(raw)
    obj = None
    try:
        obj = json.loads(raw)
    except Exception:
        m = _JSON_RE.search(raw)
        if m:
            try:
                obj = json.loads(m.group(0))
            except Exception:
                obj = None
    if not isinstance(obj, dict):
        return Label("other", "other", PARSE_ERROR, False, raw)
    l1 = obj.get("level1")
    l2 = obj.get("level2")
    l3 = obj.get("level3")
    l1 = l1 if l1 in taxonomy.DOMAINS else "other"
    l2 = l2 if l2 in taxonomy.LEVEL2_TO_LEVEL1 else "other"
    l3 = re.sub(r"\s+", " ", str(l3)).strip().lower()[: taxonomy.LEVEL3_MAX_CHARS] if isinstance(l3, str) and l3.strip() else ""
    return Label(l1, l2, l3, taxonomy.is_consistent(l1, l2), raw)


# ---------------------------------------------------------------------------------------------------- the model

class VllmLabeler:
    """vLLM wrapper: `label(list of message lists) -> list of raw output strings`. Imports vLLM lazily."""

    def __init__(self, model: str, dtype="bfloat16", tp=1, gpu_memory_utilization=0.90, max_model_len=4096,
                 max_tokens=64, seed=0):
        from vllm import LLM, SamplingParams
        self.llm = LLM(model=model, dtype=dtype, tensor_parallel_size=tp, gpu_memory_utilization=gpu_memory_utilization,
                       max_model_len=max_model_len, enable_prefix_caching=True, seed=seed, trust_remote_code=False)
        schema = taxonomy.json_schema()
        try:  # vLLM >= 0.10: structured_outputs; older: guided_decoding
            from vllm.sampling_params import StructuredOutputsParams
            self.sampling = SamplingParams(temperature=0.0, max_tokens=max_tokens,
                                           structured_outputs=StructuredOutputsParams(json=schema))
        except ImportError:
            from vllm.sampling_params import GuidedDecodingParams
            self.sampling = SamplingParams(temperature=0.0, max_tokens=max_tokens,
                                           guided_decoding=GuidedDecodingParams(json=schema))
        self.chat_template_kwargs = {"enable_thinking": False}  # Qwen3: no thinking block
        self.max_prompt_tokens = max_model_len - max_tokens
        self.tokenizer = self.llm.get_tokenizer()

    def prompt_tokens(self, messages: list[dict]) -> int:
        """Token length of the rendered chat prompt (used to shrink over-long queries before they reach the engine)."""
        try:
            s = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, **self.chat_template_kwargs)
        except TypeError:
            s = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        return len(self.tokenizer(s, add_special_tokens=False).input_ids)

    def label(self, messages_list: list[list[dict]]) -> list[str]:
        try:
            outs = self.llm.chat(messages_list, self.sampling, use_tqdm=True, chat_template_kwargs=self.chat_template_kwargs)
        except TypeError:  # very old vLLM without chat_template_kwargs
            outs = self.llm.chat(messages_list, self.sampling, use_tqdm=True)
        return [o.outputs[0].text for o in outs]


def vllm_version() -> str | None:
    try:
        import vllm
        return getattr(vllm, "__version__", "unknown")
    except Exception:
        return None


# ------------------------------------------------------------------------------------------- data, shards, resume

def load_queries(benchmark: str, data_root: Path = DEFAULT_DATA_ROOT) -> pd.DataFrame:
    path = Path(data_root) / benchmark / "queries.parquet"
    if not path.exists():
        raise SystemExit(f"{path} not found. Build it with `python preproc/build.py` (see preproc/README.md) or pass --data-root.")
    df = pd.read_parquet(path, columns=["query_id", "theme", "subtask", "query"])
    if not df.query_id.is_unique:
        raise SystemExit(f"{path}: query_id is not unique")
    return df


def select_rows(df: pd.DataFrame, limit: int | None, seed: int = 0) -> pd.DataFrame:
    """All rows in sorted query_id order; with a limit, a seeded random subset (so a smoke test spans themes)."""
    if limit is not None and limit < len(df):
        df = df.sample(n=limit, random_state=seed)
    return df.sort_values("query_id", kind="stable").reset_index(drop=True)


def plan_shards(df: pd.DataFrame, shard_size: int) -> list[tuple[int, pd.DataFrame]]:
    if shard_size <= 0:
        raise ValueError("shard_size must be positive")
    return [(i, df.iloc[s:s + shard_size]) for i, s in enumerate(range(0, len(df), shard_size))]


def shard_path(bench_dir: Path, i: int) -> Path:
    return Path(bench_dir) / f"shard_{i:05d}.parquet"


def write_atomic_parquet(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def existing_shards(bench_dir: Path) -> list[Path]:
    return sorted(Path(bench_dir).glob("shard_[0-9][0-9][0-9][0-9][0-9].parquet"))


def file_sha256(path: Path) -> str | None:
    p = Path(path)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


STRICT_METADATA_KEYS = ("model", "config_sha256", "taxonomy_version", "prompt_hash", "dtype", "max_query_chars",
                        "shard_size", "max_tokens", "max_model_len")


def build_metadata(model: str, dtype: str, max_query_chars: int, shard_size: int, max_tokens: int,
                   max_model_len: int, extra_args: dict | None = None) -> dict:
    model_path = Path(model)
    return {
        "model": str(model_path.resolve()) if model_path.exists() else str(model),
        "config_sha256": file_sha256(model_path / "config.json"),
        "taxonomy_version": taxonomy.VERSION,
        "prompt_hash": prompt_hash(),
        "vllm_version": vllm_version(),
        "dtype": dtype,
        "max_query_chars": int(max_query_chars),
        "shard_size": int(shard_size),
        "max_tokens": int(max_tokens),
        "max_model_len": int(max_model_len),
        "args": extra_args or {},
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def write_or_check_metadata(bench_dir: Path, meta: dict) -> None:
    """Write metadata.json once; on resume refuse if any strict key differs (vLLM version only warns)."""
    bench_dir = Path(bench_dir)
    bench_dir.mkdir(parents=True, exist_ok=True)
    path = bench_dir / "metadata.json"
    if not path.exists():
        path.write_text(json.dumps(meta, indent=2))
        return
    old = json.loads(path.read_text())
    diffs = [(k, old.get(k), meta.get(k)) for k in STRICT_METADATA_KEYS if old.get(k) != meta.get(k)]
    if diffs:
        lines = "\n".join(f"  {k}: existing={a!r} now={b!r}" for k, a, b in diffs)
        raise SystemExit(f"Refusing to resume into {bench_dir}: metadata differs\n{lines}\n"
                         f"Use another --out-dir, or delete the folder to relabel from scratch.")
    if old.get("vllm_version") != meta.get("vllm_version"):
        log(f"warning: resuming with vLLM {meta.get('vllm_version')} (shards so far: {old.get('vllm_version')})")


def load_cached_labels(bench_dir: Path, df: pd.DataFrame) -> dict[str, Label]:
    """query text -> Label from the shards already on disk (so a resumed run reuses them for duplicate texts)."""
    cache: dict[str, Label] = {}
    paths = existing_shards(bench_dir)
    if not paths:
        return cache
    done = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    text_of = dict(zip(df.query_id, df["query"]))
    for r in done.itertuples(index=False):
        t = text_of.get(r.query_id)
        if t is not None and t not in cache:
            cache[t] = Label(r.level1, r.level2, r.level3, bool(r.consistent), r.raw_output, bool(r.truncated))
    return cache


class TimeBudget:
    """Stop taking new shards when less than `min_remaining` seconds remain before `end_time` (epoch seconds)."""

    def __init__(self, end_time: float | None, min_remaining: float = 300.0):
        self.end_time = end_time
        self.min_remaining = min_remaining

    @classmethod
    def from_env(cls, min_remaining: float = 300.0) -> "TimeBudget":
        v = os.environ.get("SLURM_JOB_END_TIME")
        return cls(float(v) if v else None, min_remaining)

    def remaining(self) -> float | None:
        return None if self.end_time is None else self.end_time - time.time()

    def exhausted(self) -> bool:
        r = self.remaining()
        return r is not None and r < self.min_remaining


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def label_shard(sub: pd.DataFrame, labeler, cache: dict[str, Label], max_query_chars: int) -> pd.DataFrame:
    """Label one shard: unique texts not in `cache` go to the model, labels are mapped back to every row."""
    texts = list(dict.fromkeys(sub["query"].tolist()))  # unique, first-occurrence order
    todo = [t for t in texts if t not in cache]
    if todo:
        first = sub.drop_duplicates("query").set_index("query")
        batch, trunc = [], {}
        for t in todo:
            msgs, tr = fit_messages(t, first.at[t, "theme"], first.at[t, "subtask"], max_query_chars, labeler)
            batch.append(msgs)
            trunc[t] = tr
        raws = labeler.label(batch)
        if len(raws) != len(todo):
            raise RuntimeError(f"model returned {len(raws)} outputs for {len(todo)} prompts")
        for t, raw in zip(todo, raws):
            lab = parse_output(raw)
            lab.truncated = trunc[t]
            cache[t] = lab
    rows = []
    for r in sub.itertuples(index=False):
        lab = cache[r.query]
        rows.append((r.query_id, r.theme, r.subtask, lab.level1, lab.level2, lab.level3, lab.consistent, lab.raw_output,
                     lab.truncated))
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def run_benchmark(df: pd.DataFrame, bench_dir: Path, labeler, meta: dict, shard_size: int, max_query_chars: int,
                  budget: TimeBudget | None = None) -> dict:
    """Label `df` (already selected and sorted) into `bench_dir`, resuming past existing shards. Returns counters."""
    bench_dir = Path(bench_dir)
    write_or_check_metadata(bench_dir, meta)
    shards = plan_shards(df, shard_size)
    cache = load_cached_labels(bench_dir, df)
    stats = {"shards_total": len(shards), "shards_skipped": 0, "shards_done": 0, "shards_left": 0, "model_calls": 0,
             "rows": len(df), "cached_texts": len(cache)}
    budget = budget or TimeBudget(None)
    for i, sub in shards:
        path = shard_path(bench_dir, i)
        if path.exists():
            stats["shards_skipped"] += 1
            continue
        if budget.exhausted():
            stats["shards_left"] = len(shards) - stats["shards_skipped"] - stats["shards_done"]
            log(f"stopping before shard {i}: {budget.remaining():.0f}s left < {budget.min_remaining:.0f}s "
                f"({stats['shards_left']} shards left; rerun to resume)")
            break
        n_before = len(cache)
        t0 = time.time()
        out = label_shard(sub, labeler, cache, max_query_chars)
        stats["model_calls"] += len(cache) - n_before
        write_atomic_parquet(out, path)
        stats["shards_done"] += 1
        log(f"shard {i + 1}/{len(shards)}: {len(sub)} rows, {len(cache) - n_before} model calls, "
            f"{time.time() - t0:.1f}s, inconsistent={int((~out.consistent).sum())}")
    return stats


# -------------------------------------------------------------------------------------------------------- dry run

def load_token_counter(spec: str):
    """(name, count(str) -> int, render(messages) -> str). Prefers the model's tokenizer + chat template
    (transformers), falls back to tiktoken cl100k_base with a ChatML-like wrapper."""
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(spec)

        def render(messages):
            try:
                return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            except TypeError:
                return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        return f"transformers:{spec}", (lambda s: len(tok(s, add_special_tokens=False).input_ids)), render
    except Exception as e:  # noqa: BLE001
        log(f"model tokenizer not available ({type(e).__name__}: {e}); falling back to tiktoken cl100k_base (approximate)")
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")

    def render(messages):
        return "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages) + "<|im_start|>assistant\n"

    return "tiktoken:cl100k_base", (lambda s: len(enc.encode(s, disallowed_special=()))), render


def token_stats(lengths: np.ndarray, limit: int | None = None) -> dict:
    lengths = np.asarray(lengths, dtype=np.int64)
    if len(lengths) == 0:
        return {"n": 0}
    s = {"n": int(len(lengths)), "mean": float(lengths.mean()), "median": float(np.median(lengths)),
         "p90": float(np.percentile(lengths, 90)), "p99": float(np.percentile(lengths, 99)),
         "max": int(lengths.max()), "sum": int(lengths.sum())}
    if limit is not None:
        s["over_limit"] = int((lengths > limit).sum())
    return s


def dry_run(benchmarks: list[str], args) -> dict:
    name, count, render = load_token_counter(args.tokenizer or args.model)
    sys_tokens = count(render([{"role": "system", "content": SYSTEM_PROMPT}]))
    print(f"tokenizer: {name}\nsystem prompt: {len(SYSTEM_PROMPT)} chars, ~{sys_tokens} tokens (shared prefix, cached once)")
    print(f"{taxonomy.summary()}; prompt hash {prompt_hash()}")
    limit_tokens = args.max_model_len - args.max_tokens
    results = {}
    for b in benchmarks:
        df = select_rows(load_queries(b, Path(args.data_root)), args.limit, args.seed)
        uniq = df.drop_duplicates("query")
        rendered, truncated = [], 0
        for r in uniq.itertuples(index=False):
            msgs, tr = build_messages(r.query, r.theme, r.subtask, args.max_query_chars)
            rendered.append(render(msgs))
            truncated += tr
        lengths = np.array([count(s) for s in rendered])
        st = token_stats(lengths, limit_tokens)
        st.update(rows=len(df), unique_texts=len(uniq), truncated=int(truncated))
        results[b] = st
        print(f"\n=== {b}: {len(df)} rows, {len(uniq)} unique query texts, {truncated} truncated at {args.max_query_chars} chars")
        print("prompt tokens: " + ", ".join(f"{k}={v:.0f}" if isinstance(v, float) else f"{k}={v}" for k, v in st.items()
                                             if k in ("mean", "median", "p90", "p99", "max", "over_limit")))
        print(f"  (over_limit = prompts above max_model_len - max_tokens = {limit_tokens} tokens; at run time these queries are "
              f"shrunk until they fit and flagged truncated; raise --max-model-len to avoid that)")
        per_theme = pd.Series(lengths, index=uniq.theme.values).groupby(level=0).agg(["median", "max", "size"]).astype(int)
        print("  per theme (median / max / n):")
        for th, row in per_theme.iterrows():
            print(f"    {th:20s} {row['median']:6d} {row['max']:6d} {row['size']:6d}")
        order = np.argsort(lengths)
        picks = [order[0], order[len(order) // 2], order[-1]]
        for j, k in enumerate(picks):
            r = uniq.iloc[k]
            print(f"\n--- example prompt {j + 1}/3 ({b}, {['shortest', 'median', 'longest'][j]}, {lengths[k]} tokens, "
                  f"query_id={r.query_id}) ---")
            s = rendered[k]
            body = s.split(SYSTEM_PROMPT, 1)[-1] if SYSTEM_PROMPT in s else s
            print(body if len(body) <= 2500 else body[:1800] + "\n[... example clipped for display ...]\n" + body[-600:])
    print("\n--- system prompt (shared by every call) ---\n" + SYSTEM_PROMPT)
    return results


# ----------------------------------------------------------------------------------------------------------- main

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--benchmark", choices=(*BENCHMARKS, "all"), required=True)
    p.add_argument("--model", required=True, help="HF model directory on local disk (e.g. $SCRATCH/models/Qwen3-32B)")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT, help="folder holding <benchmark>/queries.parquet")
    p.add_argument("--shard-size", type=int, default=1000)
    p.add_argument("--max-query-chars", type=int, default=3000, help="middle-truncate longer queries (head+tail kept)")
    p.add_argument("--limit", type=int, default=None, help="label only a seeded random subset of N rows (output to <benchmark>_limitN)")
    p.add_argument("--dtype", default="bfloat16")
    p.add_argument("--tp", type=int, default=1)
    p.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    p.add_argument("--max-model-len", type=int, default=4096)
    p.add_argument("--max-tokens", type=int, default=64)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--min-remaining-sec", type=float, default=300.0, help="do not start a shard with less time than this before SLURM_JOB_END_TIME")
    p.add_argument("--dry-run", action="store_true", help="build prompts, print 3 and the token-length stats, exit without loading the model")
    p.add_argument("--tokenizer", default=None, help="tokenizer path for --dry-run (default: --model)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    benchmarks = list(BENCHMARKS) if args.benchmark == "all" else [args.benchmark]
    if args.dry_run:
        dry_run(benchmarks, args)
        return 0
    model_dir = Path(args.model)
    if not (model_dir / "config.json").exists():
        raise SystemExit(f"--model {args.model}: no config.json there (download it first, labeling/download_model.sh)")
    log(f"loading {args.model} with vLLM (dtype={args.dtype}, tp={args.tp}, max_model_len={args.max_model_len})")
    labeler = VllmLabeler(args.model, args.dtype, args.tp, args.gpu_memory_utilization, args.max_model_len,
                          args.max_tokens, args.seed)
    budget = TimeBudget.from_env(args.min_remaining_sec)
    meta = build_metadata(args.model, args.dtype, args.max_query_chars, args.shard_size, args.max_tokens,
                          args.max_model_len, {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()})
    for b in benchmarks:
        df = select_rows(load_queries(b, args.data_root), args.limit, args.seed)
        bench_dir = args.out_dir / (b if args.limit is None else f"{b}_limit{args.limit}")
        log(f"{b}: {len(df)} rows -> {bench_dir}" + (f" ({budget.remaining():.0f}s left in the job)" if budget.remaining() is not None else ""))
        stats = run_benchmark(df, bench_dir, labeler, meta, args.shard_size, args.max_query_chars, budget)
        log(f"{b}: {stats}")
        if stats["shards_left"]:
            log(f"{b}: incomplete, rerun the same command to resume")
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
