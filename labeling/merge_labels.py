#!/usr/bin/env python
"""Merge the label shards of a benchmark, check coverage, and write the labels file, a report and a hand-check sample.

    python labeling/merge_labels.py --benchmark all [--out-dir labeling/out] [--data-root preproc/data]

Writes
- <data-root>/<benchmark>/task_labels.parquet  (query_id, level1, level2, level3, consistent)   [--labels-out]
- <out-dir>/<benchmark>/labels_full.parquet     (every output column, plus theme/subtask)
- labeling/reports/<benchmark>_labels_report.md (counts, theme x level1, rates, 15 examples per level1)
- labeling/reports/<benchmark>_handcheck_sample.csv (200 stratified rows with an empty `correct` column)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxonomy  # noqa: E402
from label_tasks import BENCHMARKS, DEFAULT_DATA_ROOT, DEFAULT_OUT_DIR, PARSE_ERROR, existing_shards, load_queries  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_REPORTS_DIR = HERE / "reports"
LABEL_COLUMNS = ["query_id", "level1", "level2", "level3", "consistent"]


class CoverageError(Exception):
    pass


def load_shards(bench_dir: Path) -> pd.DataFrame:
    paths = existing_shards(bench_dir)
    if not paths:
        raise CoverageError(f"no shards in {bench_dir}")
    leftovers = list(Path(bench_dir).glob("*.tmp"))
    if leftovers:
        print(f"warning: ignoring {len(leftovers)} .tmp file(s) in {bench_dir} (interrupted writes)", file=sys.stderr)
    return pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)


def check_coverage(labels: pd.DataFrame, queries: pd.DataFrame) -> None:
    """Every query_id of queries.parquet exactly once in the labels, nothing else."""
    dup = labels.query_id[labels.query_id.duplicated()]
    if len(dup):
        raise CoverageError(f"{len(dup)} duplicated query_id in the shards, e.g. {dup.head(3).tolist()}")
    have, want = set(labels.query_id), set(queries.query_id)
    missing, extra = want - have, have - want
    if missing or extra:
        raise CoverageError(f"coverage failed: {len(missing)} query_id missing (e.g. {sorted(missing)[:3]}), "
                            f"{len(extra)} unknown (e.g. {sorted(extra)[:3]})")


def md_table(df: pd.DataFrame, index: bool = True) -> str:
    df = df.reset_index() if index else df
    cols = [str(c) for c in df.columns]
    rows = [[str(v) for v in r] for r in df.itertuples(index=False)]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def clip(s: str, n: int = 200) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip().replace("|", "\\|")
    return s if len(s) <= n else s[: n - 15] + " [...] " + s[-8:]


def make_report(df: pd.DataFrame, benchmark: str, meta: dict | None, n_examples: int = 15, seed: int = 0) -> str:
    """df: labels joined with theme, subtask, query."""
    n = len(df)
    rng = np.random.default_rng(seed)
    parse_err = (df.level3 == PARSE_ERROR)
    L = [f"# Task labels: {benchmark}", "",
         f"- queries: {n}", f"- taxonomy: v{(meta or {}).get('taxonomy_version', taxonomy.VERSION)}",
         f"- model: `{(meta or {}).get('model', '?')}` (config sha256 `{str((meta or {}).get('config_sha256'))[:12]}`), "
         f"vLLM {(meta or {}).get('vllm_version', '?')}, prompt hash `{(meta or {}).get('prompt_hash', '?')}`",
         f"- inconsistent level1/level2 pairs: {int((~df.consistent).sum())} ({100 * (~df.consistent).mean():.2f}%)",
         f"- parse errors (level3 = {PARSE_ERROR}): {int(parse_err.sum())} ({100 * parse_err.mean():.2f}%)",
         f"- truncated queries: {int(df.truncated.sum())} ({100 * df.truncated.mean():.2f}%)",
         f"- distinct level3 phrases: {df.level3.nunique()}", ""]
    c1 = df.level1.value_counts().rename("n").to_frame()
    c1["%"] = (100 * c1.n / n).round(2)
    L += ["## Level 1", "", md_table(c1), ""]
    c2 = df.groupby(["level1", "level2"]).size().rename("n").to_frame().sort_values(["level1", "n"], ascending=[True, False])
    c2["%"] = (100 * c2.n / n).round(2)
    L += ["## Level 2", "", md_table(c2), ""]
    ct = pd.crosstab(df.theme, df.level1)
    L += ["## Theme x level 1", "", md_table(ct), ""]
    top = (df.groupby(["theme", "level2"]).size().rename("n").reset_index().sort_values(["theme", "n"], ascending=[True, False])
           .groupby("theme").head(3))
    top["share"] = top.apply(lambda r: f"{100 * r.n / (df.theme == r.theme).sum():.0f}%", axis=1)
    L += ["## Top-3 level 2 per theme", "", md_table(top.set_index("theme")), ""]
    inc = df[~df.consistent]
    if len(inc):
        L += ["## Inconsistent pairs (level2 not under level1), top 15", "",
              md_table(inc.groupby(["level1", "level2"]).size().rename("n").sort_values(ascending=False).head(15).to_frame()), ""]
    L += [f"## {n_examples} random examples per level 1", ""]
    for d in taxonomy.LEVEL1:
        g = df[df.level1 == d]
        if not len(g):
            continue
        L.append(f"### {d} (n={len(g)})\n")
        take = g.iloc[rng.choice(len(g), size=min(n_examples, len(g)), replace=False)]
        for r in take.itertuples(index=False):
            L.append(f"- `{r.query_id}` [{r.theme}/{r.subtask}] -> **{r.level2}** / {r.level3}: {clip(r.query)}")
        L.append("")
    return "\n".join(L)


def handcheck_sample(df: pd.DataFrame, n: int = 200, seed: int = 0, min_per_class: int = 5) -> pd.DataFrame:
    """n rows stratified by level1: proportional allocation with at least min_per_class per present class."""
    rng = np.random.default_rng(seed)
    sizes = df.level1.value_counts()
    n = min(n, len(df))
    alloc = {d: min(int(s), max(min_per_class, int(round(n * s / len(df))))) for d, s in sizes.items()}
    while sum(alloc.values()) > n:
        d = max(alloc, key=alloc.get)
        alloc[d] -= 1
    while sum(alloc.values()) < n:
        room = {d: int(sizes[d]) - a for d, a in alloc.items() if int(sizes[d]) > a}
        if not room:
            break
        alloc[max(room, key=room.get)] += 1
    parts = [df[df.level1 == d].iloc[rng.choice(int(sizes[d]), size=k, replace=False)] for d, k in alloc.items() if k > 0]
    out = pd.concat(parts, ignore_index=True)
    out = out.iloc[rng.permutation(len(out))].reset_index(drop=True)
    out = out[["query_id", "theme", "subtask", "query", "level1", "level2", "level3", "consistent"]].copy()
    out["correct"] = ""
    return out


def merge_benchmark(benchmark: str, out_dir: Path, data_root: Path, labels_out: Path | None, reports_dir: Path,
                    n_examples: int = 15, n_handcheck: int = 200, seed: int = 0) -> dict:
    bench_dir = Path(out_dir) / benchmark
    queries = load_queries(benchmark, data_root)
    labels = load_shards(bench_dir)
    check_coverage(labels, queries)
    meta_path = bench_dir / "metadata.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else None
    # row order = queries.parquet order
    merged = queries.merge(labels.drop(columns=["theme", "subtask"]), on="query_id", how="left", validate="one_to_one")
    assert merged.level1.notna().all()
    merged["consistent"] = merged.consistent.astype(bool)
    merged["truncated"] = merged.truncated.astype(bool)

    labels_out = Path(labels_out) if labels_out else Path(data_root) / benchmark / "task_labels.parquet"
    labels_out.parent.mkdir(parents=True, exist_ok=True)
    merged[LABEL_COLUMNS].to_parquet(labels_out, index=False)
    merged.drop(columns=["query"]).to_parquet(bench_dir / "labels_full.parquet", index=False)

    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{benchmark}_labels_report.md"
    report_path.write_text(make_report(merged, benchmark, meta, n_examples, seed))
    sample_path = reports_dir / f"{benchmark}_handcheck_sample.csv"
    handcheck_sample(merged, n_handcheck, seed).to_csv(sample_path, index=False)
    return {"benchmark": benchmark, "rows": len(merged), "labels": str(labels_out), "report": str(report_path),
            "handcheck": str(sample_path), "inconsistent": int((~merged.consistent).sum()),
            "parse_errors": int((merged.level3 == PARSE_ERROR).sum())}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--benchmark", choices=(*BENCHMARKS, "all"), required=True)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="label_tasks.py --out-dir")
    p.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    p.add_argument("--labels-out", type=Path, default=None, help="default <data-root>/<benchmark>/task_labels.parquet (one benchmark only)")
    p.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    p.add_argument("--n-examples", type=int, default=15)
    p.add_argument("--n-handcheck", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    benchmarks = list(BENCHMARKS) if args.benchmark == "all" else [args.benchmark]
    if args.labels_out and len(benchmarks) > 1:
        raise SystemExit("--labels-out works with a single --benchmark")
    rc = 0
    for b in benchmarks:
        try:
            res = merge_benchmark(b, args.out_dir, args.data_root, args.labels_out, args.reports_dir, args.n_examples,
                                  args.n_handcheck, args.seed)
            print(json.dumps(res, indent=2))
        except CoverageError as e:
            print(f"{b}: {e}", file=sys.stderr)
            rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
