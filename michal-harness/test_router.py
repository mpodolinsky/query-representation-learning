import csv
import dataclasses
import json
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")  # no display needed; set before plots imports pyplot
import matplotlib.pyplot as plt

import plots
from router import (Data, Results, area, bootstrap_gain_ci, curve, evaluate, knn_estimate, knn_indices, realized,
                    recovery, route, select_k)


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
                train=order[:a], val=order[a:b], test=order[b:], theme=cluster)
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


def test_route_ties_go_to_the_cheaper_model_whatever_the_model_order():
    scores, cost = np.array([[0.5, 0.5, 0.2]]), np.array([2., 1., 0.5])
    assert route(scores, cost, 0.0)[0] == 1                      # tie at λ = 0: the cheaper of the two best
    perm = np.array([2, 0, 1])                                   # shuffle the models: the same model is chosen
    assert cost[route(scores, cost, 0.0)[0]] == cost[perm][route(scores[:, perm], cost[perm], 0.0)[0]]
    # 0.9 − 0.2·3 and 0.5 − 0.2·1 are equal up to float rounding (1e-16): still a tie, so the cheaper model 1 wins
    assert route(np.array([[0.9, 0.5]]), np.array([3., 1.]), 0.2)[0] == 1


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
    A = lambda n: np.mean([evaluate(data, fit, new_model="model2", n_probes=n, seed=s, n_boot=0, n_lambdas=100)["A"] for s in range(5)])
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


def test_results_folder_is_timestamped_and_holds_everything(synth, tmp_path):
    data, fit = synth
    out = Results(data, "synthetic", root=tmp_path)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", out.dir.name) and out.dir.parent == tmp_path
    out.run("frozen", fit, n_boot=20)
    assert sorted(p.name for p in out.dir.iterdir()) == ["meta.json", "results.csv", "runs", "split.npz"]
    meta = json.loads((out.dir / "meta.json").read_text())
    assert meta["benchmark"] == "synthetic" and meta["models"] == data.models and meta["cost"] == data.cost.tolist()
    assert np.array_equal(np.load(out.dir / "split.npz")["test"], data.test)


def test_results_csv_has_one_row_per_run(synth, tmp_path):
    data, fit = synth
    out = Results(data, "synthetic", root=tmp_path)
    seen = out.run("frozen", fit, n_boot=20)
    unseen = out.run("frozen", fit, new_model="model2", n_probes=50, seed=3, tune_k=True, n_boot=0)
    rows = list(csv.DictReader(open(out.dir / "results.csv")))
    assert [r["run"] for r in rows] == ["0000", "0001"]
    assert (rows[0]["new_model"], rows[0]["n_probes"], rows[0]["tune_k"]) == ("", "", "False")
    assert float(rows[0]["gain"]) == pytest.approx(seen["gain"]) and float(rows[0]["gain_ci_low"]) < seen["gain"]
    assert float(rows[0]["gain_abs"]) == pytest.approx(seen["gain_abs"]) and rows[0]["n_lambdas"] == "500"
    assert (rows[1]["new_model"], rows[1]["n_probes"], rows[1]["seed"], rows[1]["tune_k"]) == ("model2", "50", "3", "True")
    assert int(rows[1]["k"]) == unseen["k"] and rows[1]["gain_ci_low"] == ""  # n_boot=0: no interval


def test_saved_files_are_enough_to_redo_the_routing(synth, tmp_path):
    data, fit = synth
    out = Results(data, "synthetic", root=tmp_path)
    res = out.run("frozen", fit, n_boot=0)
    run = np.load(out.dir / "runs" / "0000.npz")
    test = np.load(out.dir / "split.npz")["test"]
    cost = np.array(json.loads((out.dir / "meta.json").read_text())["cost"])
    again = curve(realized(run["Q_hat"], data.S[test], cost, run["lambdas"]))  # no embedding, no kNN
    assert np.array_equal(again, run["curve_router"])  # exact: ties in q̂ − λ·cost resolve identically
    assert np.allclose(run["curve_router"], res["curves"]["router"])


# ---------------------------------------------------------------- neighbors, probes, plots

