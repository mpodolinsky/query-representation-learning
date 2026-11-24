"""Tables and figures from the results folders written by the harness (results/<timestamp>_split<seed>/results.csv,
plus the run script's k_tuning.csv next to it).

    python analyze_handcrafted.py --benchmark llmrouterbench            # tables to analysis/, figures to analysis/figures/
    python analyze_handcrafted.py --results-root results --learned-name learned --target 0.9
    python analyze_handcrafted.py --pca --diagnostics                    # adds the PCA views and the diagnostics (needs the data)

Produces
  seen_table.csv / .md        gain, A and the tuned k per embedding (and per release epoch in replay mode): mean ± std
                              over splits; `k_edge` marks an embedding whose tuned k hit the edge of the grid on any split
  unseen_table.csv            per embedding, held-out model and n: gain, gain_same_probes, recovery, A (mean over probe
                              seeds, then mean ± std over splits)
  A_unseen_curves.csv         gain(n), recovery(n), A_unseen(n) per embedding: mean over held-out models and splits
  rq1a_ratio.csv              A(task_type_<levels>) / A(other embedding) per split, for every task-type-only variant
                              (per level combination), incl. the learned embedding when its rows exist
  probes_to_target.csv        smallest n with recovery >= target (the headline), and with A_unseen(n) >= target * A_seen
                              (the paper's wording; vacuous here, see README.md, "What the analysis produces")
  k_tuning_summary.csv        per embedding: the tuned k per split and how often it sat at the edge of the grid
  figures/                    cost-quality curves (plots.plot_curves), gain vs probes per held-out model
                              (plots.plot_gain_vs_probes), gain vs probes per variant (negative region shaded),
                              A_unseen(n) per embedding, and PCA views with --pca
  diagnostics (--diagnostics) correlation matrix of the statistics block on the training split (CSV + heatmap), the
                              strongly correlated pairs, its explained variance against the PCA-whitened block, and
                              how well the statistics predict the theme (and Level 1): logistic regression and a kNN
                              classifier, train -> test accuracy against the majority class, confusion matrices
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
from matplotlib.ticker import NullFormatter, PercentFormatter  # noqa: E402
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
        tuning = csv.parent / "k_tuning.csv"
        if tuning.exists():  # the run script's record of the k tuning (run id -> grid, edge flags)
            t = pd.read_csv(tuning, dtype={"run": str, "new_model": str})[["run", "k_grid", "tuned", "best_k_at_edge", "selected_k_at_edge"]]
            df["run"] = df["run"].map(lambda r: f"{int(r):04d}")
            df = df.merge(t, on="run", how="left")
        frames.append(df)
    if not frames:
        raise SystemExit(f"no results/*/results.csv under {root}")
    df = pd.concat(frames, ignore_index=True)
    df["new_model"] = df["new_model"].fillna("")
    df["unseen"] = df["new_model"] != ""
    for col in ("n_probes", "gain_same_probes", "recovery", "gain_ci_low", "gain_ci_high"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("best_k_at_edge", "selected_k_at_edge"):
        df[col] = df[col].astype("boolean").fillna(False).astype(bool) if col in df else False
    df["k_edge"] = df["best_k_at_edge"] | df["selected_k_at_edge"]
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
    ks = seen.groupby(KEYS)["k"].agg(lambda s: " ".join(str(int(k)) for k in s)).rename("k_per_split")
    edge = seen.groupby(KEYS)["k_edge"].any().rename("k_edge")
    return t.merge(ks.reset_index(), on=KEYS).merge(edge.reset_index(), on=KEYS).rename(columns={"n": "n_splits"})


def format_seen(t: pd.DataFrame) -> str:
    lines = ["| benchmark | epoch | embedding | gain (mean ± std over splits) | A | A single best | k per split | splits |",
             "|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        lines.append(f"| {r.benchmark} | {'all models' if r.epoch == -1 else r.epoch} | {r.embedding} | "
                     f"{100 * r.gain_mean:+.2f}% ± {100 * r.gain_std:.2f} | {r.A_mean:.4f} ± {r.A_std:.4f} | "
                     f"{r.A_single_best_mean:.4f} | {r.k_per_split}{' †' if r.k_edge else ''} | {r.n_splits} |")
    lines.append("")
    lines.append("† the tuned k hit the edge of the k grid on at least one split (the harness's `select_k` warning, "
                 "or the selected k is the grid's minimum or maximum).")
    return "\n".join(lines)


def k_tuning_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per embedding (seen and unseen runs separately): the tuned k values and the share of runs at the grid edge."""
    rows = []
    for (bench, epoch, emb, unseen), g in df.groupby(KEYS + ["unseen"]):
        rows.append({"benchmark": bench, "epoch": epoch, "embedding": emb, "setting": "unseen" if unseen else "seen",
                     "n_runs": len(g), "k_grid": g["k_grid"].dropna().iloc[0] if "k_grid" in g and g["k_grid"].notna().any() else "",
                     "k_values": " ".join(f"{int(k)}x{n}" for k, n in g["k"].value_counts().sort_index().items()),
                     "share_best_k_at_edge": g["best_k_at_edge"].mean(), "share_selected_k_at_edge": g["selected_k_at_edge"].mean()})
    return pd.DataFrame(rows)


