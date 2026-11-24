"""Statistical comparisons between representations, from the harness's saved runs.

1. Paired bootstrap over the test queries (the harness's own resampling, `router.bootstrap_areas`): for two
   representations evaluated on the same split and pool, the difference of their gains (or of A) is recomputed on
   1000 resamples of the test queries, shared by both, so the interval and the p-value are for the *difference*,
   not for each run separately. Needs the saved q-hat of each run (runs/NNNN.npz), the pool's costs (meta.json) and
   the test scores (from the loader). Reported: mean difference, 95% percentile interval, two-sided bootstrap p.
2. Across splits (and seeds): the same difference per split, its mean and standard deviation, the number of splits
   whose paired interval excludes zero, and a sign count. Three splits are too few for a classical test; the paired
   intervals within each split are the evidence, the across-split numbers show whether it repeats.

    python paired_tests.py --results-root ../results --reference handcrafted                  # my run folders
    python paired_tests.py --compare-root ../results_compare --reference handcrafted --n-probes 5 50 500
Outputs: --out/paired_seen.csv, paired_unseen.csv, paired_summary.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for p in (REPO, REPO / "michal-harness", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import router  # noqa: E402

_FULL = {}


def full_data(benchmark, split, loader=None):
    key = (benchmark, split)
    if key not in _FULL:
        from run_handcrafted import find_load_data
        _FULL[key] = find_load_data(loader)(benchmark, split_seed=split)
    return _FULL[key]


def load_folder(folder: Path, loader=None):
    """The rows of one harness results folder with what the paired bootstrap needs: test scores of the pool, costs."""
    meta = json.loads((folder / "meta.json").read_text())
    rows = pd.read_csv(folder / "results.csv", dtype={"new_model": str, "run": str})
    rows["new_model"] = rows["new_model"].fillna("")
    rows["n_probes"] = pd.to_numeric(rows["n_probes"], errors="coerce").fillna(0).astype(int)
    rows["run"] = rows["run"].map(lambda r: f"{int(r):04d}")
    split = np.load(folder / "split.npz")
    full = full_data(meta["benchmark"], int(meta["split_seed"]), loader)
    cols = [full.models.index(m) for m in meta["models"]]
    S_te = np.asarray(full.S)[split["test"]][:, cols]
    return rows, {"S_te": S_te, "cost": np.asarray(meta["cost"], dtype=float), "folder": folder,
                  "benchmark": meta["benchmark"], "split_seed": int(meta["split_seed"]), "models": meta["models"]}


def realized_runs(ctx, run_id):
    npz = np.load(ctx["folder"] / "runs" / f"{run_id}.npz")
    lambdas, Q_hat, q_mean = npz["lambdas"], npz["Q_hat"], npz["q_mean"]
    S, cost = ctx["S_te"], ctx["cost"]
    return {"router": router.realized(Q_hat, S, cost, lambdas),
            "single": router.realized(np.broadcast_to(q_mean, Q_hat.shape), S, cost, lambdas),
            "oracle": router.realized(S, S, cost, lambdas)}


def paired_difference(ctx, run_a, run_b, n_boot=1000, seed=0):
    """Paired bootstrap of gain_a - gain_b and A_a - A_b over the test queries (both runs on the same pool)."""
    ra, rb = realized_runs(ctx, run_a), realized_runs(ctx, run_b)
    c_range = (ctx["cost"].min(), ctx["cost"].max())
    areas = router.bootstrap_areas({"a": ra["router"], "b": rb["router"], "single": ra["single"], "oracle": ra["oracle"]},
                                   c_range, n_boot, seed)
    d_gain = areas["a"] / areas["single"] - areas["b"] / areas["single"]
    d_A = (areas["a"] - areas["b"]) / areas["oracle"]
    point = {name: router.area(router.curve(r["router"]), *c_range) for name, r in (("a", ra), ("b", rb))}
    single, oracle = router.area(router.curve(ra["single"]), *c_range), router.area(router.curve(ra["oracle"]), *c_range)
    out = {"d_gain": (point["a"] - point["b"]) / single, "d_A": (point["a"] - point["b"]) / oracle}
    for name, d in (("gain", d_gain), ("A", d_A)):
        lo, hi = np.quantile(d, [0.025, 0.975])
        frac = (d <= 0).mean()
        out.update({f"d_{name}_ci_low": lo, f"d_{name}_ci_high": hi, f"d_{name}_p": 2 * min(frac, 1 - frac),
                    f"d_{name}_boot_mean": d.mean()})
    return out


# ---------------------------------------------------------------- driving the comparisons

def folders_under(root: Path, exclude=("archive",)):
    return sorted(p.parent for p in Path(root).rglob("results.csv") if not any(x in str(p) for x in exclude))


def comparisons(args):
    """Yield (context, label row, run_a, run_b) for every pair in every folder / matched folders."""
    roots = [Path(args.results_root)] if args.results_root else []
    if args.compare_root:
        roots.append(Path(args.compare_root))
    # group runs by (benchmark, split, pool, setting, new_model, n_probes, probe seed, train seed)
    groups = {}
    for root in roots:
        for folder in folders_under(root):
            rows, ctx = load_folder(folder, args.loader)
            rel = folder.relative_to(root)
            train_seed = next((int(p[len("train"):]) for p in rel.parts if p.startswith("train")), 0)
            instance = next((int(p[len("inst"):]) for p in rel.parts if p.startswith("inst")), -1)
            for r in rows.itertuples():
                if r.new_model == "":
                    key = (ctx["benchmark"], ctx["split_seed"], instance, tuple(ctx["models"]), "seen", "", 0, 0)
                else:
                    if args.n_probes and r.n_probes not in args.n_probes:
                        continue
                    if r.seed not in args.probe_seeds:
                        continue
                    key = (ctx["benchmark"], ctx["split_seed"], instance, tuple(ctx["models"]), "unseen", r.new_model, r.n_probes, r.seed)
                groups.setdefault(key, {}).setdefault(r.embedding, []).append((ctx, r.run, train_seed))
    for key, by_emb in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0]))):
        benchmark, split, instance, models, setting, new_model, n_probes, probe_seed = key
        if setting == "unseen" and args.seen_only:
            continue
        names = sorted(by_emb)
        refs = [args.reference] if args.reference in by_emb else []
        pairs = [(a, b) for a in names for b in refs if a != b] if refs and not args.all_pairs else \
                [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
        for a, b in pairs:
            for ctx_a, run_a, seed_a in by_emb[a]:
                for ctx_b, run_b, seed_b in by_emb[b]:
                    if seed_a != seed_b and not args.cross_seeds:
                        continue
                    yield (ctx_a, ctx_b), {"benchmark": benchmark, "split_seed": split, "instance": instance,
                                           "pool_size": len(models), "setting": setting, "new_model": new_model,
                                           "n_probes": n_probes, "probe_seed": probe_seed, "train_seed": seed_a,
                                           "a": a, "b": b}, run_a, run_b


def markdown_table(frame: pd.DataFrame, decimals=4) -> str:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for row in frame.itertuples(index=False, name=None):
        cells = [(f"{v:.{decimals}f}" if isinstance(v, (float, np.floating)) and np.isfinite(v) else str(v)) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Across splits (and seeds): mean and sd of the difference, splits whose interval excludes 0, sign count."""
    if df.empty:
        return df
    g = df.groupby(["benchmark", "setting", "instance", "new_model", "n_probes", "a", "b"], dropna=False)
    out = g.agg(n=("d_gain", "size"), d_gain_mean=("d_gain", "mean"), d_gain_sd=("d_gain", lambda s: s.std(ddof=0)),
                d_A_mean=("d_A", "mean"), wins=("d_gain", lambda s: int((s > 0).sum())),
                ci_excludes_0=("d_gain_ci_low", lambda s: int(((s > 0) | (df.loc[s.index, "d_gain_ci_high"] < 0)).sum())),
                min_p=("d_gain_p", "min"), median_p=("d_gain_p", "median")).reset_index()
    return out


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results-root", default=None, help="flat harness folders (run_handcrafted.py)")
    p.add_argument("--compare-root", default=None, help="nested folders of compare_representations.py")
    p.add_argument("--reference", default="handcrafted", help="compare every representation against this one")
    p.add_argument("--all-pairs", action="store_true")
    p.add_argument("--seen-only", action="store_true")
    p.add_argument("--n-probes", nargs="*", type=int, default=[5, 50, 500], help="unseen budgets to compare (all if empty)")
    p.add_argument("--probe-seeds", nargs="+", type=int, default=[0])
    p.add_argument("--cross-seeds", action="store_true", help="also pair different training seeds")
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--workers", type=int, default=1, help="processes for the comparisons (each one is ~10-30 s)")
    p.add_argument("--benchmark", default=None)
    p.add_argument("--loader", default=None)
    p.add_argument("--out", default=str(HERE / "analysis_compare"))
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not (args.results_root or args.compare_root):
        raise SystemExit("give --results-root and/or --compare-root")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tasks = []
    for (ctx_a, ctx_b), label, run_a, run_b in comparisons(args):
        if args.benchmark and label["benchmark"] != args.benchmark:
            continue
        if ctx_a["folder"] != ctx_b["folder"] and (ctx_a["models"] != ctx_b["models"] or ctx_a["split_seed"] != ctx_b["split_seed"]):
            continue
        tasks.append((ctx_a, ctx_b, label, run_a, run_b, args.n_boot))
    print(f"{len(tasks)} paired comparisons, {args.workers} worker(s)", flush=True)
    if args.workers > 1:
        import multiprocessing
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("fork")) as pool:
            rows = list(pool.map(_task, tasks, chunksize=4))
    else:
        rows = [_task(t) for t in tasks]
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("no comparable runs found")
    seen, unseen = df[df.setting == "seen"], df[df.setting == "unseen"]
    seen.to_csv(out / "paired_seen.csv", index=False)
    unseen.to_csv(out / "paired_unseen.csv", index=False)
    s_seen, s_unseen = summarize(seen), summarize(unseen)
    s_seen.to_csv(out / "paired_seen_summary.csv", index=False)
    s_unseen.to_csv(out / "paired_unseen_summary.csv", index=False)
    lines = [f"# Paired comparisons against `{args.reference}`" if not args.all_pairs else "# Paired comparisons", "",
             "d_gain = gain(a) - gain(b) on the same split and pool; the interval is the 95% paired bootstrap over the test "
             "queries; p is the two-sided bootstrap p-value. `wins` counts splits (x seeds) where a > b, `ci_excludes_0` "
             "those whose paired interval excludes zero.", ""]
    for title, s in (("Seen setting (final pool and instance pools)", s_seen), ("Unseen setting", s_unseen)):
        if s.empty:
            continue
        lines += [f"## {title}", "", markdown_table(s), ""]
    (out / "paired_summary.md").write_text("\n".join(lines))
    print(f"\nwritten to {out}")


