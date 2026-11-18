"""Efficient evaluation with the same routing, area and bootstrap definitions as router.py.

Each model becomes competitive against all more expensive models at most once as lambda
increases. Store these transitions, rather than materializing lambda-by-query arrays for
every policy. Tests compare curves, bootstrap intervals and selected k to the reference.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import csr_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "michal-harness"))
from router import area, curve, realized, route  # noqa: E402


def lambda_grid(cost, num=500, low=-3, high=3):
    if np.ptp(cost) <= 0:
        raise ValueError("A cost-quality area requires a nonzero cost range")
    return np.r_[0.0, np.logspace(low, high, num)] / np.ptp(cost)


@lru_cache(maxsize=6)
def bootstrap_weights(n, n_boot, seed):
    # Same RNG draws and query weights as router.bootstrap_areas.
    rng = np.random.default_rng(seed)
    rows = [np.bincount(rng.integers(n, size=n), minlength=n) / n for _ in range(n_boot)]
    return np.asarray(rows).T.copy()


def sample_areas(costs, qualities, c_range):
    """One row per bootstrap sample; identical interpolation/integration to router.area."""
    budget = np.geomspace(*c_range, 200)
    log_budget = np.log(budget)
    result = np.empty(len(qualities))
    for b, quality in enumerate(qualities):
        cost = costs if costs.ndim == 1 else costs[b]
        order = np.argsort(cost)
        y = np.interp(budget, cost[order], np.maximum.accumulate(quality[order]))
        result[b] = np.trapezoid(y, log_budget)
    return result


@dataclass
class Events:
    starts: np.ndarray
    ends: np.ndarray
    queries: np.ndarray
    costs: np.ndarray
    qualities: np.ndarray
    n_queries: int
    n_lambdas: int

    def curve(self):
        points = []
        for values in (self.costs, self.qualities):
            delta = (np.bincount(self.starts, values, minlength=self.n_lambdas + 1)
                     - np.bincount(self.ends, values, minlength=self.n_lambdas + 1))
            points.append(np.cumsum(delta[:-1]) / self.n_queries)
        return np.column_stack(points)

    def bootstrap_areas(self, weights, c_range):
        rows = np.r_[self.starts, self.ends]
        cols = np.r_[self.queries, self.queries]
        keep = rows < self.n_lambdas
        outputs = []
        for values in (self.costs, self.qualities):
            delta = np.r_[values, -values]
            matrix = csr_matrix((delta[keep], (rows[keep], cols[keep])),
                                shape=(self.n_lambdas, self.n_queries))
            weighted = (matrix @ weights).T.copy()
            outputs.append(np.cumsum(weighted, axis=1))
        return sample_areas(*outputs, c_range)


class Policy:
    """Cost-weighted argmax with the reference's 1e-9 cheaper-model tie rule."""
    def __init__(self, scores, truth, cost):
        order = np.argsort(cost, kind="stable")
        self.scores = np.asarray(scores, dtype=np.float64)[:, order]
        self.truth = np.asarray(truth, dtype=np.float64)[:, order]
        self.cost = np.asarray(cost, dtype=np.float64)[order]
        self.bounds = np.zeros(self.scores.shape)
        self.duplicate_cost = len(np.unique(self.cost)) != len(self.cost)
        if not self.duplicate_cost:
            for m in range(len(cost) - 1):
                crossing = ((self.scores[:, m+1:] - self.scores[:, [m]] - 1e-9)
                            / (self.cost[m+1:] - self.cost[m]))
                self.bounds[:, m] = crossing.max(axis=1)

    def _eligible(self, m, indices, lambdas):
        lam = lambdas[np.clip(indices, 0, len(lambdas) - 1)]
        objective = self.scores[:, m:] - lam[:, None] * self.cost[m:]
        return objective[:, 0] >= objective.max(axis=1) - 1e-9

    def events(self, lambdas):
        n, M = self.scores.shape
        L = len(lambdas)
        if self.duplicate_cost:
            # Equal-cost numerical ties can be non-monotone after floating-point cancellation.
            # Keep the exact reference path for this unusual case (neither benchmark has it).
            picks = np.array([route(self.scores, self.cost, lam) for lam in lambdas])
            changes = np.r_[np.ones((1, n), dtype=bool), picks[1:] != picks[:-1]]
            starts, queries = np.nonzero(changes)
            ends = np.full(len(starts), L, dtype=int)
            for q in range(n):
                positions = np.flatnonzero(queries == q)
                ends[positions[:-1]] = starts[positions[1:]]
            models = picks[starts, queries]
            return Events(starts, ends, queries, self.cost[models],
                          self.truth[queries, models], n, L)
        starts = np.searchsorted(lambdas, self.bounds, side="left")
        # Check the adjacent grid points using the exact floating-point objective from route.
        # This preserves boundary/tolerance behavior instead of trusting a divided threshold.
        for m in range(M):
            s = starts[:, m]
            previous = (s > 0) & self._eligible(m, s - 1, lambdas)
            s[previous] -= 1
            failed = (s < L) & ~self._eligible(m, s, lambdas)
            s[failed] += 1
            bad = ((s > 0) & self._eligible(m, s - 1, lambdas)) | ((s < L) & ~self._eligible(m, s, lambdas))
            if bad.any():
                # Rare near-coincident prices: binary search the monotone suffix condition.
                lo, hi = np.zeros(n, dtype=int), np.full(n, L, dtype=int)
                while np.any(lo[bad] < hi[bad]):
                    mid = (lo + hi) // 2
                    eligible = self._eligible(m, mid, lambdas)
                    active = bad & (lo < hi)
                    hi[active & eligible] = mid[active & eligible]
                    lo[active & ~eligible] = mid[active & ~eligible] + 1
                s[bad] = lo[bad]
        ends = np.column_stack([np.full(n, L), np.minimum.accumulate(starts, axis=1)[:, :-1]])
        queries, models = np.nonzero(starts < ends)
        return Events(starts[queries, models], ends[queries, models], queries,
                      self.cost[models], self.truth[queries, models], n, L)