def unseen_tables(df: pd.DataFrame):
    """(per held-out model table, curves table). Probe seeds are averaged first, then splits."""
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


def rq1a_ratio(df: pd.DataFrame, task_prefix="task_type", learned_name="learned") -> pd.DataFrame:
    """A(task-type-only variant) / A(other) per benchmark, epoch and split, then mean ± std over splits, for every
    task-type-only variant (embedding names starting with `task_prefix`, i.e. one row set per level combination).
    The paper's RQ1a ratio is the row with other == learned_name; it appears only once those results exist."""
    seen = df[~df["unseen"]].pivot_table(index=["benchmark", "epoch", "split_seed"], columns="embedding", values="A")
    tasks = [c for c in seen.columns if c.startswith(task_prefix)]
    others = [c for c in seen.columns if not c.startswith(task_prefix)]
    rows = []
    for task in tasks:
        for other in others:
            ratio = (seen[task] / seen[other]).dropna().rename("ratio").reset_index()
            ratio["task_variant"], ratio["other"] = task, other
            rows.append(ratio)
    if not rows:
        return pd.DataFrame()
    r = _mean_std(pd.concat(rows), ["benchmark", "epoch", "task_variant", "other"], ["ratio"]).rename(columns={"n": "n_splits"})
    r["is_rq1a"] = r["other"] == learned_name
    if not r["is_rq1a"].any():
        print(f"note: no seen-model rows for the learned embedding (name {learned_name!r}); the RQ1a ratio "
              f"A(task_type)/A(learned) is skipped. Ratios against the other embeddings are reported instead.")
    return r