def _task(t):
    """One paired comparison (runs in a worker): both runs are on the same pool and split; test scores from ctx_a."""
    ctx_a, ctx_b, label, run_a, run_b, n_boot = t
    d = paired_difference(dict(ctx_a), run_a, run_b, n_boot) if ctx_a["folder"] == ctx_b["folder"] else \
        _paired_across_folders(ctx_a, ctx_b, run_a, run_b, n_boot)
    print(f"{label['benchmark']} split {label['split_seed']} {label['setting']:6s} {label['new_model'] or '-':30s} "
          f"n={label['n_probes']:<4} {label['a']:18s} - {label['b']:18s} d_gain={d['d_gain']:+.4f} "
          f"[{d['d_gain_ci_low']:+.4f}, {d['d_gain_ci_high']:+.4f}] p={d['d_gain_p']:.3f}", flush=True)
    return {**label, **d}


def _paired_across_folders(ctx_a, ctx_b, run_a, run_b, n_boot):
    """Runs in two folders of the same split and pool (compare_representations.py: one folder per representation)."""
    ra, rb = realized_runs(ctx_a, run_a), realized_runs(ctx_b, run_b)
    cost = ctx_a["cost"]
    c_range = (cost.min(), cost.max())
    areas = router.bootstrap_areas({"a": ra["router"], "b": rb["router"], "single": ra["single"], "oracle": ra["oracle"]},
                                   c_range, n_boot, 0)
    d_gain = areas["a"] / areas["single"] - areas["b"] / areas["single"]
    d_A = (areas["a"] - areas["b"]) / areas["oracle"]
    point = {name: router.area(router.curve(r["router"]), *c_range) for name, r in (("a", ra), ("b", rb))}
    single, oracle = router.area(router.curve(ra["single"]), *c_range), router.area(router.curve(ra["oracle"]), *c_range)
    out = {"d_gain": (point["a"] - point["b"]) / single, "d_A": (point["a"] - point["b"]) / oracle}
    for name, d in (("gain", d_gain), ("A", d_A)):
        lo, hi = np.quantile(d, [0.025, 0.975])
        frac = (d <= 0).mean()
        out.update({f"d_{name}_ci_low": lo, f"d_{name}_ci_high": hi, f"d_{name}_p": 2 * min(frac, 1 - frac),
                    f"d_{name}_boot_mean": d.mean()})
    return out


if __name__ == "__main__":
    main()
