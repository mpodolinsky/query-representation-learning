"""Checks of the processed data, the replay, the splits and the probe sampler. Run from the repo root:
    python -m pytest preproc"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from preproc.data import (BENCHMARKS, DATA_DIR, MODEL_TABLES, SPLIT_SEEDS, load_data, load_split, release_epochs,
                          sample_probes, unseen_instances)

HERE = Path(__file__).parent
EXPECTED = {"llmrouterbench": dict(queries=12068, models=13, events=11, instances=12, themes=9),
            "routerbench": dict(queries=36478, models=11, events=6, instances=9, themes=12)}


@pytest.fixture(scope="module", params=BENCHMARKS)
def bench(request):
    return request.param


def test_score_matrix_complete_and_in_unit_interval(bench):
    d = load_data(bench)
    e = EXPECTED[bench]
    assert d.S.shape == (e["queries"], e["models"])
    assert not np.isnan(d.S).any() and d.S.min() >= 0 and d.S.max() <= 1
    assert len(set(d.theme)) == e["themes"] and len(d.query_ids) == len(set(d.query_ids))


def test_long_table_matches_matrix(bench):
    scores = pd.read_parquet(DATA_DIR / bench / "scores.parquet")
    d = load_data(bench)
    assert len(scores) == d.S.size and set(scores.columns) == {"query_id", "model", "score", "cost", "cost_imputed"}
    assert np.array_equal(scores.score.to_numpy().reshape(d.S.shape), d.S)  # rows in query order, models in order
    assert (scores.cost > 0).all()


def test_models_and_costs(bench):
    models = pd.read_csv(DATA_DIR / bench / "models.csv")
    assert models.model.tolist() == [m[0] for m in MODEL_TABLES[bench]] == load_data(bench).models
    scores = pd.read_parquet(DATA_DIR / bench / "scores.parquet")
    assert np.allclose(scores.groupby("model").cost.mean()[models.model], models.mean_cost)
    assert np.allclose(load_data(bench).cost, models.mean_cost)


def test_epochs_and_instances(bench):
    epochs, inst = release_epochs(bench), unseen_instances(bench)
    assert len(epochs) == EXPECTED[bench]["events"] and len(inst) == EXPECTED[bench]["instances"]
    assert sorted(m for e in epochs.new_models for m in e) == sorted(m[0] for m in MODEL_TABLES[bench])
    date = {m[0]: m[2] for m in MODEL_TABLES[bench]}
    for _, i in inst.iterrows():
        assert i.pool[-1] == i.new_model
        assert all(date[m] < i.date for m in i.pool[:-1])  # incumbents released strictly earlier (no tied sibling)
        assert set(i.pool[:-1]) == {m for m, dt in date.items() if dt < i.date}
    assert epochs.new_models.iloc[0] not in inst.new_model.tolist()  # the first event is the initial pool


def test_load_data_pools(bench):
    full = load_data(bench)
    for i, inst in unseen_instances(bench).iterrows():
        d = load_data(bench, instance=i)
        assert d.models == inst.pool and d.new_model == inst.new_model and d.epoch == inst.epoch
        cols = [full.models.index(m) for m in d.models]
        assert np.array_equal(d.S, full.S[:, cols]) and np.array_equal(d.cost, full.cost[cols])
    for t, ep in release_epochs(bench).iterrows():
        assert load_data(bench, epoch=t).models == ep.pool
    assert load_data(bench, epoch=len(release_epochs(bench)) - 1).models == full.models


def test_splits(bench):
    d = load_data(bench)
    tests = []
    for s in SPLIT_SEEDS:
        tr, va, te = load_split(bench, s)
        assert len(np.intersect1d(tr, va)) == len(np.intersect1d(tr, te)) == len(np.intersect1d(va, te)) == 0
        assert np.array_equal(np.sort(np.concatenate([tr, va, te])), np.arange(len(d.queries)))
        for t in set(d.theme):
            n = (d.theme == t).sum()
            parts = [(d.theme[p] == t).sum() for p in (tr, va, te)]
            assert min(parts) > 0, f"theme {t} missing from a split"
            assert abs(parts[0] - 0.7 * n) <= 1 and abs(parts[1] - 0.1 * n) <= 1
        tests.append(set(te))
    assert tests[0] != tests[1] != tests[2]
    # the split does not depend on the pool, so seen and unseen runs are paired
    a, b = load_data(bench, split_seed=1, epoch=0), load_data(bench, split_seed=1, instance=0)
    assert np.array_equal(a.train, b.train) and np.array_equal(a.test, b.test)


def test_query_text(bench):
    q = pd.read_parquet(DATA_DIR / bench / "queries.parquet")
    assert q["query"].str.len().gt(0).all()
    assert all(a in b for a, b in zip(q["query"], q["prompt"]))  # the bare question is part of the full prompt
    assert load_data(bench, text="prompt").queries == q.prompt.tolist()
    if bench == "llmrouterbench":
        arc = q[q.theme == "arc-agi"]
        assert (arc["query"] == arc.prompt).all()  # ARC-AGI has no bare question
        assert (q[q.theme == "mmlupro"].subtask.nunique() == 14) and q[q.theme == "hle"].subtask.nunique() == 8


def test_probes_nested_and_from_train():
    d = load_data("llmrouterbench")
    for theme in (None, d.theme):
        for seed in range(3):
            big = sample_probes(d.train, 500, seed, theme)
            assert len(set(big)) == 500 and set(big) <= set(d.train)
            for n in (1, 5, 50, 200):
                assert np.array_equal(sample_probes(d.train, n, seed, theme), big[:n])
    assert not np.array_equal(sample_probes(d.train, 50, 0), sample_probes(d.train, 50, 1))


def test_stratified_probes_are_proportional(bench):
    d = load_data(bench)
    share = pd.Series(d.theme[d.train]).value_counts(normalize=True)
    for n in (10, 100, 1000):
        for seed in range(3):
            counts = pd.Series(d.theme[sample_probes(d.train, n, seed, d.theme)]).value_counts()
            miscount = (counts.reindex(share.index, fill_value=0) - n * share).abs()
            assert miscount.max() <= 1.5, (n, seed, miscount.max())


def _harness():
    spec = importlib.util.spec_from_file_location("router", HERE.parent / "michal-harness" / "router.py")
    router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(router)
    return router


def test_harness_runs_on_load_data():
    """`evaluate` takes our Data as is, and its probes are exactly `sample_probes` (default rule)."""
    router = _harness()
    d = load_data("llmrouterbench", instance=7)  # gpt-5-chat joins a pool of 8
    themes = sorted(set(d.theme))
    fit = lambda pool: (lambda qs: (d.theme[:, None] == np.array(themes)).astype(float))  # one-hot task type
    seen = router.evaluate(d, fit, n_boot=0, n_lambdas=50)
    unseen = router.evaluate(d, fit, new_model=d.new_model, n_probes=20, seed=3, n_boot=0, n_lambdas=50)
    assert np.isfinite(seen["gain"]) and np.isfinite(unseen["gain"])
    assert np.array_equal(unseen["probes"], sample_probes(d.train, 20, 3))


@pytest.mark.skipif(not (HERE.parent / "deps/LLMRouterBench/results/bench-release").exists()
                    or not (HERE.parent.parent / "routerbench_0shot.pkl").exists(), reason="raw data not downloaded")
def test_rebuild_reproduces_tables(tmp_path):
    subprocess.run([sys.executable, str(HERE / "build.py"), "--out", str(tmp_path / "data"),
                    "--report", str(tmp_path / "report.md")], check=True, capture_output=True)
    digests = lambda p: re.findall(r"- `(\S+)`: ([0-9a-f]{16})", Path(p).read_text())
    assert digests(tmp_path / "report.md") == digests(HERE / "reports/build_report.md")
    for b in BENCHMARKS:
        for s in SPLIT_SEEDS:
            a, c = np.load(DATA_DIR / b / "splits" / f"seed{s}.npz"), np.load(tmp_path / "data" / b / "splits" / f"seed{s}.npz")
            assert all(np.array_equal(a[k], c[k]) for k in ("train", "val", "test"))
