import dataclasses

import numpy as np
import pytest

from router import Data, area, bootstrap_gain_ci, evaluate, knn_estimate, route, select_k


def make_data(Q=4000, M=5, C=6, dim=8, seed=0):
    """Queries fall in C clusters. Model m answers a query of cluster c correctly with
    probability quality[m, c] (the true q), so the observed score is a noisy Bernoulli draw of it."""
    rng = np.random.default_rng(seed)
    cluster = rng.integers(C, size=Q)
    E = rng.normal(0, 3, (C, dim))[cluster] + rng.normal(0, 1, (Q, dim))
    cost = np.geomspace(1, 20, M)  # model 0 is cheapest and, on average, weakest
    quality = np.clip(np.linspace(0.3, 0.7, M)[:, None] + rng.uniform(-0.25, 0.25, (M, C)), 0, 1)
    S = (rng.random((Q, M)) < quality[:, cluster].T).astype(float)
    order = rng.permutation(Q)
    a, b = int(0.6 * Q), int(0.7 * Q)  # 60% train, 10% validation, 30% test
    data = Data([str(i) for i in range(Q)], [f"model{m}" for m in range(M)], S, cost,
                train=order[:a], val=order[a:b], test=order[b:])
    fit = lambda _pool: lambda queries: E[[int(q) for q in queries]]  # frozen: ignores the pool
    return data, fit


@pytest.fixture(scope="module")
def synth():
    return make_data()


def test_knn_estimate_models_share_neighbors_but_not_scores():
    E = np.array([[0.], [1.], [10.]])
    S = np.array([[0., 1.], [1., 1.], [1., 0.]])
    est = knn_estimate(E, S, np.array([[0.4]]), k=2)  # neighbors are queries 0 and 1
    assert np.allclose(est, [[0.5, 1.0]])


def test_knn_estimate_k1_returns_own_scores():
    rng = np.random.default_rng(0)
    E, S = rng.normal(size=(50, 4)), rng.random((50, 3))
    assert np.allclose(knn_estimate(E, S, E, k=1), S)


def test_knn_estimate_caps_k_at_number_of_labels():
    E, S = np.array([[0.], [1.]]), np.array([[0.], [1.]])
    assert np.allclose(knn_estimate(E, S, np.array([[0.]]), k=10), [[0.5]])


def test_route_extremes():
    scores, cost = np.array([[0.2, 0.5, 0.9]]), np.array([1., 2., 10.])
    assert route(scores, cost, 0.0)[0] == 2    # no cost weight: best quality
    assert route(scores, cost, 100.0)[0] == 0  # cost dominates: cheapest


def test_area_of_linear_curve():
    # q(b) = .2 + .6(b - 1)/3 on [1, 4]; the integral of q d(ln b) is .2 * (4 - 1) = .6
    assert area(np.array([[1., .2], [4., .8]]), 1, 4) == pytest.approx(0.6, abs=1e-3)


def test_area_ignores_dominated_points():
    # the costlier but worse point (4, .7) must not pull the curve down: envelope is .5, .9, .9
    assert area(np.array([[1., .5], [2., .9], [4., .7]]), 1, 4) == pytest.approx(np.log(2) + 0.4, abs=1e-3)


def test_area_weighs_price_decades_equally():
    # quality 1 only above cost 10 on [1, 100]: half of the decades, not 90% of the linear range
    pts = np.array([[1., 0.], [10., 0.], [10.001, 1.], [100., 1.]])
    assert area(pts, 1, 100) / area(np.array([[1., 1.]]), 1, 100) == pytest.approx(0.5, abs=1e-2)


def test_evaluate_seen_beats_single_best(synth):
    res = evaluate(*synth)
    assert 0 < res["A_single_best"] < res["A"] <= 1
    assert res["gain"] == pytest.approx(res["A"] / res["A_single_best"] - 1)
    assert res["gain"] > 0


def test_oracle_maximizes_the_lambda_objective(synth):
    res = evaluate(*synth)
    objective = {name: c[:, 1] - res["lambdas"] * c[:, 0] for name, c in res["curves"].items()}
    assert (objective["oracle"] >= objective["router"] - 1e-12).all()
    assert (objective["oracle"] >= objective["single_best"] - 1e-12).all()


