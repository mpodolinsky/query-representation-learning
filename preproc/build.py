"""Build the processed benchmarks in preproc/data/ from the raw downloads, and write reports/build_report.md.

    python preproc/build.py [--llmrb-dir ...] [--routerbench-pkl ...]

Deterministic: rerunning on the same inputs gives the same tables (the report lists a digest of each)."""
import argparse
import ast
import glob
import hashlib
import json
import re
import subprocess
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from data import (BENCHMARKS, MODEL_TABLES, SPLIT_FRACTIONS, SPLIT_SEEDS, release_epochs, sample_probes,
                  unseen_instances)

HERE = Path(__file__).parent
REPO = HERE.parent
LLMRB_DATASETS = [("aime", "hybrid"), ("arc-agi", "v1"), ("gpqa", "test"), ("hle", "test"),
                  ("livecodebench", "test"), ("livemathbench", "test"), ("mmlupro", "test_3000"),
                  ("simpleqa", "test"), ("arenahard", None)]
LLMRB_EXCLUDED = {"swe-bench (verified)": "no qwen3-235b-a22b-thinking-2507 results",
                  "tau2 (test)": "no gpt-5-chat results"}
# Upstream copies of two metadata files that are Git LFS pointers in deps/ (checked against the pointers' sha256)
META_FILES = {"hle_test.jsonl": "HLE/test.jsonl", "arenahard.jsonl": "ArenaHard/arena-hard-v2.jsonl"}
META_URL = "https://media.githubusercontent.com/media/ynulihao/LLMRouterBench/main/data/{}"
PROBE_NS = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, None)  # None = every training query
PROBE_SEEDS = range(5)


# ---------------------------------------------------------------------------------------------------- raw inputs

def fetch_meta(meta_dir):
    """Download the HLE and ArenaHard metadata (categories) if missing, and verify them against the LFS pointers."""
    meta_dir.mkdir(parents=True, exist_ok=True)
    for local, upstream in META_FILES.items():
        path = meta_dir / local
        if not path.exists():
            print(f"downloading {upstream}")
            urllib.request.urlretrieve(META_URL.format(upstream), path)
        pointer = (REPO / "deps/LLMRouterBench/data" / upstream).read_text()
        oid = re.search(r"sha256:([0-9a-f]{64})", pointer).group(1)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == oid, f"{path} does not match its LFS pointer"
    return {k: [json.loads(line) for line in open(meta_dir / k)] for k in META_FILES}


def load_llmrb(bench_dir, meta):
    """Long table of the 13 flagship models on the 9 complete datasets, and the query table."""
    models = [m[0] for m in MODEL_TABLES["llmrouterbench"]]
    price = {m[0]: (m[3], m[4]) for m in MODEL_TABLES["llmrouterbench"]}
    hle_cat = {r["question"]: r["category"] for r in meta["hle_test.jsonl"]}
    arena_cat = {r["prompt"]: r["subcategory"] for r in meta["arenahard.jsonl"]}
    log, qrows, srows = Counter(), [], []
    for ds, split in LLMRB_DATASETS:
        recs = {}
        for m in models:
            files = glob.glob(f"{bench_dir}/{ds}/{split}/{m}/*.json" if split else f"{bench_dir}/{ds}/{m}/*.json")
            assert len(files) == 1, f"{ds}/{m}: expected one result file, found {files}"
            recs[m] = {r["index"]: r for r in json.load(open(files[0]))["records"]}
        index = sorted(recs[models[0]])
        assert all(sorted(recs[m]) == index for m in models), f"{ds}: models answer different queries"
        for i in index:
            # the question text is the same for every model except a handful of records: take the most common one
            texts = Counter((recs[m][i]["origin_query"], recs[m][i]["prompt"]) for m in models)
            (origin, prompt), n = texts.most_common(1)[0]
            log["text differs across models"] += len(models) - n
            query = prompt if ds == "arc-agi" else origin  # ARC-AGI's origin_query is only a task id
            subtask = ds
            if ds == "mmlupro":
                subtask = re.match(r"Answer the following (.+?) question\.", prompt).group(1)
            elif ds == "hle":
                subtask = hle_cat.get(origin, ds)
                log["hle without category"] += subtask == ds
            elif ds == "arenahard":
                subtask = arena_cat.get(origin, ds)
                log["arenahard without category"] += subtask == ds
            qid = f"llmrb/{ds}/{i}"
            qrows.append({"query_id": qid, "theme": ds, "subtask": subtask, "query": query, "prompt": prompt})
            for m in models:
                r = recs[m][i]
                pt, ct = r.get("prompt_tokens") or 0, r.get("completion_tokens") or 0
                out = str(r.get("raw_output") or "").strip()
                srows.append({"query_id": qid, "model": m, "score": float(r["score"]),
                              "cost": (pt * price[m][0] + ct * price[m][1]) / 1e6 if pt else np.nan,
                              "recorded_cost": float(r.get("cost") or 0), "empty_output": out == "",
                              "failed": out == "failed to generate"})
    return pd.DataFrame(qrows), pd.DataFrame(srows), log


