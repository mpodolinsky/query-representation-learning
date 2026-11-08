"""Tables and figures from the results folders written by the harness (results/<timestamp>_split<seed>/results.csv).

    python analyze_handcrafted.py --benchmark llmrouterbench            # tables to analysis/, figures to analysis/figures/
    python analyze_handcrafted.py --results-root results --learned-name learned --target 0.9
    python analyze_handcrafted.py --pca --loader data:load_data          # adds the PCA views (needs the data)

Produces
  seen_table.csv / .md        gain and A per embedding (and per release epoch in replay mode): mean ± std over splits
  unseen_table.csv            per embedding, held-out model and n: gain, gain_same_probes, recovery, A (mean over probe
                              seeds, then mean ± std over splits)
  A_unseen_curves.csv         A_unseen(n) per embedding: mean over held-out models and splits (a summary; events differ)
  rq1a_ratio.csv              A(task_type) / A(other embedding) per split, incl. the learned embedding when its rows exist
  probes_to_target.csv        smallest n with A_unseen(n) >= target * A_seen (paper) and with recovery >= target
  figures/                    cost-quality curves (plots.plot_curves), gain vs probes (plots.plot_gain_vs_probes),
                              A_unseen(n) per embedding, and PCA views with --pca
Spread convention (from the harness README): across splits (reported here as ± std over split seeds), across probe
seeds (std_seeds columns) and the bootstrap interval (gain_ci_* columns, per run) are kept separate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "michal-harness"))
sys.path.insert(0, str(HERE))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import NullFormatter  # noqa: E402
import plots  # noqa: E402  (also sets the shared style)

KEYS = ["benchmark", "epoch", "embedding"]


# ---------------------------------------------------------------- loading

def load_results(root: Path, benchmark: str | None = None, embeddings: list[str] | None = None) -> pd.DataFrame:
    frames = []
    for csv in sorted(Path(root).glob("*/results.csv")):
        df = pd.read_csv(csv, dtype={"new_model": str})
        df["folder"] = str(csv.parent)
        epoch = csv.parent / "epoch.json"
        df["epoch"] = json.loads(epoch.read_text())["epoch"] if epoch.exists() else -1  # -1: full pool
        frames.append(df)
    if not frames:
        raise SystemExit(f"no results/*/results.csv under {root}")
    df = pd.concat(frames, ignore_index=True)
    df["new_model"] = df["new_model"].fillna("")
    df["unseen"] = df["new_model"] != ""
    for col in ("n_probes", "gain_same_probes", "recovery", "gain_ci_low", "gain_ci_high"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if benchmark:
        df = df[df["benchmark"] == benchmark]
    if embeddings:
        df = df[df["embedding"].isin(embeddings)]
    return df.reset_index(drop=True)


def _mean_std(df, by, cols):
    """mean and std over the rows of each group, as <col>_mean, <col>_std, plus the group size n."""
    g = df.groupby(by, dropna=False)[cols]
    out = g.mean().add_suffix("_mean").join(g.std(ddof=0).add_suffix("_std"))
    out["n"] = g.size()
    return out.reset_index()


# ---------------------------------------------------------------- tables

def seen_table(df: pd.DataFrame) -> pd.DataFrame:
    seen = df[~df["unseen"]].copy()
    seen["ci_width"] = seen["gain_ci_high"] - seen["gain_ci_low"]
    t = _mean_std(seen, KEYS, ["gain", "gain_abs", "A", "A_single_best", "k", "ci_width"])
    return t.rename(columns={"n": "n_splits"})


def format_seen(t: pd.DataFrame) -> str:
    lines = ["| benchmark | epoch | embedding | gain (mean ± std over splits) | A | A single best | k | splits |",
             "|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        lines.append(f"| {r.benchmark} | {'all models' if r.epoch == -1 else r.epoch} | {r.embedding} | "
                     f"{100 * r.gain_mean:+.2f}% ± {100 * r.gain_std:.2f} | {r.A_mean:.4f} ± {r.A_std:.4f} | "
                     f"{r.A_single_best_mean:.4f} | {r.k_mean:.0f} | {r.n_splits} |")
    return "\n".join(lines)


def unseen_tables(df: pd.DataFrame):
    """(per held-out model table, A_unseen(n) curve table). Probe seeds are averaged first, then splits."""
    un = df[df["unseen"]]
    if un.empty:
        return pd.DataFrame(), pd.DataFrame()
    cols = ["gain", "gain_same_probes", "recovery", "A"]
    per_split = _mean_std(un, KEYS + ["new_model", "n_probes", "split_seed"], cols)
    per_split = per_split.rename(columns={f"{c}_std": f"{c}_std_seeds" for c in cols}).drop(columns="n")
    means = [f"{c}_mean" for c in cols]
    table = _mean_std(per_split, KEYS + ["new_model", "n_probes"], means + [f"{c}_std_seeds" for c in cols])
    table = table.rename(columns={**{f"{c}_mean_mean": f"{c}_mean" for c in cols},
                                  **{f"{c}_mean_std": f"{c}_std_splits" for c in cols},
                                  **{f"{c}_std_seeds_mean": f"{c}_std_seeds" for c in cols}, "n": "n_splits"})
    table = table[[c for c in table.columns if not c.endswith("_std_seeds_std")]]
    curves = _mean_std(per_split, KEYS + ["n_probes"], means).rename(
        columns={**{f"{c}_mean_mean": f"{c}_mean" for c in cols}, **{f"{c}_mean_std": f"{c}_std" for c in cols},
                 "n": "n_events_x_splits"})
    return table, curves


def rq1a_ratio(df: pd.DataFrame, task_name="task_type", learned_name="learned") -> pd.DataFrame:
    """A(task type only) / A(other) per benchmark, epoch and split, then mean ± std over splits.
    The paper's RQ1a ratio is the row with other == learned_name; it appears only once those results exist."""
    seen = df[~df["unseen"]].pivot_table(index=["benchmark", "epoch", "split_seed"], columns="embedding", values="A")
    if task_name not in seen.columns:
        return pd.DataFrame()
    rows = []
    for other in [c for c in seen.columns if c != task_name]:
        ratio = (seen[task_name] / seen[other]).dropna().rename("ratio").reset_index()
        ratio["other"] = other
        rows.append(ratio)
    if not rows:
        return pd.DataFrame()
    r = _mean_std(pd.concat(rows), ["benchmark", "epoch", "other"], ["ratio"]).rename(columns={"n": "n_splits"})
    r["is_rq1a"] = r["other"] == learned_name
    if not r["is_rq1a"].any():
        print(f"note: no seen-model rows for the learned embedding (name {learned_name!r}); the RQ1a ratio "
              f"A(task_type)/A(learned) is skipped. Ratios against the other embeddings are reported instead.")
    return r