def test_fit_receives_pool_without_new_model(synth):
    data, fit = synth
    calls = []
    evaluate(data, lambda pool: calls.append(pool) or fit(pool), new_model="model2", n_probes=20, n_boot=0)
    assert calls == [[m for m in data.models if m != "model2"]]


def test_unseen_with_all_train_queries_as_probes_equals_seen(synth):
    data, fit = synth
    unseen = evaluate(data, fit, new_model="model2", n_probes=len(data.train), n_boot=0)
    assert unseen["A"] == pytest.approx(evaluate(data, fit, n_boot=0)["A"])


def test_more_probes_help(synth):
    data, fit = synth
    A = lambda n: np.mean([evaluate(data, fit, new_model="model2", n_probes=n, seed=s, n_boot=0)["A"] for s in range(5)])
    assert A(5) < A(500)


def _realized(quality):
    """Fake `realized` output: 3 λ values routing every query to models of cost 1, 2, 4 with the given qualities."""
    return np.tile([[1.], [2.], [4.]], (1, len(quality))), np.tile(quality, (3, 1))


def test_bootstrap_of_identical_policies_is_zero():
    rng = np.random.default_rng(0)
    r = _realized(rng.random(300))
    assert bootstrap_gain_ci(r, r, (1, 4), n_boot=50) == (0.0, 0.0)


def test_bootstrap_interval_excludes_zero_for_a_dominating_router():
    rng = np.random.default_rng(0)
    q = rng.random(300) * 0.5
    lo, hi = bootstrap_gain_ci(_realized(q + 0.3), _realized(q), (1, 4), n_boot=200)
    assert 0 < lo <= hi


def test_bootstrap_is_reproducible_and_seed_dependent():
    rng = np.random.default_rng(0)
    r, s = _realized(rng.random(300) * 0.6 + 0.1), _realized(rng.random(300) * 0.6)
    a = bootstrap_gain_ci(r, s, (1, 4), n_boot=100, seed=1)
    assert a == bootstrap_gain_ci(r, s, (1, 4), n_boot=100, seed=1)
    assert a != bootstrap_gain_ci(r, s, (1, 4), n_boot=100, seed=2)


def test_evaluate_interval_brackets_the_gain(synth):
    res = evaluate(*synth)
    lo, hi = res["gain_ci"]
    assert lo < res["gain"] < hi
    assert evaluate(*synth, n_boot=0)["gain_ci"] is None


def test_tuned_k_is_in_the_grid_and_is_reported(synth):
    res = evaluate(*synth, tune_k=True, k_grid=(3, 7, 15), n_boot=0)
    assert res["k"] in (3, 7, 15)


def test_select_k_takes_the_largest_k_when_all_are_equally_good(synth):
    data, fit = synth
    flat = dataclasses.replace(data, S=np.tile(np.linspace(0.2, 0.8, len(data.models)), (len(data.queries), 1)))
    E = fit(None)(data.queries)
    assert select_k(E, flat, list(range(len(data.models))), k_grid=(3, 7, 15)) == 15  # estimates identical for all k


def test_select_k_never_reads_test_scores(synth):
    data, fit = synth
    S = data.S.copy()
    S[data.test] = np.random.default_rng(1).random((len(data.test), S.shape[1]))
    E, pool = fit(None)(data.queries), list(range(len(data.models)))
    assert select_k(E, dataclasses.replace(data, S=S), pool) == select_k(E, data, pool)


def test_select_k_warns_when_best_k_is_at_the_grid_edge(synth, capsys):
    data, fit = synth
    E, pool = fit(None)(data.queries), list(range(len(data.models)))
    select_k(E, data, pool, k_grid=(3, 10, 30))        # area still rising at the top of the grid
    assert "upper edge" in capsys.readouterr().out
    select_k(E, data, pool, k_grid=(300, 1000, 2000))  # best is the smallest k
    assert "lower edge" in capsys.readouterr().out


def test_select_k_is_quiet_when_best_k_is_interior_or_grid_has_one_value(synth, capsys):
    data, fit = synth
    E, pool = fit(None)(data.queries), list(range(len(data.models)))
    select_k(E, data, pool, k_grid=(3, 10, 100, 300, 1000))
    select_k(E, data, pool, k_grid=(10,))
    assert capsys.readouterr().out == ""