class MetricContext:
    """Reference policies and paired-bootstrap baselines reused within one model pool."""
    def __init__(self, truth, cost, train_mean):
        self.truth = np.asarray(truth, dtype=np.float64)
        self.cost = np.asarray(cost, dtype=np.float64)
        self.train_mean = np.asarray(train_mean, dtype=np.float64)
        self.c_range = (self.cost.min(), self.cost.max())
        self.oracle = Policy(self.truth, self.truth, self.cost)
        self.references = {}
        self.base_boot = {}

    def constant_curve(self, scores, lambdas):
        order = np.argsort(self.cost, kind="stable")
        obj = scores[None, :] - lambdas[:, None] * self.cost[None, :]
        near = obj[:, order] >= obj.max(axis=1, keepdims=True) - 1e-9
        picks = order[near.argmax(axis=1)]
        return np.column_stack([self.cost[picks], self.truth.mean(axis=0)[picks]]), picks

    def reference(self, lambdas):
        key = lambdas.tobytes()
        if key not in self.references:
            single, picks = self.constant_curve(self.train_mean, lambdas)
            oracle = self.oracle.events(lambdas).curve()
            self.references[key] = {"single": single, "picks": picks, "oracle": oracle,
                "area_single": area(single, *self.c_range), "area_oracle": area(oracle, *self.c_range)}
        return self.references[key]

    def evaluate(self, policy, lambdas, n_boot=0, seed=0, probe_mean=None):
        events = policy.events(lambdas)
        points = events.curve()
        ref = self.reference(lambdas)
        a = area(points, *self.c_range)
        gain = a / ref["area_single"] - 1
        ci = (None, None)
        if n_boot:
            weights = bootstrap_weights(len(self.truth), n_boot, seed)
            key = (lambdas.tobytes(), n_boot, seed)
            if key not in self.base_boot:
                means = (self.truth.T @ weights).T
                qualities = means[:, ref["picks"]]
                self.base_boot[key] = sample_areas(ref["single"][:, 0], qualities, self.c_range)
            boot = events.bootstrap_areas(weights, self.c_range)
            ci = tuple(np.quantile(boot / self.base_boot[key] - 1, [0.025, 0.975]))
        same_probes = None
        if probe_mean is not None:
            same_curve, _ = self.constant_curve(probe_mean, lambdas)
            same_probes = a / area(same_curve, *self.c_range) - 1
        return {"A": a / ref["area_oracle"], "A_single_best": ref["area_single"] / ref["area_oracle"],
                "gain": gain, "gain_abs": (a - ref["area_single"]) / np.log(self.c_range[1] / self.c_range[0]),
                "gain_same_probes": same_probes, "gain_ci_low": ci[0], "gain_ci_high": ci[1]}, points


def select_k(estimates, truth, cost, k_grid, n_boot=200, seed=0):
    """Same validation-area one-standard-error rule as the reference select_k."""
    if len(cost) == 1 or np.ptp(cost) == 0:
        return 10
    grid = lambda_grid(cost)
    curves = {k: Policy(estimates[k], truth, cost).events(grid) for k in k_grid}
    areas = {k: area(events.curve(), cost.min(), cost.max()) for k, events in curves.items()}
    best = max(areas, key=areas.get)
    weights = bootstrap_weights(len(truth), n_boot, seed)
    se = curves[best].bootstrap_areas(weights, (cost.min(), cost.max())).std()
    return max(k for k in k_grid if areas[k] >= areas[best] - se)