def load_routerbench(pkl):
    """Long table of the 11 models on RouterBench 0-shot, and the query table."""
    df = pd.read_pickle(pkl)
    models = [m[0] for m in MODEL_TABLES["routerbench"]]
    log = Counter({"test-match queries dropped": int((df.eval_name == "test-match").sum())})
    df = df[df.eval_name != "test-match"].reset_index(drop=True)  # 3 trivial sanity prompts, not a task

    def family(e):
        if e.startswith("mmlu"):
            return "mmlu"
        if e.lower().startswith("chinese"):
            return "chinese"
        return "mtbench" if e.startswith("mtbench") else e

    def split_prompt(p, e):
        parts = ast.literal_eval(p)
        # 2 parts: [instruction (GSM8K: with 8 worked examples), question]; MT-Bench: [turn 1, turn 2]
        query = parts[0] if (len(parts) == 1 or e.startswith("mtbench")) else parts[1]
        return query, "\n\n".join(parts)

    texts = [split_prompt(p, e) for p, e in zip(df.prompt, df.eval_name)]
    queries = pd.DataFrame({"query_id": df.sample_id, "theme": df.eval_name.map(family), "subtask": df.eval_name,
                            "query": [t[0] for t in texts], "prompt": [t[1] for t in texts]})
    scores = pd.DataFrame({
        "query_id": np.repeat(df.sample_id.to_numpy(), len(models)),
        "model": np.tile(models, len(df)),
        "score": df[models].to_numpy(np.float64).ravel(),
        "cost": df[[f"{m}|total_cost" for m in models]].to_numpy(np.float64).ravel()})
    return queries, scores, log


# ---------------------------------------------------------------------------------------------------- processing

def dedupe(queries, scores, log):
    """Drop exact duplicate prompts (keep the first): a copy in train and one in test would be a distance-0 neighbor."""
    dup = queries.prompt.duplicated()
    log["duplicate prompts dropped"] = int(dup.sum())
    queries = queries[~dup].reset_index(drop=True)
    return queries, scores[scores.query_id.isin(queries.query_id)].reset_index(drop=True)


def impute_cost(queries, scores, log):
    """Records without token counts get the model's mean cost on the same theme (flagged by `cost_imputed`)."""
    scores = scores.merge(queries[["query_id", "theme"]], on="query_id")
    scores["cost_imputed"] = scores.cost.isna()
    log["costs imputed (no token counts)"] = int(scores.cost_imputed.sum())
    scores["cost"] = scores.cost.fillna(scores.groupby(["model", "theme"]).cost.transform("mean"))
    assert scores.cost.notna().all()
    return scores.drop(columns="theme")


def make_split(theme, seed):
    """Random query-level split, stratified by theme: each theme is split SPLIT_FRACTIONS (rounded)."""
    rng = np.random.default_rng(seed)
    parts = ([], [], [])
    for t in sorted(set(theme)):
        idx = rng.permutation(np.flatnonzero(theme == t))
        n_tr = int(np.floor(SPLIT_FRACTIONS[0] * len(idx) + 0.5))
        n_va = int(np.floor(SPLIT_FRACTIONS[1] * len(idx) + 0.5))
        for part, sl in zip(parts, (idx[:n_tr], idx[n_tr:n_tr + n_va], idx[n_tr + n_va:])):
            part.append(sl)
    return tuple(np.sort(np.concatenate(p)) for p in parts)


def digest(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes()).hexdigest()[:16]