def probes_to_target(df: pd.DataFrame, target=0.9) -> pd.DataFrame:
    """Per (benchmark, epoch, embedding, held-out model, split): the smallest n whose mean-over-seeds recovery reaches
    `target` (headline: recovery = unseen gain / seen gain, both over the same single best), and the smallest n whose
    mean-over-seeds A_unseen(n) reaches target * A_seen (the paper's wording). The second is vacuous whenever the
    single best alone already has A_single_best >= target * A_seen, which `single_best_ratio` reports: then every n,
    even n = 1, "reaches the target" without routing. inf when no budget in the grid reaches it."""
    un = df[df["unseen"]]
    if un.empty:
        return pd.DataFrame()
    seen = df[~df["unseen"]].set_index(KEYS + ["split_seed"])[["A", "A_single_best", "gain"]]
    per = un.groupby(KEYS + ["new_model", "split_seed", "n_probes"])[["A", "recovery"]].mean().reset_index()
    rows = []
    for key, g in per.groupby(KEYS + ["new_model", "split_seed"]):
        skey = key[:3] + key[4:]
        A_seen = seen["A"].get(skey, np.nan)
        A_single = seen["A_single_best"].get(skey, np.nan)
        g = g.sort_values("n_probes")
        hit_rec = g.loc[g["recovery"] >= target, "n_probes"]
        hit_A = g.loc[g["A"] >= target * A_seen, "n_probes"]
        rows.append(dict(zip(KEYS + ["new_model", "split_seed"], key), A_seen=A_seen, single_best_ratio=A_single / A_seen,
                         n_to_target_recovery=hit_rec.iloc[0] if len(hit_rec) else np.inf,
                         n_to_target_A=hit_A.iloc[0] if len(hit_A) else np.inf,
                         max_n=g["n_probes"].max()))
    per_split = pd.DataFrame(rows)
    finite = lambda s: s.replace(np.inf, np.nan)
    summary = per_split.groupby(KEYS).agg(
        median_n_recovery=("n_to_target_recovery", lambda s: finite(s).median()),
        share_reached_recovery=("n_to_target_recovery", lambda s: np.isfinite(s).mean()),
        median_n_A=("n_to_target_A", lambda s: finite(s).median()),
        share_reached_A=("n_to_target_A", lambda s: np.isfinite(s).mean()),
        single_best_ratio=("single_best_ratio", "mean"),
        n_cases=("n_to_target_recovery", "size")).reset_index()
    summary["target"] = target
    summary["A_target_vacuous"] = summary["single_best_ratio"] >= target
    return summary.merge(per_split, on=KEYS, how="left", suffixes=("", "_case"))


# ---------------------------------------------------------------- figures

def load_run(folder: Path, run_id: str) -> dict:
    """Rebuild the parts of an `evaluate` result that `plots.plot_curves` needs from the saved files."""
    npz = np.load(folder / "runs" / f"{run_id}.npz")
    cost = np.array(json.loads((folder / "meta.json").read_text())["cost"])
    curves = {k[len("curve_"):]: npz[k] for k in npz.files if k.startswith("curve_")}
    return {"curves": curves, "lambdas": npz["lambdas"], "cost_range": (cost.min(), cost.max())}


