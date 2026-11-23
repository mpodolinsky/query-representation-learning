"""How the neighbourhood size k interacts with the probe budget in the unseen setting.

The harness uses one k for every model. A new model has labels on n probes only, so its estimate is the mean of
min(k, n) probes: with k >= n it is one constant (the probe mean) for every query. In a representation organized by
quality (the learned embeddings), the pool models' estimates are low exactly on the hard queries, so a constant
estimate of the new model wins there and the router sends the hard queries to it. This script measures the effect:
the unseen gain of a few representations on a few release instances, with k fixed at several values, for two probe
budgets, on one split (checkpoints and sentence vectors from the unified run's cache; nothing is retrained).

    python k_unseen_check.py                         # LLMRouterBench instances 9-11, RouterBench 7-8, split 0
Writes --out/k_unseen_check.csv; build_report.py shows it."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for p in (REPO, REPO / "michal-harness", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--instances", nargs="+", default=["llmrouterbench:9", "llmrouterbench:10", "llmrouterbench:11", "routerbench:7", "routerbench:8"])
    p.add_argument("--representations", nargs="+", default=["handcrafted", "frozen", "regression", "contrastive"])
    p.add_argument("--ks", nargs="+", type=int, default=[20, 50, 200, 500, 1000])
    p.add_argument("--budgets", nargs="+", type=int, default=[50, 500])
    p.add_argument("--split", type=int, default=0)
    p.add_argument("--train-seed", type=int, default=0)
    p.add_argument("--probe-seed", type=int, default=0)
    p.add_argument("--cache", default=str(REPO / "results" / "learned" / "cache"))
    p.add_argument("--out", default=str(HERE / "analysis_compare"))
    args = p.parse_args(argv)
    import torch
    torch.set_num_threads(1)
    from preproc.data import load_data
    from router import evaluate
    from learned.features import SentenceFeatures
    from learned.train import TrainConfig, make_fit
    from handcrafted import fit_handcrafted, fit_stats_only
    from run_handcrafted import labels_for

    rows, cache = [], {}
    for spec in args.instances:
        bench, inst = spec.split(":")
        inst = int(inst)
        if bench not in cache:
            full = load_data(bench, split_seed=args.split)
            sent = SentenceFeatures(full.queries, args.cache)
            labels = labels_for("auto", bench, full)
            cache[bench] = (full, sent, labels)
        full, sent, labels = cache[bench]
        data = load_data(bench, split_seed=args.split, instance=inst)
        fits = {"handcrafted": fit_handcrafted(full, levels=(1, 2), labels=labels), "stats": fit_stats_only(full),
                "frozen": lambda m, s=sent: s.embed}
        for name in ("regression", "contrastive"):
            fits[name] = make_fit(data, sent, TrainConfig(objective=name, seed=args.train_seed), Path(args.cache) / "checkpoints")
        for name in args.representations:
            seen = {k: evaluate(data, fits[name], k=k, n_boot=0)["gain"] for k in args.ks}
            for n in args.budgets:
                for k in args.ks:
                    res = evaluate(data, fits[name], new_model=data.new_model, n_probes=n, seed=args.probe_seed, k=k, n_boot=0)
                    rows.append({"benchmark": bench, "instance": inst, "new_model": data.new_model, "representation": name,
                                 "n_probes": n, "k": k, "k_new": min(k, n), "gain_unseen": res["gain"], "gain_seen_same_k": seen[k],
                                 "A_unseen": res["A"], "gain_same_probes": res["gain_same_probes"]})
                    print(f"{bench} inst {inst} {name:12s} n={n:<4} k={k:<5} unseen {res['gain']:+.4f}  seen {seen[k]:+.4f}", flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "k_unseen_check.csv", index=False)
    print(df.pivot_table(index=["benchmark", "representation", "n_probes"], columns="k", values="gain_unseen").round(4).to_string())


if __name__ == "__main__":
    main()