def probes_to_target(df: pd.DataFrame, target=0.9) -> pd.DataFrame:
    """Per (benchmark, epoch, embedding, held-out model, split): the smallest n whose mean-over-seeds A_unseen(n)
    reaches target * A_seen (paper definition), and the smallest n whose mean recovery reaches `target` (the harness
    decision log prefers this one). inf when no budget in the grid reaches it."""
    un = df[df["unseen"]]
    if un.empty:
        return pd.DataFrame()
    seen = df[~df["unseen"]].set_index(KEYS + ["split_seed"])[["A", "gain"]]
    per = un.groupby(KEYS + ["new_model", "split_seed", "n_probes"])[["A", "recovery"]].mean().reset_index()
    rows = []
    for key, g in per.groupby(KEYS + ["new_model", "split_seed"]):
        skey = key[:3] + key[4:]
        A_seen = seen["A"].get(skey, np.nan)
        g = g.sort_values("n_probes")
        hit_A = g.loc[g["A"] >= target * A_seen, "n_probes"]
        hit_rec = g.loc[g["recovery"] >= target, "n_probes"]
        rows.append(dict(zip(KEYS + ["new_model", "split_seed"], key), A_seen=A_seen,
                         n_to_target_A=hit_A.iloc[0] if len(hit_A) else np.inf,
                         n_to_target_recovery=hit_rec.iloc[0] if len(hit_rec) else np.inf,
                         max_n=g["n_probes"].max()))
    per_split = pd.DataFrame(rows)
    finite = lambda s: s.replace(np.inf, np.nan)
    summary = per_split.groupby(KEYS).agg(
        median_n_A=("n_to_target_A", lambda s: finite(s).median()),
        share_reached_A=("n_to_target_A", lambda s: np.isfinite(s).mean()),
        median_n_recovery=("n_to_target_recovery", lambda s: finite(s).median()),
        share_reached_recovery=("n_to_target_recovery", lambda s: np.isfinite(s).mean()),
        n_cases=("n_to_target_A", "size")).reset_index()
    summary["target"] = target
    return summary.merge(per_split, on=KEYS, how="left", suffixes=("", "_case"))


