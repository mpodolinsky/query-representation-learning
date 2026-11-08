"""Shared plotting: one style for every figure. Each function takes arrays or `evaluate` results and returns the Figure."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator, PercentFormatter
from sklearn.decomposition import PCA

# categorical slots 1-3 (a scatter keeps to three colors), an ordinal ramp for k, a sequential ramp, neutral inks
SERIES = {"router": "#2a78d6", "single_best": "#eb6834", "single_best_probes": "#eb6834", "oracle": "#1baf7a"}
BLUE, ORANGE = SERIES["router"], SERIES["single_best"]
BLUES = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # light to dark, for up to 4 values of k
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#cde2fb", "#3987e5", "#0d366b"])
INK, MUTED, SURFACE, FAINT = "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d2"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e4e3df", "grid.linewidth": 0.6, "lines.linewidth": 2,
                     "figure.figsize": (6.5, 4)})


# ---------------------------------------------------------------- cost-quality curves

def _curve_axes(res, title):
    fig, ax = plt.subplots()
    ax.set(xlabel="mean cost per query", ylabel="mean quality (observed test score)", xscale="log",
           xlim=res["cost_range"], title=title)
    return fig, ax


def _label_end(ax, curve, text, below=False):
    # label the λ = 0 end of a curve
    ax.annotate(text, curve[0], xytext=(-4, -20 if below else 8), textcoords="offset points",
                color=INK, fontsize=9, ha="right")


def plot_curves(res, title):
    """Cost-quality curves of the router, the single best and the oracle returned by `evaluate`."""
    fig, ax = _curve_axes(res, title)
    for name, c in res["curves"].items():
        label = "single best, same probes" if name == "single_best_probes" else name.replace("_", " ")
        ax.plot(c[:, 0], c[:, 1], color=SERIES[name], label=label, linestyle="--" if name == "single_best_probes" else "-")
        if name != "single_best_probes":
            _label_end(ax, c, label, below=name == "single_best")
    ax.legend(frameon=False, loc="lower right")
    return fig


def plot_curves_by_k(results, selected, title):
    """`results` maps k -> `evaluate` result. Router curves are shaded light to dark by k (up to 4 values) and the
    selected k is thicker. The single best and the oracle do not depend on k."""
    assert len(results) <= len(BLUES)
    fig, ax = _curve_axes(results[selected], title)
    for k, shade in zip(sorted(results), BLUES):
        c = results[k]["curves"]["router"]
        ax.plot(c[:, 0], c[:, 1], color=shade, linewidth=3.2 if k == selected else 1.6,
                label=f"router, k = {k}" + (" (selected)" if k == selected else ""))
    for name in ("single_best", "oracle"):
        c = results[selected]["curves"][name]
        ax.plot(c[:, 0], c[:, 1], color=SERIES[name], label=name.replace("_", " "))
        _label_end(ax, c, name.replace("_", " "), below=name == "single_best")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    return fig


def plot_gain_vs_probes(n_grid, gains, seen_gain, gains_same_probes=None, title="Unseen-model gain against probe budget"):
    """`gains` has shape (len(n_grid), n_seeds), the gain over the full-information single best: the mean over seeds
    as a line, min to max as a band. `gains_same_probes` (same shape) optionally adds the gain over the single best
    that only knows the new model from the same probes, as a dashed line."""
    gains = np.asarray(gains)
    fig, ax = plt.subplots()
    ax.plot(n_grid, gains.mean(1), color=BLUE, label="over the full-information single best")
    ax.fill_between(n_grid, gains.min(1), gains.max(1), color=BLUE, alpha=0.15, linewidth=0)
    if gains_same_probes is not None:
        ax.plot(n_grid, np.asarray(gains_same_probes).mean(1), color=ORANGE, linestyle="--", linewidth=1.6,
                label="over the single best with the same probes")
    ax.axhline(seen_gain, color=MUTED, linewidth=1, label="seen-model gain (tuned k)")
    ax.set(xscale="log", xlabel="number of probes n", ylabel="gain over single best", title=title)
    ax.yaxis.set_major_locator(MaxNLocator(steps=[1, 2, 5, 10]))  # ticks at whole percents: 2%, 4%, ... or 5%, 10%
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, loc="lower right")
    return fig


# ---------------------------------------------------------------- PCA views of the embedding space

def pca_project(E, fit_idx=None):
    """Project all embeddings on the first two principal axes fitted on E[fit_idx] (default: all of E).
    Returns Z of shape (n, 2) and the share of variance explained by each axis."""
    pca = PCA(n_components=2).fit(E if fit_idx is None else E[fit_idx])
    return pca.transform(E), pca.explained_variance_ratio_


def _sample(n, cap=20_000):
    # keep a scatter fast and readable on large data: a fixed random subset of at most `cap` points
    return np.arange(n) if n <= cap else np.sort(np.random.default_rng(0).choice(n, cap, replace=False))


def _panels(n, ratio, ncols=3):
    """A grid of n small panels with shared axes and the PCA axis labels. Returns the figure and the n axes."""
    rows, ncols = -(-n // ncols), min(n, ncols)
    fig, axes = plt.subplots(rows, ncols, figsize=(3.3 * ncols, 2.9 * rows), sharex=True, sharey=True,
                             squeeze=False, layout="constrained")
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    for ax in axes.flat[:n]:
        ax.grid(False)
    fig.supxlabel(f"PC1 ({ratio[0]:.0%} of variance)", fontsize=9)
    fig.supylabel(f"PC2 ({ratio[1]:.0%} of variance)", fontsize=9)
    return fig, list(axes.flat[:n])


def _pc_labels(ax, ratio):
    ax.set(xlabel=f"PC1 ({ratio[0]:.0%} of variance)", ylabel=f"PC2 ({ratio[1]:.0%} of variance)")
    ax.grid(False)


def plot_pca_groups(Z, ratio, labels, title, names=None, groups=None, max_groups=8):
    """Small multiples, one panel per group (a task type, the model the router picks, ...): the group in blue over
    all points in gray. Colors do not carry identity, the panel title does.
    `groups` lists the groups to show, in this order, empty ones included (e.g. all models in their original order,
    also the ones never chosen). By default the groups present, in label order; with more than `max_groups` of
    them, the largest ones."""
    labels = np.asarray(labels)
    present, counts = np.unique(labels, return_counts=True)
    truncated = groups is None and len(present) > max_groups
    if groups is None:
        groups = np.sort(present[np.argsort(-counts, kind="stable")[:max_groups]])
    keep = _sample(len(Z))
    fig, axes = _panels(len(groups), ratio)
    for ax, g in zip(axes, groups):
        mask = labels == g
        ax.scatter(*Z[keep].T, s=4, color=FAINT, linewidths=0, rasterized=True)
        ax.scatter(*Z[keep][mask[keep]].T, s=5, color=BLUE, linewidths=0, rasterized=True)
        ax.set_title(f"{(names or {}).get(g, g)} (n = {mask.sum()})", fontsize=9)
        if not mask.any():
            ax.text(0.5, 0.5, "none", transform=ax.transAxes, ha="center", va="center", color=MUTED)
    shown = f" (largest {max_groups} of {len(present)}, in label order)" if truncated else ""
    fig.suptitle(title + shown, fontsize=11)
    return fig


def plot_pca_quality(Z, ratio, S, model_names, title="Mean observed score of each model over the PCA plane"):
    """One panel per model (column of S): the observed score averaged in hexagonal bins, on a shared 0-1 scale."""
    fig, axes = _panels(len(model_names), ratio)
    for ax, s, name in zip(axes, S.T, model_names):
        hb = ax.hexbin(*Z.T, C=s, reduce_C_function=np.mean, gridsize=16, mincnt=3, cmap=SEQ, vmin=0, vmax=1,
                       linewidths=0)
        ax.set_title(name, fontsize=9)
    fig.colorbar(hb, ax=axes, shrink=0.8, label="mean observed score")
    fig.suptitle(title, fontsize=11)
    return fig


def plot_explained_variance(embeddings, fit_idx=None, max_components=20):
    """Cumulative share of variance of the principal components, one line per embedding (at most three)."""
    assert len(embeddings) <= 3
    fig, ax = plt.subplots()
    for (name, E), color in zip(embeddings.items(), (BLUE, ORANGE, SERIES["oracle"])):
        X = E if fit_idx is None else E[fit_idx]
        pca = PCA(n_components=min(max_components, *X.shape)).fit(X)
        ax.plot(np.arange(1, pca.n_components_ + 1), np.cumsum(pca.explained_variance_ratio_), color=color, label=name)
    ax.set(xlabel="number of principal components", ylabel="cumulative share of variance", ylim=(0, 1.02),
           title="How much of the embedding the leading components hold")
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, loc="lower right")
    return fig


def _scatter_legend(ax):
    # fixed marker sizes in the legend, whatever the size of the points on the plot (the star needs more)
    legend = ax.legend(frameon=False, loc="best", fontsize=8)
    for handle, text in zip(legend.legend_handles, legend.get_texts()):
        handle.set_sizes([120 if text.get_text() == "query" else 36])


def plot_probes(Z, ratio, train, probes, routed=None, title="Where the probes of the new model sit"):
    """The probe queries of the new model over the training queries. `train`, `probes` and `routed` are row indices
    of Z; `routed` optionally marks the test queries the router sends to the new model."""
    fig, ax = plt.subplots(figsize=(6.5, 5))
    keep = train[_sample(len(train))]
    ax.scatter(*Z[keep].T, s=4, color=FAINT, linewidths=0, label="training queries", rasterized=True)
    if routed is not None and len(routed):
        ax.scatter(*Z[routed].T, s=6, color=BLUE, linewidths=0, label="test queries routed to the new model")
    ax.scatter(*Z[probes].T, s=45, marker="D", color=ORANGE, edgecolor=INK, linewidth=0.6, zorder=3,
               label=f"probes (n = {len(probes)})")
    _pc_labels(ax, ratio)
    ax.set_title(title)
    _scatter_legend(ax)
    return fig


def plot_neighbors(Z, ratio, train, query, neighbors, probes=None, probe_neighbors=None,
                   title="One query and the neighbors that estimate its quality"):
    """A query (star) and the labeled queries its estimate is averaged over. `train`, `query`, `neighbors`, `probes`
    and `probe_neighbors` are row indices of Z. `neighbors` are the k nearest training queries, shared by the pool
    models. In the unseen-model setting `probes` are the new model's probes and `probe_neighbors` the ones its
    estimate is averaged over."""
    fig, ax = plt.subplots(figsize=(6.5, 5))
    keep = train[_sample(len(train))]
    ax.scatter(*Z[keep].T, s=4, color=FAINT, linewidths=0, label="training queries", rasterized=True)
    if probes is not None:
        ax.scatter(*Z[probes].T, s=16, marker="D", color=ORANGE, alpha=0.45, linewidths=0,
                   label=f"probes of the new model (n = {len(probes)})")
    ax.scatter(*Z[neighbors].T, s=32, color=BLUE, edgecolor=INK, linewidth=0.5, zorder=3,
               label=f"neighbors for the pool models (k = {len(neighbors)})")
    if probe_neighbors is not None:
        ax.scatter(*Z[probe_neighbors].T, s=70, marker="D", color=ORANGE, edgecolor=INK, linewidth=0.8, zorder=4,
                   label=f"neighbors for the new model (k = {len(probe_neighbors)})")
    ax.scatter(*Z[[query]].T, s=260, marker="*", color=INK, edgecolor=SURFACE, linewidth=0.8, zorder=5, label="query")
    _pc_labels(ax, ratio)
    ax.set_title(title)
    _scatter_legend(ax)
    fig.text(0.01, 0.005, "Neighbors are found in the full embedding space; some can look far apart in this 2D projection.",
             fontsize=7, color=MUTED)
    return fig
