"""Reported seed spreads must preserve the experiment's split/train/probe hierarchy."""
import numpy as np
import pandas as pd
import pytest

from learned.report import markdown_table, seed_summary, sensitivity_summary


def test_seed_variability_sources_are_not_pooled():
    rows = []
    for split in range(3):
        for train in range(3):
            for probe in range(3):
                a = 0.5 + 0.01 * split + 0.001 * train + 0.0001 * probe
                rows.append(dict(benchmark="b", embedding="regression", setting="unseen",
                                 split_seed=split, train_seed=train, probe_seed=probe,
                                 A=a, gain=2*a - 1, task_type_recovery=0.9))
    row = seed_summary(pd.DataFrame(rows), ["benchmark", "embedding"]).iloc[0]
    assert row.A_split_sd == pytest.approx(0.01)
    assert row.A_training_sd == pytest.approx(0.001)
    assert row.A_probe_sd == pytest.approx(0.0001)
    assert row.runs == 27


def test_sensitivity_is_paired_with_its_own_reference():
    keys = dict(benchmark="b", split_seed=0, instance=0, train_seed=0, embedding="frozen",
                setting="unseen", n_probes=10, probe_seed=0)
    main = pd.DataFrame([dict(keys, A=0.7, gain=0.1)])
    sens = pd.DataFrame([dict(keys, variant="reference", A=0.7, gain=0.1),
                         dict(keys, variant="k5", A=0.72, gain=0.12)])
    summary, _ = sensitivity_summary(main, sens)
    row = summary[summary.variant == "k5"].iloc[0]
    assert row.max_abs_delta_A == pytest.approx(0.02)
    assert row.runs == 1
    assert "—" in markdown_table(pd.DataFrame({"A": [np.nan]}))