def write(benchmark, queries, scores, out):
    """Write the processed tables of one benchmark; return the model table."""
    d = out / benchmark
    (d / "splits").mkdir(parents=True, exist_ok=True)
    order = {m[0]: i for i, m in enumerate(MODEL_TABLES[benchmark])}
    scores = scores.sort_values(["query_id", "model"], key=lambda c: c.map(order) if c.name == "model" else c)
    scores = scores.set_index("query_id").loc[queries.query_id].reset_index()  # rows in query order
    queries = queries.assign(n_chars=queries["query"].str.len())

    epochs = release_epochs(benchmark)
    first_epoch = {m: int(e.epoch) for _, e in epochs.iterrows() for m in e.new_models}
    agg = scores.groupby("model").agg(mean_cost=("cost", "mean"), mean_score=("score", "mean"),
                                      n_cost_imputed=("cost_imputed", "sum"))
    models = pd.DataFrame([{"model": m, "display_name": dn, "release": date, "epoch": first_epoch[m],
                            "price_in_per_1m": pi, "price_out_per_1m": po} for m, dn, date, pi, po in
                           MODEL_TABLES[benchmark]]).join(agg, on="model")
    epoch_costs = pd.DataFrame([{"epoch": e.epoch, "date": e.date, **{m: (models.set_index("model").mean_cost[m]
                                if m in e.pool else np.nan) for m in models.model}} for _, e in epochs.iterrows()])
    as_text = lambda df: df.assign(**{c: df[c].map(";".join) for c in ("new_models", "pool") if c in df})

    queries.to_parquet(d / "queries.parquet", compression="zstd", index=False)
    scores[["query_id", "model", "score", "cost", "cost_imputed"]].to_parquet(
        d / "scores.parquet", compression="zstd", index=False)
    models.to_csv(d / "models.csv", index=False)
    as_text(epochs).to_csv(d / "epochs.csv", index=False)
    epoch_costs.to_csv(d / "epoch_costs.csv", index=False)
    as_text(unseen_instances(benchmark)).to_csv(d / "instances.csv", index=False)
    theme = queries.theme.to_numpy()
    splits = {}
    for s in SPLIT_SEEDS:
        tr, va, te = splits[s] = make_split(theme, s)
        np.savez(d / "splits" / f"seed{s}.npz", train=tr, val=va, test=te)
    return queries, scores, models, epoch_costs, splits


# ---------------------------------------------------------------------------------------------------- report

