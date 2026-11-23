"""The checked-in review bundle must support the reported grid and derived numbers."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learned.experiments import save_metrics
from learned.full_experiments import verify_coverage


@pytest.mark.parametrize("variant", ["", "balanced"])
def test_published_results_are_complete_and_reproduce_summaries(tmp_path, variant):
    root = Path(__file__).resolve().parents[1] / "results_summary" / variant
    protocol = json.loads((root / "protocol.json").read_text())
    manifest = json.loads((root / "sha256.json").read_text())
    for name, expected in manifest.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    main = pd.read_csv(root / "metrics.csv")
    sensitivity = pd.read_csv(root / "sensitivity.csv.gz")
    assert verify_coverage(main, sensitivity, protocol) == json.loads((root / "coverage.json").read_text())
    save_metrics(main.to_dict("records"), tmp_path, 0.9)
    pd.testing.assert_frame_equal(pd.read_csv(tmp_path / "probes_to_target.csv"),
                                  pd.read_csv(root / "probes_to_target.csv"))
    # pandas writes the summary's index names on a third header line.
    pd.testing.assert_frame_equal(pd.read_csv(tmp_path / "summary.csv", header=[0, 1], index_col=list(range(5))),
                                  pd.read_csv(root / "summary.csv", header=[0, 1], index_col=list(range(5))))
    if variant:
        scaling = pd.read_csv(root / "block_scaling.csv")
        np.testing.assert_allclose(scaling.sentence_mean_squared_norm,
                                   scaling.balanced_handcrafted_mean_squared_norm, rtol=1e-6)