@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_knn_estimate_is_the_mean_over_knn_indices():
    rng = np.random.default_rng(0)
    E, S, Q = rng.normal(size=(60, 3)), rng.random((60, 4)), rng.normal(size=(5, 3))
    idx = knn_indices(E, Q, k=7)
    assert idx.shape == (5, 7)
    assert np.allclose(knn_estimate(E, S, Q, k=7), S[idx].mean(1))
    assert knn_indices(E, Q, k=500).shape == (5, 60)  # capped at the number of labeled queries


def test_evaluate_returns_the_probes_and_the_cost_range(synth):
    data, fit = synth
    seen = evaluate(data, fit, n_boot=0)
    unseen = evaluate(data, fit, new_model="model2", n_probes=30, n_boot=0)
    assert seen["probes"] is None
    assert len(unseen["probes"]) == 30 and np.isin(unseen["probes"], data.train).all()
    assert seen["cost_range"] == (data.cost.min(), data.cost.max())


def test_results_save_the_probes_of_unseen_runs_only(synth, tmp_path):
    data, fit = synth
    out = Results(data, "synthetic", root=tmp_path)
    out.run("frozen", fit, n_boot=0)
    unseen = out.run("frozen", fit, new_model="model2", n_probes=30, n_boot=0)
    assert "probes" not in np.load(out.dir / "runs" / "0000.npz")
    assert np.array_equal(np.load(out.dir / "runs" / "0001.npz")["probes"], unseen["probes"])


@pytest.fixture(scope="module")
def projected(synth):
    data, fit = synth
    E = fit(None)(data.queries)
    Z, ratio = plots.pca_project(E, data.train)
    return data, E, Z, ratio


def test_pca_project_is_fitted_on_the_given_rows(projected):
    data, E, Z, ratio = projected
    assert Z.shape == (len(E), 2)
    assert 0 < ratio[1] <= ratio[0] and ratio.sum() <= 1
    assert np.allclose(Z[data.train].mean(0), 0, atol=1e-8)  # centered on the training rows, not on all rows


def _visible(fig):
    return sum(ax.get_visible() for ax in fig.axes)


def test_cost_quality_plots(synth):
    data, fit = synth
    results = {k: evaluate(data, fit, k=k, n_boot=0) for k in (3, 10, 50)}
    assert len(plots.plot_curves(results[10], "t").axes[0].lines) == 3          # router, single best, oracle
    assert len(plots.plot_curves_by_k(results, 50, "t").axes[0].lines) == 5     # three k plus single best and oracle
    gains = np.random.default_rng(0).random((3, 4))
    assert len(plots.plot_gain_vs_probes([1, 10, 100], gains, 0.1).axes[0].lines) == 2
    assert len(plots.plot_gain_vs_probes([1, 10, 100], gains, 0.1, gains).axes[0].lines) == 3
    unseen = evaluate(data, fit, new_model="model2", n_probes=20, n_boot=0)
    assert len(plots.plot_curves(unseen, "t").axes[0].lines) == 4              # plus the same-probes single best


def _titles(fig):
    return [ax.get_title() for ax in fig.axes if ax.get_visible()]


def test_pca_group_panels_follow_the_groups_and_the_cap(projected):
    data, E, Z, ratio = projected
    fig = plots.plot_pca_groups(Z, ratio, data.theme, "t")
    assert len(_titles(fig)) == len(np.unique(data.theme))
    assert [t.split(" (")[0] for t in _titles(fig)] == [str(g) for g in np.unique(data.theme)]  # label order, not size
    assert len(_titles(plots.plot_pca_groups(Z, ratio, data.theme, "t", max_groups=2))) == 2


def test_pca_groups_can_show_every_group_in_the_given_order_including_empty_ones(projected):
    data, E, Z, ratio = projected
    picks = np.where(data.theme % 2 == 0, 1, 3)                    # only models 1 and 3 are ever "chosen"
    names = dict(enumerate(data.models))
    fig = plots.plot_pca_groups(Z, ratio, picks, "t", names=names, groups=range(len(data.models)))
    titles = _titles(fig)
    assert [t.split(" (")[0] for t in titles] == data.models        # original model order, all models
    assert [t.split("n = ")[1] for t in titles] == ["0)", f"{(picks == 1).sum()})", "0)", f"{(picks == 3).sum()})", "0)"]
    assert any(t.get_text() == "none" for t in fig.axes[0].texts)   # an empty panel says so