def md(df, floatfmt="{:.4g}"):
    """Markdown table without the tabulate dependency."""
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (floatfmt.format(v) if isinstance(v, float)
                                                                       else str(v))
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def report_benchmark(name, queries, scores, models, epoch_costs, splits, log, extra):
    S = scores.pivot(index="query_id", columns="model", values="score")
    nonbinary = scores.assign(nb=~scores.score.isin([0.0, 1.0])).groupby(
        scores.query_id.map(queries.set_index("query_id").theme)).nb.mean()
    out = [f"## {name}", "",
           f"- **{len(queries):,} queries × {len(models)} models = {len(scores):,} (query, model) rows**; "
           f"score matrix complete: {not S.isna().any().any()}; scores in [{scores.score.min()}, {scores.score.max()}]"
           f" (no rescaling needed); {(~scores.score.isin([0.0, 1.0])).mean():.1%} of scores are not 0/1"
           f" (themes: {', '.join(f'{t} {v:.0%}' for t, v in nonbinary[nonbinary > 0].items())}).",
           *[f"- {k}: {v:,}" for k, v in log.items()], *extra, ""]

    # themes and split sizes
    rows = []
    for t, g in queries.groupby("theme"):
        idx = set(g.index)
        row = {"theme": t, "queries": len(g), "share": f"{len(g) / len(queries):.1%}", "subtasks": g.subtask.nunique()}
        for s, (tr, va, te) in splits.items():
            row[f"seed{s} train/val/test"] = "/".join(str(len(idx & set(p))) for p in (tr, va, te))
        rows.append(row)
    out += ["### Themes and splits", "", md(pd.DataFrame(rows)), ""]

    out += ["### Models", "", md(models.assign(
        mean_cost=models.mean_cost.map("{:.3g}".format), mean_score=models.mean_score.map("{:.3f}".format))), ""]
    theme_of = scores.query_id.map(queries.set_index("query_id").theme)
    ms = scores.groupby([theme_of.rename("theme"), "model"]).score.mean().unstack()[models.model]
    ms.columns = models.display_name
    out += ["### Mean score per theme", "", md(ms.reset_index(), "{:.2f}"), ""]
    ec = epoch_costs.copy()
    ec.columns = ["epoch", "date"] + models.display_name.tolist()
    out += ["### Release epochs: mean cost per query (USD; blank = not released yet)", "",
            md(ec, "{:.2e}"), ""]
    inst = unseen_instances(name.lower())
    out += ["### Unseen-model instances", "", md(inst.assign(
        pool=inst.pool.map(lambda p: f"{len(p)} models: " + ", ".join(p)))), ""]

    # probe coverage of the themes, split seed 0 (the same for every instance: probes depend on the split and seed only)
    tr = splits[0][0]
    theme = queries.theme.to_numpy()
    rows = []
    for n in PROBE_NS:
        row = {"n": n or f"all ({len(tr)})"}
        share = pd.Series(theme[tr]).value_counts(normalize=True)
        for label, th in (("random", None), ("stratified", theme)):
            probes = [theme[sample_probes(tr, n, s, th)] for s in PROBE_SEEDS]
            dev = [(pd.Series(p).value_counts().reindex(share.index, fill_value=0) - len(p) * share).abs().max()
                   for p in probes]
            row[f"{label}: themes covered"] = f"{np.mean([len(set(p)) for p in probes]):.1f}"
            row[f"{label}: max theme miscount"] = f"{np.mean(dev):.1f}"
        rows.append(row)
    out += [f"### Probe coverage (split seed 0, mean over probe seeds 0–{max(PROBE_SEEDS)}, "
            f"{queries.theme.nunique()} themes)", "",
            "Probes depend only on the training split and the probe seed, so every unseen instance gets the same ones. "
            "*Max theme miscount* is the largest |probes of a theme − n × its share of train|: stratified sampling keeps "
            "the theme mix proportional (miscount about 1 or less); it does not guarantee that a small theme is covered.", "",
            md(pd.DataFrame(rows)), ""]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--llmrb-dir", default=REPO / "deps/LLMRouterBench/results/bench-release", type=Path)
    ap.add_argument("--routerbench-pkl", default=REPO.parent / "routerbench_0shot.pkl", type=Path)
    ap.add_argument("--meta-dir", default=HERE / "raw", type=Path)
    ap.add_argument("--out", default=HERE / "data", type=Path)
    ap.add_argument("--report", default=HERE / "reports/build_report.md", type=Path)
    args = ap.parse_args()

    git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    report = ["# Build report", "",
              f"Built {datetime.now():%Y-%m-%d %H:%M} at commit {git('rev-parse', '--short', 'HEAD')}"
              f"{'-dirty' if git('status', '--porcelain') else ''} by `preproc/build.py`.", ""]
    digests = []
    for name in BENCHMARKS:
        if name == "llmrouterbench":
            q, s, log = load_llmrb(args.llmrb_dir, fetch_meta(args.meta_dir))
            extra = [f"- excluded datasets: " + "; ".join(f"{k}: {v}" for k, v in LLMRB_EXCLUDED.items()),
                     f"- empty outputs (mostly reasoning models hitting their token limit; scored as published): "
                     f"{int(s.empty_output.sum()):,}; 'failed to generate' (API failures, scored 0 as published): "
                     f"{int(s.failed.sum())}",
                     f"- cost = tokens × Table 1 price. The recorded `cost` is 0 on "
                     f"{int(((s.recorded_cost == 0) & s.cost.notna()).sum()):,} records that have token counts; "
                     "recorded vs recomputed total: "
                     + ", ".join(f"{m} {g.recorded_cost.sum() / g.cost.sum() - 1:+.1%}"
                                 for m, g in s.dropna(subset=["cost"]).groupby("model", sort=False)
                                 if abs(g.recorded_cost.sum() / g.cost.sum() - 1) > 0.005) + " (others within 0.5%)"]
        else:
            q, s, log = load_routerbench(args.routerbench_pkl)
            s["cost_imputed"] = False
            extra = ["- cost = recorded `total_cost`; prices in the model table are from "
                     "`deps/routerbench/routers/common.py` (information only)"]
        q, s = dedupe(q, s, log)
        if name == "llmrouterbench":
            s = impute_cost(q, s, log)
        queries, scores, models, epoch_costs, splits = write(name, q, s, args.out)
        print(f"{name}: {len(queries)} queries × {len(models)} models")
        report += report_benchmark({"llmrouterbench": "LLMRouterBench", "routerbench": "RouterBench"}[name],
                                   queries, scores, models, epoch_costs, splits, log, extra)
        digests += [f"- `{name}/queries`: {digest(queries)}",
                    f"- `{name}/scores`: {digest(scores[['query_id', 'model', 'score', 'cost', 'cost_imputed']])}"]
    report += ["## Table digests", "", "Content hashes of the processed tables; a rebuild must reproduce them.", "",
               *digests, ""]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report))
    print(f"report: {args.report}")


if __name__ == "__main__":
    main()
