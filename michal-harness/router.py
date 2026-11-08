"""Router and evaluation harness: kNN quality estimator, λ sweep, area A and result saving (paper §2, §7.2)."""
import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

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
    theme: np.ndarray | None = None  # task type of each query (e.g. math, code), used for plots and RQ1a


def knn_indices(E_labeled, E_query, k):
    """(n_query, min(k, n_labeled)) indices of the nearest labeled embeddings (Euclidean), nearest first."""
    k = min(k, len(E_labeled))
    return NearestNeighbors(n_neighbors=k).fit(E_labeled).kneighbors(E_query, return_distance=False)


def knn_estimate(E_labeled, S_labeled, E_query, k):
    """q̂ of shape (n_query, n_models), Eq. 2: mean score over the k nearest labeled queries (Euclidean).
    The columns of S_labeled are models labeled on the same queries, so they share neighbors."""
    idx = knn_indices(E_labeled, E_query, k)
    return sum(S_labeled[idx[:, j]] for j in range(idx.shape[1])) / idx.shape[1]


def route(scores, cost, lam):
    """Eq. 1: per query, the model maximizing score − λ·cost. Ties (within 1e-9) go to the cheaper model, so the
    result does not depend on the order of the models."""
    objective = scores - lam * cost
    cheapest_first = np.argsort(cost, kind="stable")
    near_best = objective[:, cheapest_first] >= objective.max(1, keepdims=True) - 1e-9
    return cheapest_first[near_best.argmax(1)]


def realized(scores, S, cost, lambdas):
    """Per-query cost and observed quality of the routed model for each λ: two (n_lambda, n_query) arrays."""
    picks = np.array([route(scores, cost, lam) for lam in lambdas])
    return cost[picks], S[np.arange(len(S)), picks]


def lambda_grid(cost, num=500):
    """λ = 0 plus `num` log-spaced values, scaled so that λ·(cost range) spans 1e-3 … 1e3."""
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


def select_k(E, data, pool, k_grid=(5, 10, 20, 50, 100, 200), n_boot=200, seed=0, n_lambdas=500):
    """One-standard-error rule on the validation split: the largest k (smoothest estimate) whose router
    area is within one bootstrap standard error of the best k. Only the `pool` models are used."""
    tr, va, cost = data.train, data.val, data.cost[pool]
    c_range = (cost.min(), cost.max())
    runs = {k: realized(knn_estimate(E[tr], data.S[tr][:, pool], E[va], k), data.S[va][:, pool], cost,
                        lambda_grid(cost, n_lambdas)) for k in k_grid}
    areas = {k: area(curve(run), *c_range) for k, run in runs.items()}
    best = max(areas, key=areas.get)
    if len(k_grid) > 1 and best in (min(k_grid), max(k_grid)):
        print(f"WARNING select_k: best k={best} is at the {'upper' if best == max(k_grid) else 'lower'} edge of "
              f"the grid {tuple(k_grid)}; the grid may be too narrow.")
    se = bootstrap_areas({"best": runs[best]}, c_range, n_boot, seed)["best"].std()
    return max(k for k in k_grid if areas[k] >= areas[best] - se)


def evaluate(data, fit, new_model=None, n_probes=None, seed=0, k=10, tune_k=False, k_grid=(5, 10, 20, 50, 100, 200),
             n_boot=1000, n_lambdas=500):
    """Evaluate the embedding returned by `fit(train_models) -> embed(list[str]) -> ndarray`.
    new_model=None: seen-model setting. Otherwise `new_model` is held out of `fit` and of the
    kNN labels, and only gets scores on `n_probes` probe queries (unseen-model setting).
    `gain` is over the single best that knows every model's quality from all training queries, in both settings,
    so the baseline does not change with `n_probes`. In the unseen setting `gain_same_probes` is over the single
    best that knows the new model only from the same probes.
    tune_k=True ignores `k` and picks it from `k_grid` for this embedding (see `select_k`); the new model's
    labels are never used for that. `gain_ci` is a bootstrap interval over the test queries (None if n_boot=0)."""
    assert (new_model is None) == (n_probes is None), "new_model and n_probes go together"
    M = len(data.models)
    new = None if new_model is None else data.models.index(new_model)
    pool = [m for m in range(M) if m != new]

    E = np.asarray(fit([data.models[m] for m in pool])(data.queries))
    if tune_k:
        k = select_k(E, data, pool, k_grid, n_lambdas=n_lambdas)  # independent of the probe seed: tuning never touches the probes
    tr, te = data.train, data.test
    S_tr, S_te = data.S[tr], data.S[te]

    Q_hat, probe_ids, q_mean_probes = np.empty((len(te), M)), None, None  # kNN estimates
    Q_hat[:, pool] = knn_estimate(E[tr], S_tr[:, pool], E[te], k)
    q_mean = S_tr.mean(0)  # mean train quality of every model, the new one included: the full-information single best
    if new is not None:
        probes = np.random.default_rng(seed).choice(len(tr), n_probes, replace=False)  # TODO: Arman's sampler
        probe_ids = tr[probes]
        Q_hat[:, [new]] = knn_estimate(E[probe_ids], S_tr[probes][:, [new]], E[te], k)
        q_mean_probes = q_mean.copy()
        q_mean_probes[new] = S_tr[probes, new].mean()  # what the single best knows from the same probes

    lambdas = lambda_grid(data.cost, n_lambdas)
    policies = {"router": Q_hat, "single_best": np.broadcast_to(q_mean, Q_hat.shape), "oracle": S_te}
    if q_mean_probes is not None:
        policies["single_best_probes"] = np.broadcast_to(q_mean_probes, Q_hat.shape)
    runs = {name: realized(scores, S_te, data.cost, lambdas) for name, scores in policies.items()}
    curves = {name: curve(run) for name, run in runs.items()}
    c_range = (data.cost.min(), data.cost.max())
    areas = {name: area(c, *c_range) for name, c in curves.items()}
    ci = bootstrap_gain_ci(runs["router"], runs["single_best"], c_range, n_boot, seed=seed) if n_boot else None
    gain_same_probes = areas["router"] / areas["single_best_probes"] - 1 if q_mean_probes is not None else None
    return {"gain": areas["router"] / areas["single_best"] - 1,  # main metric: area gain over the full-information single best
            "gain_same_probes": gain_same_probes,                # unseen only: over the single best given the same probes
            "gain_abs": (areas["router"] - areas["single_best"]) / np.log(c_range[1] / c_range[0]),  # in mean score
            "gain_ci": ci,                                       # 95% bootstrap interval over test queries
            "A": areas["router"] / areas["oracle"],              # secondary: area relative to the oracle
            "A_single_best": areas["single_best"] / areas["oracle"],
            "k": k, "n_lambdas": n_lambdas, "lambdas": lambdas, "curves": curves, "Q_hat": Q_hat, "q_mean": q_mean,
            "q_mean_probes": q_mean_probes,
            "probes": probe_ids,  # query indices of the probes (None in the seen setting)
            "cost_range": c_range}  # the range `A` is integrated over


