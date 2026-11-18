"""The complete-grid accelerator must reproduce the original harness's measurements."""
import numpy as np
import pytest

from learned.evaluation import MetricContext, Policy, lambda_grid, select_k
from router import curve, evaluate, knn_estimate, realized, select_k as reference_select_k
from test_router import make_data
from types import SimpleNamespace

from preproc.data import load_data
from learned.features import baselines
from learned.full_experiments import K_GRID, predict_all_k, probe_predictions


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


@pytest.mark.parametrize("instance,budget", [(5, None), (5, 20), (5, 500), (0, 20)])
def test_real_benchmark_pipeline_matches_router_reference(tmp_path, instance, budget):
    """Real scores/splits/pools, full kNN + probe paths, area and paired intervals.

    Handcrafted features keep this regression test offline (no encoder download).
    The single-incumbent case explicitly uses the documented k=10 fallback.
    """
    full = load_data("llmrouterbench", split_seed=0)
    data = load_data("llmrouterbench", split_seed=0, instance=instance)
    embed = baselines(full, SimpleNamespace(values=np.ones((len(full.queries), 1))))["handcrafted"]
    E = embed(full.queries)
    predictions = predict_all_k(full, E, tmp_path)
    cols = [full.models.index(m) for m in data.models]
    new = None if budget is None else data.models.index(data.new_model)
    pool = [i for i in range(len(data.models)) if i != new]
    val = {k: predictions[f"val{k}"][:, np.asarray(cols)[pool]] for k in K_GRID}
    k = select_k(val, data.S[data.val][:, pool], data.cost[pool], K_GRID)
    seed = 2
    expected = evaluate(data, lambda models: embed,
                        new_model=None if new is None else data.new_model,
                        n_probes=budget, seed=seed, tune_k=len(pool) > 1,
                        k=10, n_boot=20)
    assert k == expected["k"]
    estimates = predictions[f"test{k}"][:, cols].copy()
    means = data.S[data.train].mean(axis=0)
    probe_mean = None
    if new is not None:
        predicted, mean, ids = probe_predictions(data, E, new, budget, seed)
        estimates[:, new] = predicted[k]
        np.testing.assert_array_equal(ids, expected["probes"])
        probe_mean = means.copy()
        probe_mean[new] = mean
    np.testing.assert_allclose(estimates, expected["Q_hat"], atol=1e-14, rtol=0)
    context = MetricContext(data.S[data.test], data.cost, means)
    actual, points = context.evaluate(Policy(estimates, data.S[data.test], data.cost),
                                     lambda_grid(data.cost), n_boot=20, seed=seed,
                                     probe_mean=probe_mean)
    for key in ("gain", "A", "gain_abs", "A_single_best"):
        assert actual[key] == pytest.approx(expected[key], abs=1e-10, rel=0)
    if new is not None:
        assert actual["gain_same_probes"] == pytest.approx(expected["gain_same_probes"], abs=1e-10)
    np.testing.assert_allclose([actual["gain_ci_low"], actual["gain_ci_high"]],
                               expected["gain_ci"], atol=1e-10, rtol=0)
    np.testing.assert_allclose(points, expected["curves"]["router"], atol=1e-12, rtol=0)
