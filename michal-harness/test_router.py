import numpy as np
import pytest

from router import Data, area, evaluate, knn_estimate, route


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
    data = Data([str(i) for i in range(Q)], [f"model{m}" for m in range(M)], S, cost,
                train=order[: int(0.7 * Q)], test=order[int(0.7 * Q):])
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
    evaluate(data, lambda pool: calls.append(pool) or fit(pool), new_model="model2", n_probes=20)
    assert calls == [[m for m in data.models if m != "model2"]]


def test_unseen_with_all_train_queries_as_probes_equals_seen(synth):
    data, fit = synth
    unseen = evaluate(data, fit, new_model="model2", n_probes=len(data.train))
    assert unseen["A"] == pytest.approx(evaluate(data, fit)["A"])


def test_more_probes_help(synth):
    data, fit = synth
    A = lambda n: np.mean([evaluate(data, fit, new_model="model2", n_probes=n, seed=s)["A"] for s in range(5)])
    assert A(5) < A(500)
