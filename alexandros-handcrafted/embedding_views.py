"""PCA and t-SNE views of every representation, colored by task type (theme, Level 1, Level 2), and the numbers
behind the question "is the embedding just encoding the task type?".

Inputs: the final-pool embeddings exported by compare_representations.py (results_compare/embeddings/<benchmark>/
split<k>/<name>.npy with labels.npz), or --from-variants to compute the handcrafted variants from the data directly.

For each representation and label level:
  figures  PCA small multiples (one panel per category, the category in blue over all queries in gray, the harness
           style) and t-SNE small multiples on a fixed random subsample;
  numbers  kNN label purity (share of a test query's 10 nearest training neighbours with the same label: what the
           router's own estimator sees), a linear probe (multinomial logistic regression, train -> test accuracy),
           the majority-class rate, and the silhouette of the labels in the embedding (subsample).
  A representation whose linear-probe accuracy and purity are at the task-type one-hot's level, and whose PCA panels
  separate by category, is "just task type"; one that scores higher on the routing metrics with similar purity
  carries information beyond the label.

    python embedding_views.py --benchmark llmrouterbench                      # everything exported for split 0
    python embedding_views.py --benchmark routerbench --from-variants stats handcrafted task_type_L1
    python embedding_views.py --names frozen regression --labels task_level1 --no-tsne
Outputs: --out/views/<benchmark>_<name>_{pca,tsne}_<label>.png and --out/label_structure.csv."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for p in (REPO, REPO / "michal-harness", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import plots  # noqa: E402  (shared style)

LABELS = ["theme", "task_level1", "task_level2"]


# ---------------------------------------------------------------- inputs

def load_exported(folder: Path, names=None):
    """{name: E} and the labels dict from an embeddings folder written by compare_representations.py."""
    labels = dict(np.load(folder / "labels.npz", allow_pickle=False))
    files = sorted(folder.glob("*.npy"))
    if names:
        files = [folder / f"{n}.npy" for n in names if (folder / f"{n}.npy").exists()]
    return {f.stem: np.load(f) for f in files}, labels


def from_variants(benchmark, split, names, args):
    """Compute the handcrafted variants from the data (no run needed) in the exported format."""
    from handcrafted import VARIANTS
    from run_handcrafted import find_load_data, labels_for
    data = find_load_data(args.loader)(benchmark, split_seed=split)
    labs = labels_for(args.level_labels, benchmark, data)
    kw = dict(tokenizer=args.tokenizer, **({"labels": labs} if labs else {}))
    embs = {n: np.asarray(VARIANTS[n](data, **kw)(data.models)(data.queries), dtype=np.float32) for n in names}
    labels = {"theme": np.asarray(data.theme, dtype=str), "train": data.train, "val": data.val, "test": data.test}
    for l in (1, 2):
        if labs and labs.get(l) is not None:
            labels[f"task_level{l}"] = np.asarray(labs[l], dtype=str)
    return embs, labels


# ---------------------------------------------------------------- numbers

def knn_purity(E, labels, train, test, k=10):
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=min(k, len(train))).fit(E[train])
    idx = nn.kneighbors(E[test], return_distance=False)
    return float((labels[train][idx] == labels[test][:, None]).mean())


def linear_probe(E, labels, train, test, seed=0):
    import warnings
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler().fit(E[train])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        clf = LogisticRegression(max_iter=1000, C=1.0, random_state=seed).fit(sc.transform(E[train]), labels[train])
    return float((clf.predict(sc.transform(E[test])) == labels[test]).mean())


def silhouette(E, labels, sample=3000, seed=0):
    from sklearn.metrics import silhouette_score
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(E), min(sample, len(E)), replace=False)
    if len(np.unique(labels[idx])) < 2:
        return float("nan")
    return float(silhouette_score(E[idx], labels[idx]))


def label_structure(name, E, labels, which, benchmark, split):
    rows = []
    train, test = labels["train"], labels["test"]
    for lab in which:
        if lab not in labels:
            continue
        y = labels[lab].astype(str)
        counts = pd.Series(y[train]).value_counts()
        rows.append({"benchmark": benchmark, "split": split, "representation": name, "label": lab, "d": E.shape[1],
                     "n_classes": int(counts.size), "majority": float(counts.iloc[0] / counts.sum()),
                     "knn_purity_k10": knn_purity(E, y, train, test), "linear_probe_acc": linear_probe(E, y, train, test),
                     "silhouette": silhouette(E, y)})
    return rows


# ---------------------------------------------------------------- figures

def _panels(Z, labels, title, axis, max_groups=12, ncols=4):
    """Small multiples in the harness style: each panel one category in blue over every point in gray."""
    labels = np.asarray(labels).astype(str)
    present, counts = np.unique(labels, return_counts=True)
    order = present[np.argsort(-counts, kind="stable")][:max_groups]
    n = len(order)
    rows, ncols = -(-n // ncols), min(n, ncols)
    fig, axes = plt.subplots(rows, ncols, figsize=(2.6 * ncols, 2.5 * rows), squeeze=False, sharex=True, sharey=True)
    keep = np.arange(len(Z)) if len(Z) <= 20_000 else np.sort(np.random.default_rng(0).choice(len(Z), 20_000, replace=False))
    for ax, g in zip(axes.flat, order):
        mask = labels == g
        ax.scatter(*Z[keep].T, s=3, color=plots.FAINT, linewidths=0, rasterized=True)
        ax.scatter(*Z[keep][mask[keep]].T, s=4, color=plots.BLUE, linewidths=0, rasterized=True)
        ax.set_title(f"{g[:28]} (n = {mask.sum()})", fontsize=8)
        ax.set_xticks([]), ax.set_yticks([])
        ax.grid(False)
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel(axis[0], fontsize=8)
    for row in axes:
        row[0].set_ylabel(axis[1], fontsize=8)
    shown = f" (largest {max_groups} of {len(present)})" if len(present) > max_groups else ""
    fig.suptitle(title + shown, fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def pca_figure(E, labels, lab, name, benchmark):
    Z, ratio = plots.pca_project(E, fit_idx=labels["train"])
    axis = (f"PC1 ({ratio[0]:.0%})", f"PC2 ({ratio[1]:.0%})")
    return _panels(Z, labels[lab], f"{benchmark}: {name}, PCA by {lab}", axis)


def tsne_coords(E, sample, seed=0, perplexity=30):
    from sklearn.manifold import TSNE
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(len(E), min(sample, len(E)), replace=False))
    X = E[idx]
    if X.shape[1] > 50:  # PCA to 50 dimensions first, the usual t-SNE preprocessing
        from sklearn.decomposition import PCA
        X = PCA(n_components=50, random_state=seed).fit_transform(X)
    Z = TSNE(n_components=2, init="pca", perplexity=min(perplexity, max(5, len(idx) // 4)), random_state=seed).fit_transform(X)
    return idx, Z


# ---------------------------------------------------------------- main

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--embeddings", default=str(REPO / "results_compare" / "embeddings"))
    p.add_argument("--benchmark", nargs="+", default=["llmrouterbench", "routerbench"])
    p.add_argument("--split", type=int, default=0)
    p.add_argument("--names", nargs="*", default=None, help="representations to show (default: all exported)")
    p.add_argument("--from-variants", nargs="*", default=None, help="handcrafted variants computed from the data")
    p.add_argument("--labels", nargs="+", default=LABELS, choices=LABELS)
    p.add_argument("--sample", type=int, default=5000, help="points in the t-SNE")
    p.add_argument("--no-tsne", action="store_true")
    p.add_argument("--no-figures", action="store_true")
    p.add_argument("--max-groups", type=int, default=12)
    p.add_argument("--out", default=str(HERE / "analysis_compare"))
    p.add_argument("--loader", default=None)
    p.add_argument("--level-labels", default="auto")
    p.add_argument("--tokenizer", default="tiktoken:cl100k_base")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out = Path(args.out)
    views = out / "views"
    views.mkdir(parents=True, exist_ok=True)
    rows = []
    for benchmark in args.benchmark:
        folder = Path(args.embeddings) / benchmark / f"split{args.split}"
        embs, labels = {}, None
        if folder.exists() and (folder / "labels.npz").exists():
            embs, labels = load_exported(folder, args.names)
        if args.from_variants:
            more, labs2 = from_variants(benchmark, args.split, args.from_variants, args)
            embs.update(more)
            labels = labels or labs2
        if not embs:
            print(f"{benchmark}: nothing to show (no exported embeddings under {folder}, no --from-variants)")
            continue
        for name, E in embs.items():
            E = np.asarray(E, dtype=np.float64)
            print(f"{benchmark}: {name} {E.shape}", flush=True)
            rows += label_structure(name, E, labels, args.labels, benchmark, args.split)
            if args.no_figures:
                continue
            for lab in args.labels:
                if lab not in labels:
                    continue
                fig = pca_figure(E, labels, lab, name, benchmark)
                fig.savefig(views / f"{benchmark}_{name}_pca_{lab}.png", dpi=130)
                plt.close(fig)
            if not args.no_tsne:
                idx, Z = tsne_coords(E, args.sample)
                for lab in args.labels:
                    if lab not in labels:
                        continue
                    fig = _panels(Z, labels[lab][idx], f"{benchmark}: {name}, t-SNE by {lab} ({len(idx)} queries)",
                                  ("t-SNE 1", "t-SNE 2"), args.max_groups)
                    fig.savefig(views / f"{benchmark}_{name}_tsne_{lab}.png", dpi=130)
                    plt.close(fig)
    table = pd.DataFrame(rows)
    path = out / "label_structure.csv"
    if path.exists():  # merge with earlier runs (other benchmarks / representations)
        old = pd.read_csv(path)
        keys = ["benchmark", "split", "representation", "label"]
        old = old.merge(table[keys], on=keys, how="left", indicator=True).query("_merge == 'left_only'").drop(columns="_merge")
        table = pd.concat([old, table], ignore_index=True)
    table.sort_values(["benchmark", "label", "representation"]).to_csv(path, index=False)
    if rows:
        print(table.sort_values(["benchmark", "label", "representation"]).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"written to {out}")


if __name__ == "__main__":
    main()