# ---------------------------------------------------------------- figures

def load_run(folder: Path, run_id: str) -> dict:
    """Rebuild the parts of an `evaluate` result that `plots.plot_curves` needs from the saved files."""
    npz = np.load(folder / "runs" / f"{run_id}.npz")
    cost = np.array(json.loads((folder / "meta.json").read_text())["cost"])
    curves = {k[len("curve_"):]: npz[k] for k in npz.files if k.startswith("curve_")}
    return {"curves": curves, "lambdas": npz["lambdas"], "cost_range": (cost.min(), cost.max())}


def figures(df: pd.DataFrame, curves: pd.DataFrame, out: Path, split=0):
    out.mkdir(parents=True, exist_ok=True)
    main = df[df["split_seed"] == split]
    for r in main[~main["unseen"]].itertuples():  # cost-quality curves of the seen runs on the main split
        fig = plots.plot_curves(load_run(Path(r.folder), f"{int(r.run):04d}"),
                                f"{r.embedding}, seen-model setting, split {split} (k = {r.k})")
        fig.savefig(out / f"curves_{r.benchmark}_epoch{r.epoch}_{r.embedding}_split{split}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
    un = main[main["unseen"]]
    for (bench, epoch, emb, new), g in un.groupby(KEYS + ["new_model"]):  # gain vs probes, the harness figure
        seen_rows = main[(~main["unseen"]) & (main["embedding"] == emb) & (main["epoch"] == epoch) & (main["benchmark"] == bench)]
        if seen_rows.empty:
            continue
        piv = g.pivot_table(index="n_probes", columns="seed", values="gain")
        same = g.pivot_table(index="n_probes", columns="seed", values="gain_same_probes")
        fig = plots.plot_gain_vs_probes(piv.index.values, piv.values, seen_rows["gain"].iloc[0], same.values,
                                        title=f"{emb}: new model {new} (split {split})")
        fig.savefig(out / f"gain_vs_probes_{bench}_epoch{epoch}_{emb}_{new}_split{split}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
    if not curves.empty:  # A_unseen(n) per embedding, averaged over held-out models and splits
        for (bench, epoch), g in curves.groupby(["benchmark", "epoch"]):
            fig, ax = plt.subplots()
            for emb, ge in g.groupby("embedding"):
                ge = ge.sort_values("n_probes")
                ax.errorbar(ge["n_probes"], ge["A_mean"], yerr=ge["A_std"], marker="o", capsize=3, label=emb)
            ax.set(xscale="log", xlabel="number of probes n", ylabel="A_unseen(n) (mean over held-out models, splits)",
                   title=f"{bench}: A against the probe budget" + ("" if epoch == -1 else f" (epoch {epoch})"))
            ax.set_xticks(sorted(g["n_probes"].unique()), [f"{int(n)}" for n in sorted(g["n_probes"].unique())], minor=False)
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.legend(frameon=False)
            fig.savefig(out / f"A_unseen_{bench}_epoch{epoch}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)


def pca_views(args, out: Path):
    """PCA views of the handcrafted space: task type panels, model quality, explained variance of the three variants."""
    from run_handcrafted import find_load_data
    from handcrafted import VARIANTS
    load_data = find_load_data(args.loader)
    for bench in ([args.benchmark] if args.benchmark else ["llmrouterbench", "routerbench"]):
        data = load_data(bench, split_seed=0)
        embs = {name: VARIANTS[name](data)(data.models)(data.queries) for name in ("task_type", "stats", "handcrafted")}
        E = embs["handcrafted"]
        Z, ratio = plots.pca_project(E, fit_idx=data.train)
        if getattr(data, "theme", None) is not None:
            plots.plot_pca_groups(Z, ratio, data.theme, f"{bench}: task type over the PCA plane (handcrafted)").savefig(
                out / f"pca_task_type_{bench}.png", dpi=150, bbox_inches="tight")
        plots.plot_pca_quality(Z[data.train], ratio, np.asarray(data.S)[data.train], data.models).savefig(
            out / f"pca_model_quality_{bench}.png", dpi=150, bbox_inches="tight")
        plots.plot_explained_variance(embs, fit_idx=data.train).savefig(
            out / f"explained_variance_{bench}.png", dpi=150, bbox_inches="tight")
        plt.close("all")


# ---------------------------------------------------------------- main

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results-root", default=str(REPO / "results"))
    p.add_argument("--benchmark", default=None, help="keep only this benchmark (default: all, tables are per benchmark)")
    p.add_argument("--embeddings", nargs="*", default=None, help="keep only these embedding names")
    p.add_argument("--out", default=str(HERE / "analysis"))
    p.add_argument("--learned-name", default="learned", help="embedding name of the learned embedding (RQ1a ratio)")
    p.add_argument("--target", type=float, default=0.9, help="probes-to-target fraction")
    p.add_argument("--main-split", type=int, default=0, help="split used for the per-run figures")
    p.add_argument("--no-figures", action="store_true")
    p.add_argument("--pca", action="store_true", help="also draw the PCA views (loads the data)")
    p.add_argument("--loader", default=None, help="for --pca: module:function giving load_data")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = load_results(Path(args.results_root), args.benchmark, args.embeddings)
    print(f"{len(df)} runs from {df['folder'].nunique()} results folders; embeddings: {sorted(df['embedding'].unique())}; "
          f"splits: {sorted(df['split_seed'].unique().tolist())}")

    seen = seen_table(df)
    seen.to_csv(out / "seen_table.csv", index=False)
    (out / "seen_table.md").write_text(format_seen(seen) + "\n")
    print("\nSeen-model setting\n" + format_seen(seen))

    table, curves = unseen_tables(df)
    table.to_csv(out / "unseen_table.csv", index=False)
    curves.to_csv(out / "A_unseen_curves.csv", index=False)
    if not curves.empty:
        print("\nA_unseen(n), mean over held-out models and splits")
        print(curves.pivot_table(index=["benchmark", "epoch", "n_probes"], columns="embedding", values="A_mean").round(4).to_string())

    ratio = rq1a_ratio(df, learned_name=args.learned_name)
    ratio.to_csv(out / "rq1a_ratio.csv", index=False)
    if not ratio.empty:
        print("\nA(task_type) / A(other), seen-model setting")
        print(ratio.to_string(index=False))

    ptt = probes_to_target(df, args.target)
    ptt.to_csv(out / "probes_to_target.csv", index=False)
    if not ptt.empty:
        print(f"\nProbes to target ({args.target:.0%}): median n over held-out models and splits")
        print(ptt.drop_duplicates(KEYS)[KEYS + ["median_n_A", "share_reached_A", "median_n_recovery",
                                                 "share_reached_recovery", "n_cases"]].to_string(index=False))

    if not args.no_figures:
        figures(df, curves, out / "figures", split=args.main_split)
        if args.pca:
            pca_views(args, out / "figures")
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