def recovery(unseen, seen):
    """Fraction of the seen-model gain that an unseen run recovers with its probes. Both gains are over the same
    full-information single best, so this is (area_unseen − area_base) / (area_seen − area_base).
    NaN if the seen-model gain is not positive."""
    return unseen["gain"] / seen["gain"] if seen["gain"] > 0 else float("nan")


class Results:
    """Saves the runs of one experiment in a new folder `root/YYYY-MM-DD_HH-MM-SS/` (gitignored):
    results.csv (one row per run), runs/NNNN.npz (curves, λ grid, test q̂, mean qualities and probe queries of the run),
    split.npz (train/val/test indices) and meta.json. Everything needed to redo the routing, the area and the
    gain later, without refitting an embedding or rerunning the kNN, is in there."""

    def __init__(self, data, benchmark, root="results"):
        self.data, self.benchmark, self.rows, self.seen = data, benchmark, [], {}  # seen: embedding name -> seen run
        self.dir = Path(root) / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        (self.dir / "runs").mkdir(parents=True)
        np.savez_compressed(self.dir / "split.npz", train=data.train, val=data.val, test=data.test)
        git = lambda *args: subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()
        (self.dir / "meta.json").write_text(json.dumps({
            "created": datetime.now().isoformat(timespec="seconds"), "benchmark": benchmark,
            "git_commit": git("rev-parse", "--short", "HEAD") + ("-dirty" if git("status", "--porcelain") else ""),
            "models": data.models, "cost": data.cost.tolist()}, indent=2))

    def run(self, embedding, fit, new_model=None, n_probes=None, seed=0, **eval_kwargs):
        """Evaluate `fit` with `evaluate`, save the run, and return the `evaluate` result.
        `embedding` is the name written in the results table. Run the seen-model setting first: an unseen run of
        the same embedding name then gets its `recovery` against it. q̂ is stored in float64 on purpose: float32
        rounding (about 1e-7) is larger than the 1e-9 tolerance that decides routing ties."""
        res = evaluate(self.data, fit, new_model, n_probes, seed, **eval_kwargs)
        run_id = f"{len(self.rows):04d}"
        unseen = {} if res["probes"] is None else {"probes": res["probes"], "q_mean_probes": res["q_mean_probes"]}
        np.savez_compressed(self.dir / "runs" / f"{run_id}.npz", lambdas=res["lambdas"], q_mean=res["q_mean"],
                            Q_hat=res["Q_hat"], **unseen, **{f"curve_{name}": c for name, c in res["curves"].items()})
        if new_model is None:
            self.seen[embedding] = res
        lo, hi = res["gain_ci"] or ("", "")
        self.rows.append({"run": run_id, "benchmark": self.benchmark, "embedding": embedding,
                          "new_model": new_model or "", "n_probes": n_probes or "", "seed": seed,
                          "tune_k": eval_kwargs.get("tune_k", False), "k": res["k"], "n_lambdas": res["n_lambdas"],
                          "gain": res["gain"], "gain_abs": res["gain_abs"],
                          "gain_same_probes": "" if res["gain_same_probes"] is None else res["gain_same_probes"],
                          "recovery": recovery(res, self.seen[embedding]) if new_model and embedding in self.seen else "",
                          "gain_ci_low": lo, "gain_ci_high": hi, "A": res["A"], "A_single_best": res["A_single_best"]})
        with open(self.dir / "results.csv", "w", newline="") as f:  # rewritten each run: partial results survive a crash
            writer = csv.DictWriter(f, fieldnames=self.rows[0])
            writer.writeheader()
            writer.writerows(self.rows)
        return res
