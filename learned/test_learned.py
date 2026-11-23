"""Small offline tests for training isolation, objectives, integration and proposal metrics."""
import copy
import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import torch

from preproc.data import Data
from learned.features import SentenceFeatures, baselines
from learned.model import contrastive_loss
from learned.train import TrainConfig, make_fit
from learned.experiments import parser, probes_to_target, run, task_recovery


@pytest.fixture
def small():
    torch.set_num_threads(1)
    rng = np.random.default_rng(1)
    x = rng.normal(size=(96, 12)).astype(np.float32)
    scores = (x[:, :3] > 0).astype(float)
    data = Data([f"query {i}" for i in range(96)], ["a", "b", "new"], scores,
                np.array([0.001, 0.01, 0.02]), np.arange(64), np.arange(64, 80),
                np.arange(80, 96), theme=np.array(["math", "code"] * 48), new_model="new")

    class Features:
        values = x
        key = "synthetic-features"
        positions = {q: i for i, q in enumerate(data.queries)}
        def embed(self, queries):
            return x[[self.positions[q] for q in queries]]
    return data, Features()


@pytest.mark.parametrize("objective", ["regression", "contrastive"])
def test_training_excludes_held_out_model_and_external_splits(small, tmp_path, objective):
    data, features = small
    config = TrainConfig(objective=objective, epochs=3, batch_size=16, embedding_dim=4, seed=2)
    first = make_fit(data, features, config, tmp_path / "first")(["a", "b"])
    changed = copy.deepcopy(data)
    changed.S[:, 2] = 1 - changed.S[:, 2]  # all held-out-model labels
    changed.S[np.r_[data.val, data.test], :2] = 1 - changed.S[np.r_[data.val, data.test], :2]
    second = make_fit(changed, features, config, tmp_path / "second")(["a", "b"])
    np.testing.assert_array_equal(first(data.queries), second(data.queries))
    metadata = json.loads(next((tmp_path / "first").glob("*/training.json")).read_text())
    assert metadata["models"] == ["a", "b"]
    fit, stop = set(metadata["fit_indices"]), set(metadata["stop_indices"])
    assert not fit & stop
    assert fit | stop == set(data.train)


def test_reload_order_and_different_pool_checkpoints(small, tmp_path):
    data, features = small
    config = TrainConfig(epochs=2, batch_size=16, embedding_dim=4)
    fit = make_fit(data, features, config, tmp_path)
    embed = fit(["a", "b"])
    E = embed(data.queries)
    reloaded = make_fit(data, features, config, tmp_path)(["a", "b"])
    np.testing.assert_array_equal(E[[5, 1, 5]], reloaded(["query 5", "query 1", "query 5"]))
    assert reloaded([]).shape == (0, 4)
    np.testing.assert_allclose(np.linalg.norm(E, axis=1), 1, atol=1e-6)
    fit(["a", "b", "new"])
    assert len(list(tmp_path.glob("*/model.pt"))) == 2


def test_regression_learns_profiles(small, tmp_path):
    data, features = small
    cfg = TrainConfig(epochs=25, patience=25, batch_size=16, hidden_dim=16,
                      embedding_dim=8, learning_rate=0.02)
    make_fit(data, features, cfg, tmp_path)(data.models)
    history = json.loads(next(tmp_path.glob("*/training.json")).read_text())["history"]
    assert min(row["stop_loss"] for row in history) < history[0]["stop_loss"] * 0.8


def test_contrastive_loss_rewards_matching_geometry_and_handles_single_pair_class():
    profiles = torch.tensor([[0., 1.], [0., 1.], [1., 0.]])
    good = torch.tensor([[1., 0.], [1., 0.], [-1., 0.]], requires_grad=True)
    bad = torch.tensor([[1., 0.], [-1., 0.], [1., 0.]])
    assert contrastive_loss(good, profiles) < contrastive_loss(bad, profiles)
    for y in [profiles, torch.zeros_like(profiles), torch.eye(3)]:
        loss = contrastive_loss(good, y)
        assert torch.isfinite(loss)
        loss.backward()
        assert torch.isfinite(good.grad).all()


def test_features_cache_and_query_order(tmp_path, monkeypatch):
    calls = []
    def encode(self, queries):
        calls.append(list(queries))
        return np.array([[len(q), 1] for q in queries], dtype=np.float32)
    monkeypatch.setattr(SentenceFeatures, "_encode", encode)
    first = SentenceFeatures(["a", "long"], tmp_path)
    second = SentenceFeatures(["a", "long"], tmp_path)
    assert len(calls) == 1
    np.testing.assert_array_equal(second.embed(["long", "a", "long"]), first.values[[1, 0, 1]])
    assert second.embed([]).shape == (0, 2)
    assert second.embed(["new text"]).shape == (1, 2)