def plot_gain_vs_probes_by_variant(df: pd.DataFrame, bench: str, epoch=-1):
    """One panel per embedding with unseen runs: the gain over the full-information single best against the probe
    budget, one thin line per held-out model (mean over probe seeds and splits), the mean over held-out models in
    bold, the seen-model gain dashed, and the region below zero (routing worse than the single best) shaded."""
    sub = df[(df["benchmark"] == bench) & (df["epoch"] == epoch)]
    un = sub[sub["unseen"]]
    if un.empty:
        return None
    embs = sorted(un["embedding"].unique())
    per_model = un.groupby(["embedding", "new_model", "n_probes"])["gain"].mean().reset_index()
    seen_gain = sub[~sub["unseen"]].groupby("embedding")["gain"].mean()
    ncols = min(3, len(embs))
    nrows = -(-len(embs) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.2 * nrows), sharex=True, sharey=True, squeeze=False,
                             layout="constrained")
    for ax in axes.flat[len(embs):]:
        ax.set_visible(False)
    lo = min(per_model["gain"].min(), 0)
    for ax, emb in zip(axes.flat, embs):
        g = per_model[per_model["embedding"] == emb]
        for _, gm in g.groupby("new_model"):
            gm = gm.sort_values("n_probes")
            ax.plot(gm["n_probes"], gm["gain"], color=plots.MUTED, linewidth=0.8, alpha=0.5)
        mean = g.groupby("n_probes")["gain"].mean()
        ax.plot(mean.index, mean.values, color=plots.BLUE, linewidth=2.4, label="mean over held-out models")
        if emb in seen_gain:
            ax.axhline(seen_gain[emb], color=plots.INK, linewidth=1, linestyle="--", label="seen-model gain")
        ax.axhspan(lo * 1.15, 0, color=plots.ORANGE, alpha=0.12, linewidth=0)
        ax.axhline(0, color=plots.ORANGE, linewidth=1)
        ax.set(xscale="log", title=emb)
        ax.title.set_fontsize(10)
        ax.set_xticks(sorted(g["n_probes"].unique()), [f"{int(n)}" for n in sorted(g["n_probes"].unique())])
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.tick_params(labelsize=8)
    axes.flat[0].yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    axes.flat[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.supxlabel("number of probes n", fontsize=9)
    fig.supylabel("gain over the full-information single best", fontsize=9)
    fig.suptitle(f"{bench}: unseen-model gain against the probe budget, per held-out model (thin) and on average (bold); "
                 f"shaded: the router does worse than the single best", fontsize=10)
    return fig


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
        fig.savefig(out / f"gain_vs_probes_{bench}_epoch{epoch}_{emb}_{new.replace('/', '_')}_split{split}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
    for (bench, epoch) in df[df["unseen"]].groupby(["benchmark", "epoch"]).groups:  # per variant, all splits
        fig = plot_gain_vs_probes_by_variant(df, bench, epoch)
        if fig is not None:
            fig.savefig(out / f"gain_vs_probes_by_variant_{bench}_epoch{epoch}.png", dpi=150, bbox_inches="tight")
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


# ---------------------------------------------------------------- data-side views (need the loader)

def _load(args, bench, split=0):
    """The data of one benchmark and split, and the task labels the run script would attach (None if there are none)."""
    from run_handcrafted import find_load_data, labels_for
    data = find_load_data(args.loader)(bench, split_seed=split)
    return data, labels_for(args.level_labels, bench, data)


def _benches(args):
    return [args.benchmark] if args.benchmark else ["llmrouterbench", "routerbench"]


def pca_views(args, out: Path):
    """PCA views of the handcrafted space: task type panels, model quality, explained variance of the three variants."""
    from handcrafted import VARIANTS
    for bench in _benches(args):
        data, labels = _load(args, bench)
        kw = dict(tokenizer=args.tokenizer, **({"labels": labels} if labels else {}))
        embs = {name: VARIANTS[name](data, **kw)(data.models)(data.queries) for name in ("task_type_L1", "stats", "handcrafted")}
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


def predict_labels_from_stats(Z, data, targets: dict, k=50, seed=0) -> tuple[pd.DataFrame, dict]:
    """How well the standardized statistics predict each label in `targets` (name -> labels aligned with the
    queries): multinomial logistic regression and a k-nearest-neighbor classifier (the router's own estimator),
    fitted on data.train and scored on data.test, against the majority class of the training split.
    Returns the summary rows and, per target, the row-normalized confusion matrix (rows = true class) on test."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix
    from sklearn.neighbors import KNeighborsClassifier
    tr, te = np.asarray(data.train), np.asarray(data.test)
    rows, confusions = [], {}
    for name, y in targets.items():
        y = np.asarray(y, dtype=object).astype(str)
        classes = sorted(set(y[tr]))
        majority = max(classes, key=lambda c: (y[tr] == c).sum())
        logit = LogisticRegression(max_iter=3000, random_state=seed).fit(Z[tr], y[tr])
        knn = KNeighborsClassifier(n_neighbors=k).fit(Z[tr], y[tr])
        pred = logit.predict(Z[te])
        rows.append({"target": name, "n_classes": len(classes), "n_train": len(tr), "n_test": len(te),
                     "majority_class": majority, "majority_test_acc": float((y[te] == majority).mean()),
                     "logit_train_acc": float((logit.predict(Z[tr]) == y[tr]).mean()),
                     "logit_test_acc": float((pred == y[te]).mean()),
                     f"knn{k}_test_acc": float((knn.predict(Z[te]) == y[te]).mean())})
        cm = confusion_matrix(y[te], pred, labels=classes, normalize="true")
        confusions[name] = pd.DataFrame(cm, index=classes, columns=classes)
    return pd.DataFrame(rows), confusions


def plot_confusion(cm: pd.DataFrame, title: str):
    n = len(cm)
    fig, ax = plt.subplots(figsize=(0.55 * n + 2.5, 0.5 * n + 2))
    im = ax.imshow(cm.values, cmap=plots.SEQ, vmin=0, vmax=1)
    ax.set_xticks(range(n), cm.columns, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(n), cm.index, fontsize=7)
    ax.set(xlabel="predicted", ylabel="true")
    ax.grid(False)
    for i in range(n):
        for j in range(n):
            if cm.values[i, j] >= 0.1:
                ax.text(j, i, f"{cm.values[i, j]:.2f}", ha="center", va="center", fontsize=6,
                        color=plots.SURFACE if cm.values[i, j] > 0.6 else plots.INK)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="share of the true class (test split)")
    ax.set_title(title, fontsize=10)
    return fig


def stats_diagnostics(args, out: Path):
    """Correlation structure of the numeric block on the training split: matrix (CSV + heatmap), strongly correlated
    pairs, the cumulative explained variance of the z-scored block against the whitened one; and how well the
    statistics predict the theme and Level 1 (summary CSV, confusion matrices as CSV and heatmaps)."""
    from matplotlib.colors import LinearSegmentedColormap
    from handcrafted import FEATURE_NAMES, HandcraftedEmbedding
    diverging = LinearSegmentedColormap.from_list("div", [plots.ORANGE, "#e9e8e4", plots.BLUE])  # two poles, neutral middle
    summaries = []
    for bench in _benches(args):
        data, labels = _load(args, bench)
        plain = HandcraftedEmbedding(data, use_task_type=False, tokenizer=args.tokenizer)
        white = HandcraftedEmbedding(data, use_task_type=False, whiten=True, tokenizer=args.tokenizer)
        Z_all = plain.stats_block()
        Z, W = Z_all[data.train], white.stats_block()[data.train]
        with np.errstate(invalid="ignore", divide="ignore"):  # a constant feature has no correlation: shown as 0
            corr = pd.DataFrame(np.corrcoef(Z, rowvar=False), index=FEATURE_NAMES, columns=FEATURE_NAMES).fillna(0.0)
        corr.to_csv(out / f"stats_correlation_{bench}.csv")
        pairs = [(a, b, corr.loc[a, b]) for i, a in enumerate(FEATURE_NAMES) for b in FEATURE_NAMES[i + 1:] if abs(corr.loc[a, b]) >= 0.7]
        pairs.sort(key=lambda t: -abs(t[2]))
        print(f"\n{bench}: statistics block on {len(data.train)} training queries; |r| >= 0.7 pairs:")
        for a, b, r in pairs:
            print(f"  {a:22s} {b:22s} r = {r:+.2f}")
        print(f"  whitened block: {W.shape[1]} components, max |off-diagonal correlation| = "
              f"{np.abs(np.corrcoef(W, rowvar=False) - np.eye(W.shape[1])).max():.2e}")
        fig, ax = plt.subplots(figsize=(7.5, 6.5))
        im = ax.imshow(corr.values, cmap=diverging, vmin=-1, vmax=1)
        ax.set_xticks(range(len(FEATURE_NAMES)), FEATURE_NAMES, rotation=60, ha="right", fontsize=8)
        ax.set_yticks(range(len(FEATURE_NAMES)), FEATURE_NAMES, fontsize=8)
        ax.grid(False)
        for i in range(len(FEATURE_NAMES)):          # label only the strong cells, so the picture stays readable
            for j in range(len(FEATURE_NAMES)):
                if i != j and abs(corr.values[i, j]) >= 0.5:
                    ax.text(j, i, f"{corr.values[i, j]:+.1f}", ha="center", va="center", fontsize=6.5, color=plots.INK)
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="Pearson correlation (training split)")
        ax.set_title(f"{bench}: correlation of the z-scored statistics", fontsize=11)
        fig.savefig(out / f"stats_correlation_{bench}.png", dpi=150, bbox_inches="tight")
        plots.plot_explained_variance({"stats (z-scored)": Z, "stats (whitened)": W}, max_components=Z.shape[1]).savefig(
            out / f"stats_explained_variance_{bench}.png", dpi=150, bbox_inches="tight")
        plt.close("all")

        # do the statistics know the task type? theme (the dataset) and, when labeled, Level 1
        targets = {}
        if getattr(data, "theme", None) is not None:
            targets["theme"] = data.theme
        if labels and labels.get(1) is not None:
            targets["task_level1"] = labels[1]
        if targets:
            summary, confusions = predict_labels_from_stats(Z_all, data, targets)
            summary.insert(0, "benchmark", bench)
            summaries.append(summary)
            print(f"\n{bench}: the 15 statistics as a classifier of the label (train -> test):")
            print(summary.drop(columns="benchmark").to_string(index=False))
            for name, cm in confusions.items():
                cm.to_csv(out / f"stats_predict_{name}_{bench}.csv")
                acc = summary.loc[summary["target"] == name, "logit_test_acc"].iloc[0]
                plot_confusion(cm, f"{bench}: {name} predicted from the statistics (logistic regression, test accuracy {acc:.0%})").savefig(
                    out / "figures" / f"stats_predict_{name}_{bench}.png", dpi=150, bbox_inches="tight")
                plt.close("all")
    if summaries:
        pd.concat(summaries).to_csv(out / "stats_predict_labels.csv", index=False)


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
    p.add_argument("--diagnostics", action="store_true",
                   help="correlation, whitening and label-prediction diagnostics of the statistics block (loads the data)")
    p.add_argument("--loader", default=None, help="for --pca / --diagnostics: module:function giving load_data")
    p.add_argument("--level-labels", default="auto", help="for --pca / --diagnostics: as in run_handcrafted.py")
    p.add_argument("--tokenizer", default="tiktoken:cl100k_base", help="for --pca / --diagnostics")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out = Path(args.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    df = load_results(Path(args.results_root), args.benchmark, args.embeddings)
    print(f"{len(df)} runs from {df['folder'].nunique()} results folders; embeddings: {sorted(df['embedding'].unique())}; "
          f"splits: {sorted(df['split_seed'].unique().tolist())}")

    seen = seen_table(df)
    seen.to_csv(out / "seen_table.csv", index=False)
    (out / "seen_table.md").write_text(format_seen(seen) + "\n")
    print("\nSeen-model setting\n" + format_seen(seen))
    k_tuning_summary(df).to_csv(out / "k_tuning_summary.csv", index=False)

    table, curves = unseen_tables(df)
    table.to_csv(out / "unseen_table.csv", index=False)
    curves.to_csv(out / "A_unseen_curves.csv", index=False)
    if not curves.empty:
        print("\nA_unseen(n), mean over held-out models and splits")
        print(curves.pivot_table(index=["benchmark", "epoch", "n_probes"], columns="embedding", values="A_mean").round(4).to_string())
        print("\nrecovery(n), mean over held-out models and splits")
        print(curves.pivot_table(index=["benchmark", "epoch", "n_probes"], columns="embedding", values="recovery_mean").round(3).to_string())

    ratio = rq1a_ratio(df, learned_name=args.learned_name)
    ratio.to_csv(out / "rq1a_ratio.csv", index=False)
    if not ratio.empty:
        print("\nA(task-type-only variant) / A(other), seen-model setting, per level combination")
        print(ratio.to_string(index=False))

    ptt = probes_to_target(df, args.target)
    ptt.to_csv(out / "probes_to_target.csv", index=False)
    if not ptt.empty:
        print(f"\nProbes to target (recovery >= {args.target:.0%}): median n over held-out models and splits")
        print(ptt.drop_duplicates(KEYS)[KEYS + ["median_n_recovery", "share_reached_recovery", "single_best_ratio",
                                                 "A_target_vacuous", "n_cases"]].to_string(index=False))

    if not args.no_figures:
        figures(df, curves, out / "figures", split=args.main_split)
        if args.pca:
            pca_views(args, out / "figures")
    if args.diagnostics:
        stats_diagnostics(args, out)
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