def test_pca_quality_has_one_panel_per_model_and_a_colorbar(projected):
    data, E, Z, ratio = projected
    fig = plots.plot_pca_quality(Z, ratio, data.S, data.models)
    assert _visible(fig) == len(data.models) + 1


def test_explained_variance_has_one_line_per_embedding_and_is_cumulative(projected):
    data, E, Z, ratio = projected
    fig = plots.plot_explained_variance({"a": E, "b": E * 3}, fit_idx=data.train, max_components=5)
    lines = fig.axes[0].lines
    assert len(lines) == 2 and (np.diff(lines[0].get_ydata()) >= 0).all() and lines[0].get_ydata()[-1] <= 1


def test_probe_and_neighbor_plots_label_what_they_show(projected):
    data, E, Z, ratio = projected
    probes, query = data.train[:20], data.test[0]
    neighbors = data.train[knn_indices(E[data.train], E[[query]], 10)[0]]
    probe_neighbors = probes[knn_indices(E[probes], E[[query]], 5)[0]]
    fig = plots.plot_probes(Z, ratio, data.train, probes, routed=data.test[:50])
    assert [t.get_text() for t in fig.axes[0].get_legend().get_texts()][-1] == "probes (n = 20)"
    fig = plots.plot_neighbors(Z, ratio, data.train, query, neighbors, probes, probe_neighbors)
    texts = [t.get_text() for t in fig.axes[0].get_legend().get_texts()]
    assert "query" in texts and "neighbors for the pool models (k = 10)" in texts
    assert "neighbors for the new model (k = 5)" in texts


# ---------------------------------------------------------------- baselines and recovery in the unseen setting

def test_unseen_baseline_is_the_full_information_single_best_whatever_the_probes(synth):
    data, fit = synth
    seen = evaluate(data, fit, n_boot=0)
    for n, seed in [(2, 0), (50, 1), (400, 2)]:
        unseen = evaluate(data, fit, new_model="model2", n_probes=n, seed=seed, n_boot=0)
        assert unseen["A_single_best"] == pytest.approx(seen["A_single_best"])
        assert np.allclose(unseen["curves"]["single_best"], seen["curves"]["single_best"])


def test_same_probes_baseline_exists_only_in_the_unseen_setting_and_is_noisier(synth):
    data, fit = synth
    assert evaluate(data, fit, n_boot=0)["gain_same_probes"] is None
    few = evaluate(data, fit, new_model="model2", n_probes=3, n_boot=0)
    assert "single_best_probes" in few["curves"] and few["q_mean_probes"][2] != few["q_mean"][2]
    all_train = evaluate(data, fit, new_model="model2", n_probes=len(data.train), n_boot=0)
    assert all_train["gain_same_probes"] == pytest.approx(all_train["gain"])  # all labels known: same baseline


def test_recovery_is_one_with_all_labels_and_nan_without_a_seen_gain(synth):
    data, fit = synth
    seen = evaluate(data, fit, n_boot=0)
    unseen = evaluate(data, fit, new_model="model2", n_probes=len(data.train), n_boot=0)
    assert recovery(unseen, seen) == pytest.approx(1)
    assert recovery({"gain": 0.05}, {"gain": 0.10}) == pytest.approx(0.5)
    assert np.isnan(recovery({"gain": 0.05}, {"gain": -0.01}))


def test_results_report_the_three_numbers(synth, tmp_path):
    data, fit = synth
    out = Results(data, "synthetic", root=tmp_path)
    out.run("frozen", fit, new_model="model2", n_probes=20, n_boot=0)            # no seen run yet: no recovery
    seen = out.run("frozen", fit, n_boot=0)
    unseen = out.run("frozen", fit, new_model="model2", n_probes=60, n_boot=0)
    rows = list(csv.DictReader(open(out.dir / "results.csv")))
    assert rows[0]["recovery"] == "" and rows[0]["gain_same_probes"] != ""
    assert rows[1]["gain_same_probes"] == "" and rows[1]["recovery"] == ""        # the seen run itself
    assert float(rows[2]["recovery"]) == pytest.approx(recovery(unseen, seen))
    assert float(rows[2]["gain"]) == pytest.approx(unseen["gain"])
    saved = np.load(out.dir / "runs" / "0002.npz")
    assert "q_mean_probes" in saved and "curve_single_best_probes" in saved