def test_baseline_standardization_uses_train_only(small):
    data, features = small
    first = baselines(data, features)
    changed = replace(data, queries=list(data.queries))
    changed.queries[-1] = "long test query " * 1000
    second = baselines(changed, features)
    for name in ("handcrafted", "combined", "combined_balanced"):
        np.testing.assert_allclose(first[name](data.queries[:64]), second[name](data.queries[:64]))
    assert set(first) == {"task_type", "handcrafted", "frozen", "combined", "combined_balanced"}
    with pytest.raises(ValueError, match="labeled benchmark"):
        first["task_type"](["unseen question"])


def test_balanced_concatenation_matches_train_block_energy(small):
    data, features = small
    embeds = baselines(data, features)
    original = embeds["combined"](data.queries)
    balanced = embeds["combined_balanced"](data.queries)
    d = features.values.shape[1]
    np.testing.assert_array_equal(balanced[:, :d], features.values)
    np.testing.assert_allclose(np.square(balanced[data.train, :d]).sum(1).mean(),
                               np.square(balanced[data.train, d:]).sum(1).mean(), rtol=1e-6)
    # The historical baseline is preserved; balancing changes only its second block.
    np.testing.assert_array_equal(original[:, d:], embeds["handcrafted"](data.queries))
    assert not np.allclose(original[:, d:], balanced[:, d:])


def test_proposal_metrics():
    assert probes_to_target([50, 1, 10], [0.91, 0.7, 0.85], 1.0) == 50
    assert probes_to_target([1, 10], [0.9, 0.8], 1.0) == 1
    assert probes_to_target([1, 10], [0.1, 0.2], 1.0) is None
    assert task_recovery(0.6, 0.8) == pytest.approx(0.75)
    assert np.isnan(task_recovery(0.6, 0))


def test_experiment_runner_seen_unseen_and_metrics(small, tmp_path, monkeypatch):
    import learned.experiments as experiments
    data, features = small
    monkeypatch.setattr(experiments, "load_data", lambda *a, **kw: data)
    monkeypatch.setattr(experiments, "unseen_instances", lambda *a: [0])
    monkeypatch.setattr(experiments, "SentenceFeatures", lambda *a, **kw: features)
    cache = tmp_path / "cache"
    cache.mkdir()
    args = parser().parse_args(["--representations", "task_type", "frozen", "regression", "contrastive",
        "--instances", "0", "--probe-budgets", "1", "10", "--probe-seeds", "0", "1",
        "--epochs", "2", "--n-boot", "0", "--n-lambdas", "20", "--fixed-k",
        "--output", str(tmp_path / "runs"), "--cache", str(cache)])
    output = run(args)
    metrics = pd.read_csv(output / "metrics.csv")
    assert len(metrics) == 4 * (1 + 1 + 2 * 2)
    assert np.isfinite(metrics.A).all()
    learned = metrics[metrics.embedding.isin(["regression", "contrastive"])]
    assert np.isfinite(learned.task_type_recovery).all()
    assert len(pd.read_csv(output / "probes_to_target.csv")) == 4 * 2
    assert list(output.glob("**/cost_quality_seen.png"))
    assert list(output.glob("**/area_vs_probes.png"))
    # Two objectives, each with a seen and an unseen checkpoint, not one per budget/seed.
    assert len(list(cache.glob("checkpoints/*/model.pt"))) == 4


def test_single_incumbent_uses_fixed_k_without_division_by_zero(small, tmp_path, monkeypatch):
    import learned.experiments as experiments
    data, features = small
    data = replace(data, models=data.models[:2], S=data.S[:, :2], cost=data.cost[:2], new_model="b")
    monkeypatch.setattr(experiments, "load_data", lambda *a, **kw: data)
    monkeypatch.setattr(experiments, "unseen_instances", lambda *a: [0])
    monkeypatch.setattr(experiments, "SentenceFeatures", lambda *a, **kw: features)
    cache = tmp_path / "cache"
    cache.mkdir()
    args = parser().parse_args(["--representations", "frozen", "--instances", "0",
        "--probe-budgets", "1", "--n-boot", "0", "--n-lambdas", "20",
        "--output", str(tmp_path / "runs"), "--cache", str(cache)])
    with np.errstate(divide="raise", invalid="raise"):
        output = run(args)
    metrics = pd.read_csv(output / "metrics.csv")
    assert metrics[metrics.setting == "unseen"].k.tolist() == [10]
