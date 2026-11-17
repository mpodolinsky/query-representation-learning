"""The complete-grid accelerator must reproduce the original harness's measurements."""
import numpy as np
import pytest

from learned.evaluation import MetricContext, Policy, lambda_grid, select_k
from router import curve, evaluate, knn_estimate, realized, select_k as reference_select_k
from test_router import make_data


@pytest.mark.parametrize("models", [1, 2, 5, 13])
@pytest.mark.parametrize("discrete", [False, True])
def test_transition_curves_match_reference(models, discrete):
    rng = np.random.default_rng(models)
    scores = rng.random((90, models))
    if discrete:
        scores = np.round(scores * 5) / 5
    truth = rng.random(scores.shape)
    cost = rng.permutation(np.geomspace(0.0001, 0.1, models))
    lambdas = np.r_[0, np.geomspace(0.001, 1e6, 501)]
    result = Policy(scores, truth, cost).events(lambdas).curve()
    expected = curve(realized(scores, truth, cost, lambdas))
    np.testing.assert_allclose(result, expected, atol=2e-14, rtol=1e-12)


def test_equal_prices_and_near_ties_match_reference():
    scores = np.array([[0.5, 0.5 + 1e-9, 0.5], [0, 1e-9 - 1e-15, 1e-9 + 1e-15],
                       [1, 0, 1], [0.2, 0.7, 0.6]])
    truth = np.arange(12).reshape(4, 3) / 12
    for cost in [np.array([0.1, 0.2, 0.3]), np.array([0.1, 0.1, 0.3])]:
        grid = lambda_grid(cost)
        np.testing.assert_allclose(Policy(scores, truth, cost).events(grid).curve(),
                                   curve(realized(scores, truth, cost, grid)), atol=1e-13)


def test_metrics_and_paired_bootstrap_match_reference():
    data, fit = make_data(Q=300, M=5, seed=3)
    result = evaluate(data, fit, new_model="model4", n_probes=20, seed=2, n_boot=100)
    ctx = MetricContext(data.S[data.test], data.cost, data.S[data.train].mean(axis=0))
    policy = Policy(result["Q_hat"], data.S[data.test], data.cost)
    metrics, points = ctx.evaluate(policy, result["lambdas"], n_boot=100, seed=2,
                                    probe_mean=result["q_mean_probes"])
    for key in ("A", "A_single_best", "gain", "gain_abs", "gain_same_probes"):
        assert metrics[key] == pytest.approx(result[key], abs=1e-11)
    np.testing.assert_allclose(points, result["curves"]["router"], atol=1e-13)
    np.testing.assert_allclose([metrics["gain_ci_low"], metrics["gain_ci_high"]],
                               result["gain_ci"], atol=1e-11)


def test_validation_k_matches_reference():
    data, fit = make_data(Q=800, M=4, seed=7)
    E = fit(data.models)(data.queries)
    ks = (5, 10, 20, 50)
    estimates = {k: knn_estimate(E[data.train], data.S[data.train], E[data.val], k) for k in ks}
    actual = select_k(estimates, data.S[data.val], data.cost, ks)
    expected = reference_select_k(E, data, list(range(4)), k_grid=ks)
    assert actual == expected
