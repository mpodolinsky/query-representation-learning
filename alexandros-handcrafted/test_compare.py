"""Plumbing tests for the unified comparison, the embedding views, the paired tests and the report builder, on fake
data with the stub sentence encoder (no network, tiny training). Run from this folder: python -m pytest -q test_compare.py"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "michal-harness"))
sys.path.insert(0, str(HERE))

pytest.importorskip("torch")
import preproc.data as pdata  # noqa: E402
from test_handcrafted import DATASETS  # noqa: E402

M = 4


def fake_full(Q=500, seed=0, split_seed=0):
    """preproc.data.Data with text queries, a dataset-name theme, a Level-2 column and scores that depend on it."""
    rng = np.random.default_rng(seed)
    names = list(DATASETS)
    ds = rng.integers(len(names), size=Q)
    sub = np.array([DATASETS[names[d]][0] for d in ds], dtype=object)
    subs = sorted(set(sub.tolist()))
    queries = [rng.choice(DATASETS[names[d]][1]).format(a=rng.integers(2, 99), b=rng.integers(2, 99), c=rng.integers(2, 999))
               + f" (query {i})" for i, d in enumerate(ds)]
    quality = np.clip(np.linspace(0.3, 0.7, M)[:, None] + rng.uniform(-0.3, 0.3, (M, len(subs))), 0, 1)
    S = (rng.random((Q, M)) < quality[:, [subs.index(s) for s in sub]].T).astype(float)
    order = np.random.default_rng(100 + split_seed).permutation(Q)
    a, b = int(0.6 * Q), int(0.7 * Q)
    data = pdata.Data(queries, [f"model{m}" for m in range(M)], S, np.geomspace(1, 20, M), order[:a], order[a:b], order[b:],
                      theme=np.array(names, dtype=object)[ds], split_seed=split_seed, benchmark="fakebench")
    data.task_level2 = sub
    return data


INSTANCES = pd.DataFrame([{"instance": 0, "epoch": 1, "new_model": "model1", "pool": ["model0", "model1"]},        # one incumbent
                          {"instance": 1, "epoch": 3, "new_model": "model3", "pool": ["model0", "model1", "model2", "model3"]}])


def fake_load_data(benchmark, split_seed=0, epoch=None, instance=None, **kw):
    full = fake_full(split_seed=split_seed)
    if instance is None:
        return full
    inst = INSTANCES.iloc[instance]
    cols = [full.models.index(m) for m in inst.pool]
    import dataclasses
    data = dataclasses.replace(full, models=list(inst.pool), S=full.S[:, cols], cost=full.cost[cols], epoch=int(inst.epoch), new_model=inst.new_model)
    data.task_level2 = full.task_level2
    return data


@pytest.fixture
def fake_loader(monkeypatch):
    monkeypatch.setattr(pdata, "load_data", fake_load_data)
    monkeypatch.setattr(pdata, "unseen_instances", lambda benchmark: INSTANCES)


@pytest.fixture(scope="module")
def compare_root(tmp_path_factory):
    """One small unified run, shared by the tests below (built with a module-scoped monkeypatch)."""
    import compare_representations as cmp
    mp = pytest.MonkeyPatch()
    mp.setattr(pdata, "load_data", fake_load_data)
    mp.setattr(pdata, "unseen_instances", lambda benchmark: INSTANCES)
    root = tmp_path_factory.mktemp("compare")
    args = ["--benchmarks", "fakebench", "--split-seeds", "0", "--encoder", "stub", "--tokenizer", "whitespace",
            "--representations", "task_type_L1", "task_type_L12", "stats", "handcrafted", "frozen", "combined", "regression", "contrastive_hc",
            "--training-seeds", "0", "--epochs", "1", "--probe-budgets", "2", "10", "--probe-seeds", "1", "--n-boot", "20",
            "--n-boot-unseen", "10", "--k-grid", "10", "20", "--n-lambdas", "40", "--level-labels", "none",
            "--output", str(root), "--cache", str(root / "cache"), "--threads", "1"]
    cmp.main(args)
    mp.undo()
    return root, args


def test_compare_runner_rows_shards_embeddings_and_resume(compare_root, fake_loader, capsys):
    root, args = compare_root
    m = pd.read_csv(root / "metrics.csv")
    reps = {"task_type_L1", "task_type_L12", "stats", "handcrafted", "frozen", "combined", "regression", "contrastive_hc"}
    assert set(m.embedding) == reps
    assert set(m.instance) == {-1, 0, 1} and set(m.setting) == {"seen", "unseen"}
    assert len(m) == len(reps) * (3 + 2 * 2 * 1)                          # 3 seen runs + 2 instances x 2 budgets x 1 seed
    single = m[(m.instance == 0) & (m.setting == "unseen")]
    assert (single.k == 10).all() and (~single.k_tuned).all()              # one incumbent: fixed k = 10
    assert np.isfinite(m.gain).all() and m[m.setting == "seen"].gain_ci_low.notna().all()
    assert m[m.setting == "unseen"].recovery.notna().all()
    emb = root / "embeddings" / "fakebench" / "split0"
    assert {p.stem for p in emb.glob("*.npy")} == reps and (emb / "labels.npz").exists()
    labels = np.load(emb / "labels.npz")
    assert set(labels.files) >= {"theme", "task_level1", "task_level2", "train", "test"}
    assert np.load(emb / "handcrafted.npy").shape[1] == np.load(emb / "task_type_L12.npy").shape[1] + 15
    assert np.load(emb / "combined.npy").shape[1] == 32 + np.load(emb / "handcrafted.npy").shape[1]
    shards = list((root / "shards").glob("*.json"))
    assert len(shards) == len(reps) * 3
    # resume: nothing is recomputed, the metrics are rewritten identically
    import compare_representations as cmp
    cmp.main(args)
    out = capsys.readouterr().out
    assert "seen   " not in out and len(pd.read_csv(root / "metrics.csv")) == len(m)
    cmp.main(args + ["--dry-run"])
    assert "shards done" in capsys.readouterr().out


def test_stub_features_are_deterministic_and_normalized():
    from compare_representations import StubSentenceFeatures
    s = StubSentenceFeatures(["hello world", "def f(x): return x"])
    assert s.values.shape == (2, 32) and np.allclose(np.linalg.norm(s.values, axis=1), 1)
    assert np.allclose(s.embed(["hello world"]), s.values[:1]) and np.allclose(s.embed(["new text"]), StubSentenceFeatures(["new text"]).values)


def test_concat_features_balance_the_blocks():
    from compare_representations import ConcatFeatures, StubSentenceFeatures
    from handcrafted import HandcraftedEmbedding
    data = fake_full()
    s = StubSentenceFeatures(data.queries)
    hand = HandcraftedEmbedding(data, levels=(1, 2), tokenizer="whitespace")
    c = ConcatFeatures(s, hand, data)
    tr = data.train
    assert c.values.shape == (len(data.queries), 32 + hand.dim)
    assert c.values[tr, :32].var(0).sum() == pytest.approx(c.values[tr, 32:].var(0).sum(), rel=1e-4)
    assert np.allclose(c.embed(data.queries[:3]), c.values[:3])


def test_embedding_views_numbers_and_figures(compare_root, tmp_path):
    import embedding_views as ev
    root, _ = compare_root
    out = tmp_path / "views"
    ev.main(["--embeddings", str(root / "embeddings"), "--benchmark", "fakebench", "--names", "task_type_L1", "frozen",
             "--sample", "200", "--out", str(out), "--labels", "theme", "task_level1"])
    t = pd.read_csv(out / "label_structure.csv")
    assert set(t.representation) == {"task_type_L1", "frozen"} and set(t.label) == {"theme", "task_level1"}
    row = t[(t.representation == "task_type_L1") & (t.label == "task_level1")].iloc[0]
    assert row.linear_probe_acc == pytest.approx(1.0) and row.knn_purity_k10 == pytest.approx(1.0)   # its own label
    assert (t.majority < 1).all() and t.silhouette.notna().all()
    figs = {p.name for p in (out / "views").glob("*.png")}
    assert {"fakebench_frozen_pca_theme.png", "fakebench_frozen_tsne_task_level1.png", "fakebench_task_type_L1_pca_task_level1.png"} <= figs
    # a second call merges into the same table instead of dropping the earlier rows
    ev.main(["--embeddings", str(root / "embeddings"), "--benchmark", "fakebench", "--names", "stats", "--no-tsne",
             "--no-figures", "--out", str(out), "--labels", "theme"])
    t2 = pd.read_csv(out / "label_structure.csv")
    assert set(t2.representation) == {"task_type_L1", "frozen", "stats"}


def test_paired_tests_on_the_compare_root(compare_root, fake_loader, tmp_path):
    import paired_tests as pt
    root, _ = compare_root
    out = tmp_path / "paired"
    pt.main(["--compare-root", str(root), "--reference", "handcrafted", "--n-boot", "50", "--n-probes", "10", "--out", str(out)])
    seen = pd.read_csv(out / "paired_seen.csv")
    assert set(seen.b) == {"handcrafted"} and "handcrafted" not in set(seen.a)
    assert set(seen.instance) == {-1, 0, 1} and len(seen[seen.instance == -1]) == 7
    assert ((seen.d_gain_ci_low <= seen.d_gain_boot_mean) & (seen.d_gain_boot_mean <= seen.d_gain_ci_high)).all()
    assert ((seen.d_gain_p >= 0) & (seen.d_gain_p <= 1)).all()
    unseen = pd.read_csv(out / "paired_unseen.csv")
    assert set(unseen.n_probes) == {10} and set(unseen.new_model) == {"model1", "model3"}
    summary = (out / "paired_summary.md").read_text()
    assert "## Seen setting" in summary and "## Unseen setting" in summary and "| frozen | handcrafted |" in summary
    s = pd.read_csv(out / "paired_seen_summary.csv")
    assert (s.n == 1).all() and set(s.columns) >= {"wins", "ci_excludes_0", "median_p"}


def test_build_report_with_and_without_inputs(compare_root, fake_loader, tmp_path, monkeypatch):
    import build_report as br
    root, _ = compare_root
    monkeypatch.setattr(br, "UNIFIED", root / "metrics.csv")
    monkeypatch.setattr(br, "CMP", tmp_path / "nothing")
    out = tmp_path / "REPORT.md"
    br.main(["--out", str(out)])
    text = out.read_text()
    for section in ("## 1. In one paragraph", "## 2. Data", "### 3.2 The learned embeddings", "### 5.3 Unified comparison",
                    "## 6. Observations", "## 7. What is pending"):
        assert section in text
    assert "contrastive_hc" in text and "Task-type recovery per level" in text
    assert "not found: run paired_tests.py" in text and (tmp_path / "report_data.json").exists()
    monkeypatch.setattr(br, "UNIFIED", tmp_path / "missing.csv")
    monkeypatch.setattr(br, "NIK", tmp_path / "missing")
    monkeypatch.setattr(br, "MINE", tmp_path / "missing")
    br.main(["--out", str(out)])
    text = out.read_text()
    assert "Not run yet" in text and "seen_summary.csv not found" in text
