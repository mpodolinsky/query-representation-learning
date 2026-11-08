"""Router and evaluation harness: kNN quality estimator, λ sweep and area A (paper §2, §7.2)."""
from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import NearestNeighbors


@dataclass
class Data:
    """Stand-in for Arman's table until his schema is fixed."""
    queries: list[str]
    models: list[str]
    S: np.ndarray       # (Q, M) observed scores in [0, 1]
    cost: np.ndarray    # (M,) mean per-query cost at the evaluated epoch
    train: np.ndarray   # query indices. WARNING: one fixed split; re-splitting variance is not measured
    val: np.ndarray     # used ONLY to tune k. Embedding training (early stopping included) must never see it
    test: np.ndarray


def knn_estimate(E_labeled, S_labeled, E_query, k):
    """q̂ of shape (n_query, n_models), Eq. 2: mean score over the k nearest labeled queries (Euclidean).
    The columns of S_labeled are models labeled on the same queries, so they share neighbors."""
    k = min(k, len(E_labeled))
    idx = NearestNeighbors(n_neighbors=k).fit(E_labeled).kneighbors(E_query, return_distance=False)
    return sum(S_labeled[idx[:, j]] for j in range(k)) / k


def route(scores, cost, lam):
    """Eq. 1: per query, the model maximizing score − λ·cost."""
    return (scores - lam * cost).argmax(1)


def realized(scores, S, cost, lambdas):
    """Per-query cost and observed quality of the routed model for each λ: two (n_lambda, n_query) arrays."""
    picks = np.array([route(scores, cost, lam) for lam in lambdas])
    return cost[picks], S[np.arange(len(S)), picks]


def lambda_grid(cost, num=100):
    """λ = 0 plus a log-spaced sweep scaled so that λ·(cost range) spans 1e-3 … 1e3."""
    return np.r_[0, np.logspace(-3, 3, num)] / np.ptp(cost)


def curve(run, w=None):
    """(mean cost, mean quality) per λ of a `realized` run; w optionally weights the queries."""
    cost, quality = run
    return np.column_stack([cost.mean(1), quality.mean(1)] if w is None else [cost @ w, quality @ w])


def area(points, c_lo, c_hi, grid=200):
    """Area under the best-quality-within-budget curve over the cost range [c_lo, c_hi], on a log-cost axis
    (each price decade weighs the same). Between operating points the curve is linear in cost."""
    points = points[np.argsort(points[:, 0])]
    budget = np.geomspace(c_lo, c_hi, grid)
    quality = np.interp(budget, points[:, 0], np.maximum.accumulate(points[:, 1]))
    return np.trapezoid(quality, np.log(budget))


def bootstrap_areas(runs, c_range, n_boot, seed=0):
    """Area of each policy on n_boot resamples of the queries (drawn with replacement).
    `runs` maps a name to a `realized` output; every resample is shared by all policies (paired)."""
    n = next(iter(runs.values()))[0].shape[1]
    rng = np.random.default_rng(seed)
    areas = {name: np.empty(n_boot) for name in runs}
    for b in range(n_boot):
        w = np.bincount(rng.integers(n, size=n), minlength=n) / n  # weight of each query in the resample
        for name, run in runs.items():
            areas[name][b] = area(curve(run, w), *c_range)
    return areas


def bootstrap_gain_ci(router, single, c_range, n_boot=1000, level=0.95, seed=0):
    """Percentile bootstrap interval of the area gain of `router` over `single` (both `realized` outputs)."""
    areas = bootstrap_areas({"router": router, "single": single}, c_range, n_boot, seed)
    return tuple(np.quantile(areas["router"] / areas["single"] - 1, [(1 - level) / 2, (1 + level) / 2]))


def select_k(E, data, pool, k_grid=(5, 10, 20, 50, 100, 200), n_boot=200, seed=0):
    """One-standard-error rule on the validation split: the largest k (smoothest estimate) whose router
    area is within one bootstrap standard error of the best k. Only the `pool` models are used."""
    tr, va, cost = data.train, data.val, data.cost[pool]
    c_range = (cost.min(), cost.max())
    runs = {k: realized(knn_estimate(E[tr], data.S[tr][:, pool], E[va], k), data.S[va][:, pool], cost,
                        lambda_grid(cost)) for k in k_grid}
    areas = {k: area(curve(run), *c_range) for k, run in runs.items()}
    best = max(areas, key=areas.get)
    if len(k_grid) > 1 and best in (min(k_grid), max(k_grid)):
        print(f"WARNING select_k: best k={best} is at the {'upper' if best == max(k_grid) else 'lower'} edge of "
              f"the grid {tuple(k_grid)}; the grid may be too narrow.")
    se = bootstrap_areas({"best": runs[best]}, c_range, n_boot, seed)["best"].std()
    return max(k for k in k_grid if areas[k] >= areas[best] - se)


def evaluate(data, fit, new_model=None, n_probes=None, seed=0, k=10, tune_k=False, k_grid=(5, 10, 20, 50, 100, 200),
             n_boot=1000):
    """Evaluate the embedding returned by `fit(train_models) -> embed(list[str]) -> ndarray`.
    new_model=None: seen-model setting. Otherwise `new_model` is held out of `fit` and of the
    kNN labels, and only gets scores on `n_probes` probe queries (unseen-model setting).
    tune_k=True ignores `k` and picks it from `k_grid` for this embedding (see `select_k`); the new model's
    labels are never used for that. `gain_ci` is a bootstrap interval over the test queries (None if n_boot=0)."""
    assert (new_model is None) == (n_probes is None), "new_model and n_probes go together"
    M = len(data.models)
    new = None if new_model is None else data.models.index(new_model)
    pool = [m for m in range(M) if m != new]

    E = np.asarray(fit([data.models[m] for m in pool])(data.queries))
    if tune_k:
        k = select_k(E, data, pool, k_grid)  # independent of the probe seed: tuning never touches the probes
    tr, te = data.train, data.test
    S_tr, S_te = data.S[tr], data.S[te]

    Q_hat, q_mean = np.empty((len(te), M)), np.empty(M)  # kNN estimates, mean train quality
    Q_hat[:, pool] = knn_estimate(E[tr], S_tr[:, pool], E[te], k)
    q_mean[pool] = S_tr[:, pool].mean(0)
    if new is not None:
        probes = np.random.default_rng(seed).choice(len(tr), n_probes, replace=False)  # TODO: Arman's sampler
        Q_hat[:, [new]] = knn_estimate(E[tr[probes]], S_tr[probes][:, [new]], E[te], k)
        q_mean[new] = S_tr[probes, new].mean()

    lambdas = lambda_grid(data.cost)
    policies = {"router": Q_hat, "single_best": np.broadcast_to(q_mean, Q_hat.shape), "oracle": S_te}
    runs = {name: realized(scores, S_te, data.cost, lambdas) for name, scores in policies.items()}
    curves = {name: curve(run) for name, run in runs.items()}
    c_range = (data.cost.min(), data.cost.max())
    areas = {name: area(c, *c_range) for name, c in curves.items()}
    ci = bootstrap_gain_ci(runs["router"], runs["single_best"], c_range, n_boot, seed=seed) if n_boot else None
    return {"gain": areas["router"] / areas["single_best"] - 1,  # main metric: area gain over the single best
            "gain_ci": ci,                                       # 95% bootstrap interval over test queries
            "A": areas["router"] / areas["oracle"],              # secondary: area relative to the oracle
            "A_single_best": areas["single_best"] / areas["oracle"],
            "k": k, "lambdas": lambdas, "curves": curves}
