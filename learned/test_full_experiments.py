"""Full-grid coverage, resumability, and exact per-k neighbor estimates."""
from dataclasses import replace
import json

import numpy as np
import pandas as pd
import pytest

from learned.full_experiments import (KEYS, VARIANTS, parser, predict_all_k, run_full, verify_coverage)
from router import knn_estimate
from test_router import make_data


def test_per_k_estimates_match_reference_with_tied_embeddings(tmp_path):
    data, fit = make_data(Q=100, M=3, dim=4)
    E = np.round(fit(data.models)(data.queries))
    E[:20] = 0  # tie sets must use per-k reference searches, not a max-k prefix
    predictions = predict_all_k(data, E, tmp_path)
    for k in (5, 10, 20, 50, 100, 200, 400):
        for label in ("val", "test"):
            expected = knn_estimate(E[data.train], data.S[data.train], E[getattr(data, label)], k)
            np.testing.assert_allclose(predictions[f"{label}{k}"], expected, atol=1e-14)


def test_full_grid_metrics_sensitivity_resume_and_missing_detection(tmp_path, monkeypatch):
    import learned.full_experiments as full
    data, frozen = make_data(Q=100, M=3, dim=8)
    data = replace(data, new_model="model2")
    values = frozen(data.models)(data.queries).astype(np.float32)

    class Features:
        key = "offline-full-grid"
        positions = {q: i for i, q in enumerate(data.queries)}
        def __init__(self, *args):
            self.values = values
        def embed(self, queries):
            return self.values[[self.positions[q] for q in queries]]

    monkeypatch.setattr(full, "load_data", lambda *a, **kw: data)
    monkeypatch.setattr(full, "unseen_instances", lambda *a: [0])
    monkeypatch.setattr(full, "SentenceFeatures", Features)
    args = vars(parser().parse_args(["--output", str(tmp_path / "full"),
        "--benchmarks", "llmrouterbench", "--splits", "0", "--training-seeds", "0", "1",
        "--probe-seeds", "0", "1", "--probe-budgets", "1", "10", "--n-boot", "10",
        "--representations", "task_type", "regression", "contrastive", "--workers", "1", "--threads", "1"]))
    output = run_full(args)
    coverage = json.loads((output / "coverage.json").read_text())
    assert coverage["complete"] and coverage["main_actual"] == 36
    assert coverage["sensitivity_actual"] == 36 * len(VARIANTS)
    main = pd.read_csv(output / "metrics.csv")
    sens = pd.read_csv(output / "sensitivity.csv")
    assert main.gain_ci_low.notna().all()
    assert main[main.embedding != "task_type"].task_type_recovery.notna().all()
    baseline = main[main.embedding == "task_type"]
    np.testing.assert_allclose(baseline[baseline.train_seed == 0].A, baseline[baseline.train_seed == 1].A)
    with pytest.raises(AssertionError, match="Missing"):
        verify_coverage(main.iloc[1:], sens, args)
    def forbidden(*args):
        raise AssertionError("A resumed completed run must not train again")
    monkeypatch.setattr(full, "make_fit", forbidden)
    run_full(args)
    again = pd.read_csv(output / "metrics.csv")
    pd.testing.assert_frame_equal(main.sort_values(KEYS).reset_index(drop=True),
                                  again.sort_values(KEYS).reset_index(drop=True))
