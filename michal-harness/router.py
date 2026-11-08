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


def curve(scores, S, cost, lambdas):
    """(mean cost, mean quality) for each λ when routing by `scores`; quality is the observed score S."""
    rows = np.arange(len(S))
    picks = [route(scores, cost, lam) for lam in lambdas]
    return np.array([(cost[p].mean(), S[rows, p].mean()) for p in picks])


def lambda_grid(cost, num=100):
    """λ = 0 plus a log-spaced sweep scaled so that λ·(cost range) spans 1e-3 … 1e3."""
    return np.r_[0, np.logspace(-3, 3, num)] / np.ptp(cost)


def area(points, c_lo, c_hi, grid=200):
    """Area under the best-quality-within-budget curve over the cost range [c_lo, c_hi], on a log-cost axis
    (each price decade weighs the same). Between operating points the curve is linear in cost."""
    points = points[np.argsort(points[:, 0])]
    budget = np.geomspace(c_lo, c_hi, grid)
    quality = np.interp(budget, points[:, 0], np.maximum.accumulate(points[:, 1]))
    return np.trapezoid(quality, np.log(budget))


def evaluate(data, fit, new_model=None, n_probes=None, seed=0, k=10):
    """Evaluate the embedding returned by `fit(train_models) -> embed(list[str]) -> ndarray`.
    new_model=None: seen-model setting. Otherwise `new_model` is held out of `fit` and of the
    kNN labels, and only gets scores on `n_probes` probe queries (unseen-model setting)."""
    assert (new_model is None) == (n_probes is None), "new_model and n_probes go together"
    M = len(data.models)
    new = None if new_model is None else data.models.index(new_model)
    pool = [m for m in range(M) if m != new]

    E = np.asarray(fit([data.models[m] for m in pool])(data.queries))
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
    curves = {name: curve(scores, S_te, data.cost, lambdas) for name, scores in policies.items()}
    areas = {name: area(c, data.cost.min(), data.cost.max()) for name, c in curves.items()}
    return {"gain": areas["router"] / areas["single_best"] - 1,  # main metric: area gain over the single best
            "A": areas["router"] / areas["oracle"],              # secondary: area relative to the oracle
            "A_single_best": areas["single_best"] / areas["oracle"],
            "k": k, "lambdas": lambdas, "curves": curves}
