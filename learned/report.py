"""Create the results README, seed summaries and figures from a verified complete run."""
import argparse
from dataclasses import asdict
import hashlib
import gzip
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .full_experiments import KEYS, verify_coverage
from .features import SentenceFeatures, baselines, fingerprint
from .train import TrainConfig
from preproc.data import load_data, unseen_instances


def markdown_table(frame, decimals=4):
    headings = list(frame.columns)
    lines = ["| " + " | ".join(map(str, headings)) + " |", "|" + "---|" * len(headings)]
    for row in frame.itertuples(index=False, name=None):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(f"{value:.{decimals}f}" if np.isfinite(value) else "—")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def seed_summary(frame, groups):
    """Keep split, training and probe variation distinct instead of treating all rows as iid."""
    rows = []
    for keys, group in frame.groupby(groups, dropna=False):
        row = dict(zip(groups, keys if isinstance(keys, tuple) else (keys,)))
        row["runs"] = len(group)
        for metric in ("A", "gain", "task_type_recovery"):
            if group[metric].notna().sum() == 0:
                continue
            row[f"{metric}_mean"] = group[metric].mean()
            split_means = group.groupby("split_seed")[metric].mean()
            row[f"{metric}_split_sd"] = split_means.std()
            training = group.groupby(["split_seed", "train_seed"])[metric].mean()
            row[f"{metric}_training_sd"] = training.groupby(level=0).std().mean()
            if (group.setting == "unseen").all():
                row[f"{metric}_probe_sd"] = group.groupby(["split_seed", "train_seed"])[metric].std().mean()
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity_summary(main, sensitivity):
    reference = main[KEYS + ["A", "gain"]].rename(columns={"A": "reference_A", "gain": "reference_gain"})
    matched = sensitivity.merge(reference, on=KEYS, how="left", validate="many_to_one")
    assert matched.reference_A.notna().all()
    matched["delta_A"] = matched.A - matched.reference_A
    matched["delta_gain"] = matched.gain - matched.reference_gain
    result = matched.groupby(["benchmark", "variant"]).agg(
        runs=("A", "size"), max_abs_delta_A=("delta_A", lambda v: v.abs().max()),
        p95_abs_delta_A=("delta_A", lambda v: v.abs().quantile(0.95)),
        max_abs_delta_gain=("delta_gain", lambda v: v.abs().max())).reset_index()
    return result, matched


def audit_training(root, protocol):
    """Check every seen/unseen training role against its actual permitted input hash."""
    rows, checked = [], set()
    for benchmark in protocol["benchmarks"]:
        full = load_data(benchmark)
        features = SentenceFeatures(full.queries, protocol["feature_cache"])
        for split in protocol["splits"]:
            for instance in [-1] + list(range(len(unseen_instances(benchmark)))):
                data = load_data(benchmark, split_seed=split, instance=None if instance == -1 else instance)
                pools = [("seen", data.models)]
                if instance != -1:
                    pools.append(("unseen", [m for m in data.models if m != data.new_model]))
                for seed in protocol["training_seeds"]:
                    for objective in ("regression", "contrastive"):
                        if objective not in protocol["representations"]:
                            continue
                        config = TrainConfig(objective=objective, seed=seed)
                        for setting, names in pools:
                            columns = [data.models.index(m) for m in names]
                            profiles = data.S[np.ix_(data.train, columns)].astype(np.float32)
                            signature = hashlib.sha256(profiles.tobytes() + data.train.tobytes()).hexdigest()
                            key = fingerprint({"features": features.key, "models": tuple(names),
                                               "training": signature, "config": asdict(config)})
                            path = root / "cache/checkpoints" / key / "training.json"
                            metadata = json.loads(path.read_text())
                            assert metadata["models"] == names
                            assert metadata["config"] == asdict(config)
                            fit, stop = set(metadata["fit_indices"]), set(metadata["stop_indices"])
                            assert not fit & stop and fit | stop == set(data.train)
                            assert not (fit | stop) & set(np.r_[data.val, data.test])
                            assert setting != "unseen" or data.new_model not in names
                            assert np.isfinite([[h["train_loss"], h["stop_loss"]] for h in metadata["history"]]).all()
                            assert (path.parent / "model.pt").exists() and (path.parent / "embeddings.npy").exists()
                            checked.add(key)
                            rows.append(dict(benchmark=benchmark, split_seed=split, instance=instance,
                                train_seed=seed, objective=objective, setting=setting, checkpoint=key,
                                allowed_models=";".join(names), fit_queries=len(fit), stop_queries=len(stop),
                                best_epoch=metadata["best_epoch"], audit="passed"))
    pd.DataFrame(rows).to_csv(root / "training_audit.csv", index=False)
    stored = {p.parent.name for p in (root / "cache/checkpoints").glob("*/training.json")}
    assert stored == checked, "Unexpected or missing trained checkpoints"
    summary = {"complete": True, "training_roles_checked": len(rows), "unique_checkpoints": len(checked),
               "held_out_model_violations": 0, "external_split_violations": 0}
    (root / "training_audit.json").write_text(json.dumps(summary, indent=2))
    return summary


def figures(main, sensitivity, output):
    names = ["task_type", "handcrafted", "frozen", "combined", "regression", "contrastive"]
    colors = dict(zip(names, plt.get_cmap("tab10").colors))
    paths = []
    for benchmark, data in main.groupby("benchmark"):
        final = data[(data.instance == -1) & (data.setting == "seen")]
        means = final.groupby("embedding").A.mean().reindex(names)
        sd = final.groupby(["embedding", "split_seed"]).A.mean().groupby(level=0).std().reindex(names)
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.bar(names, means, yerr=sd, capsize=3, color=[colors[n] for n in names])
        ax.set(ylabel="Oracle-normalized area A", title=f"{benchmark}: final-pool seen performance\nError bars: SD of split means")
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        path = f"{benchmark}_seen.png"
        fig.savefig(output / path, dpi=160)
        plt.close(fig)
        paths.append(path)

        unseen = data[data.setting == "unseen"]
        instances = sorted(unseen.instance.unique())
        fig, axes = plt.subplots(int(np.ceil(len(instances) / 3)), 3, figsize=(14, 3 * int(np.ceil(len(instances) / 3))),
                                 squeeze=False)
        for ax, instance in zip(axes.flat, instances):
            release = unseen[unseen.instance == instance]
            for name in names:
                means = release[release.embedding == name].groupby("n_probes").A.mean()
                ax.plot(means.index, means, color=colors[name], label=name)
            ax.set(xscale="log", title=release.new_model.iloc[0], xlabel="probes", ylabel="mean A")
            ax.tick_params(labelsize=8)
            ax.title.set_fontsize(9)
        for ax in axes.flat[len(instances):]:
            ax.set_visible(False)
        axes.flat[0].legend(fontsize=7)
        fig.suptitle(f"{benchmark}: every unseen release (means over split/training/probe seeds)")
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        path = f"{benchmark}_unseen_releases.png"
        fig.savefig(output / path, dpi=160)
        plt.close(fig)
        paths.append(path)

        fixed = sensitivity[(sensitivity.benchmark == benchmark) & (sensitivity.instance == -1)
                            & (sensitivity.setting == "seen") & sensitivity.variant.str.match(r"k\d+$")]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for name in names:
            means = fixed[fixed.embedding == name].groupby("k").A.mean()
            ax.plot(means.index, means, marker=".", label=name, color=colors[name])
        ax.set(xscale="log", xlabel="fixed k", ylabel="mean A", title=f"{benchmark}: k sensitivity, final-pool seen")
        ax.legend(fontsize=8)
        fig.tight_layout()
        path = f"{benchmark}_k_sensitivity.png"
        fig.savefig(output / path, dpi=160)
        plt.close(fig)
        paths.append(path)
    return paths


def export_snapshot(root, destination):
    """Publish small, reviewable results, leaving checkpoints and caches gitignored."""
    destination.mkdir(parents=True, exist_ok=True)
    required = ["protocol.json", "coverage.json", "metrics.csv", "summary.csv", "probes_to_target.csv"]
    optional = ["seen_summary.csv", "unseen_summary.csv", "sensitivity_summary.csv",
                "training_audit.csv", "training_audit.json", "validation.json", "execution.json",
                "lambda_outlier_reference_check.json", "block_scaling.csv", "comparison_seen.csv",
                "comparison_unseen.csv"]
    published = required + [n for n in optional if (root / n).exists()]
    for name in published:
        shutil.copy2(root / name, destination / name)
    for path in root.glob("*.png"):
        shutil.copy2(path, destination / path.name)
        published.append(path.name)
    # Include all sensitivity rows without putting a 53 MB plaintext file in Git.
    with (root / "sensitivity.csv").open("rb") as source:
        with (destination / "sensitivity.csv.gz").open("wb") as target:
            with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as compressed:
                shutil.copyfileobj(source, compressed)
    published.append("sensitivity.csv.gz")
    hashes = {name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
              for name in sorted(published)}
    (destination / "sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")


def balanced_comparison(root, balanced, main):
    protocol = json.loads((balanced / "protocol.json").read_text())
    rows = pd.read_csv(balanced / "metrics.csv")
    sens = pd.read_csv(balanced / "sensitivity.csv")
    checked = verify_coverage(rows, sens, protocol)
    assert checked == json.loads((balanced / "coverage.json").read_text())
    original_protocol = json.loads((root / "protocol.json").read_text())
    for key in ("benchmarks", "splits", "training_seeds", "probe_seeds", "probe_budgets", "n_boot"):
        assert protocol[key] == original_protocol[key], f"Unmatched balancing protocol: {key}"
    original = main[main.embedding == "combined"]
    keys = [k for k in KEYS if k != "embedding"]
    paired = original.merge(rows, on=keys, validate="one_to_one", suffixes=("_original", "_balanced"))
    assert len(paired) == len(original) == len(rows)
    joined = pd.concat([original, rows], ignore_index=True)
    seen = seed_summary(joined[(joined.instance == -1) & (joined.setting == "seen")],
                        ["benchmark", "embedding"])
    unseen = seed_summary(joined[joined.setting == "unseen"],
                          ["benchmark", "instance", "new_model", "embedding", "n_probes"])
    seen.to_csv(balanced / "comparison_seen.csv", index=False)
    unseen.to_csv(balanced / "comparison_unseen.csv", index=False)
    scaling = []
    for benchmark in protocol["benchmarks"]:
        for split in protocol["splits"]:
            data = load_data(benchmark, split_seed=split)
            sentences = SentenceFeatures(data.queries, protocol["feature_cache"])
            embeds = baselines(data, sentences)
            h = embeds["handcrafted"](data.queries)[data.train].astype(np.float64)
            e = sentences.values[data.train].astype(np.float64)
            d = e.shape[1]
            b = embeds["combined_balanced"](data.queries)[data.train, d:].astype(np.float64)
            scaling.append(dict(benchmark=benchmark, split_seed=split,
                sentence_mean_norm=np.linalg.norm(e, axis=1).mean(),
                handcrafted_mean_norm=np.linalg.norm(h, axis=1).mean(),
                handcrafted_weight=np.sqrt(np.square(e).sum(1).mean() / np.square(h).sum(1).mean()),
                sentence_mean_squared_norm=np.square(e).sum(1).mean(),
                balanced_handcrafted_mean_squared_norm=np.square(b).sum(1).mean()))
    pd.DataFrame(scaling).to_csv(balanced / "block_scaling.csv", index=False)
    return seen, unseen, checked


def build_report(root, repo, export, balanced=None):
    root, repo, export = map(Path, (root, repo, export))
    coverage = json.loads((root / "coverage.json").read_text())
    assert coverage["complete"] and coverage["missing_main"] == coverage["missing_sensitivity"] == 0
    protocol = json.loads((root / "protocol.json").read_text())
    complete = {"benchmarks": ["llmrouterbench", "routerbench"], "splits": [0, 1, 2],
                "training_seeds": [0, 1, 2], "probe_seeds": [0, 1, 2],
                "probe_budgets": [1, 5, 10, 20, 50, 100, 500],
                "representations": ["task_type", "handcrafted", "frozen", "combined", "regression", "contrastive"]}
    if any(set(protocol.get(key, [])) != set(values) for key, values in complete.items()) or protocol["n_boot"] != 1000:
        raise ValueError("The project-wide README requires the full default protocol; inspect subset CSVs directly")
    main = pd.read_csv(root / "metrics.csv")
    sensitivity = pd.read_csv(root / "sensitivity.csv")
    assert verify_coverage(main, sensitivity, protocol) == coverage
    training_audit = audit_training(root, protocol)
    seen = seed_summary(main[(main.instance == -1) & (main.setting == "seen")], ["benchmark", "embedding"])
    unseen = seed_summary(main[main.setting == "unseen"], ["benchmark", "instance", "new_model", "embedding", "n_probes"])
    sens_summary, _ = sensitivity_summary(main, sensitivity)
    seen.to_csv(root / "seen_summary.csv", index=False)
    unseen.to_csv(root / "unseen_summary.csv", index=False)
    sens_summary.to_csv(root / "sensitivity_summary.csv", index=False)
    paths = figures(main, sensitivity, root)
    checkpoints = list((root / "cache/checkpoints").glob("*/training.json"))
    validation = json.loads((root / "validation.json").read_text()) if (root / "validation.json").exists() else None
    targets = pd.read_csv(root / "probes_to_target.csv")
    reached = targets[targets.status == "reached"]
    lines = ["# Query representation learning: completed experiments", "",
        "The agreed project implementation and the three selected remaining tasks are complete. "
        "The full experiment grid, k/lambda sensitivity checks, and all requested split/training/probe repeats "
        "were executed and checked for missing or duplicate experiment keys.", "",
        "## What is implemented", "",
        "- Data preprocessing, release timelines, shared query splits and nested probe sampling.",
        "- Handcrafted features; frozen sentence embeddings; their concatenation; and an MLP learned "
        "with either profile regression or contrastive learning. Task-type-only is included for RQ1a.",
        "- The shared kNN quality estimator and quality-minus-cost routing rule, validation-based k selection, "
        "single-best and oracle comparisons, cost-quality area A, gain and paired-bootstrap intervals.",
        "- Seen and unseen-model experiments, task-type recovery, and proposal-defined probes-to-target.",
        "- Complete-grid execution with resumable results, cached fits/neighbor estimates, and reference-tested "
        "transition-based evaluation. These execution changes preserve the original routing and metric definitions.", "",
        "## Completed coverage", "",
        "| Item | Completed |", "|---|---|",
        "| Benchmarks | LLMRouterBench and RouterBench |",
        "| Release instances | All 12 primary and 9 secondary instances |",
        f"| Split seeds | {protocol['splits']} |",
        f"| Learned-model training seeds | {protocol['training_seeds']} |",
        f"| Probe seeds | {protocol['probe_seeds']} |",
        f"| Probe budgets | {protocol['probe_budgets']} |",
        "| Representations | All six entries, covering the four proposal types and both learned objectives |",
        f"| Main evaluation rows | {coverage['main_actual']:,} / {coverage['main_expected']:,} |",
        f"| Sensitivity rows | {coverage['sensitivity_actual']:,} / {coverage['sensitivity_expected']:,} |",
        "| Missing or duplicate keys | 0 |",
        f"| Trained checkpoints | {len(checkpoints)} distinct fits |",
        f"| Audited seen/unseen training roles | {training_audit['training_roles_checked']}; zero held-out/split violations |",
        f"| Bootstrap samples | {protocol['n_boot']:,} per main evaluation; 200 for validation k selection |", "",
        "Deterministic baselines have no trainable parameters, so their results are reused across training-seed "
        "labels rather than treating duplicate computations as independent evidence. Learned fits are separate "
        "for each split, training seed and permitted model pool; identical pools reuse the same checkpoint. "
        "Every unseen embedding excludes the newly released model's scores. Probe labels only enter its kNN estimate. "
        "The reserved validation split is used for k selection; embedding early stopping uses training queries only.", "",
        "The primary processed data contains 12,066 queries × 13 models; the secondary contains 36,478 × 11. "
        "Timeline replay changes model availability; it does not simulate timestamped queries, silent API updates "
        "or historical price changes.", "",
        "## Main metrics", "",
        "A is cost-quality area divided by oracle area. Gain is relative area gain over the full-information "
        "single-best baseline; it is not percentage-point accuracy improvement. The cost axis is logarithmic. "
        "In the unseen setting, gain_same_probes also compares against a single-best baseline with the same probe labels.", "",
        "### Final-pool seen results", "",
        "Means over all three splits and three training seeds. Split SD is computed on split means; "
        "training SD is computed within each split and then averaged across splits.", ""]
    for benchmark, table in seen.groupby("benchmark"):
        lines += [f"**{benchmark}**", ""]
        display = table[["embedding", "A_mean", "A_split_sd", "A_training_sd", "gain_mean"]].copy()
        display["gain_mean"] = display.gain_mean.map(lambda v: f"{v:+.2%}")
        display.columns = ["Representation", "Mean A", "Split SD", "Training SD", "Mean gain"]
        lines += [markdown_table(display), ""]
        best = table.loc[table.A_mean.idxmax()]
        lines += [f"Highest observed mean A among the original six entries: **{best.embedding}** "
                  f"({best.A_mean:.4f}). `combined` is the unweighted concatenation; "
                  "this is not a claim that its block scaling is optimal.", "",
                  f"![{benchmark} seen results](@DATA@/{benchmark}_seen.png)", ""]
    lines += ["### Every unseen release at 500 probes", "",
        "Each cell is mean A over split/training/probe seeds. Compare representations within a row: "
        "different release pools have different cost ranges and oracle normalizers. The CSVs also contain "
        "every smaller probe budget, gains, same-probe gains and bootstrap intervals. "
        "**Single-incumbent unseen pools use fixed k=10** (LLMRouterBench instance 0); "
        "other pools use validation-selected k. The same k estimates both incumbent and new-model "
        "quality, capped by the available labels/probe budget.", ""]
    for benchmark, table in unseen[unseen.n_probes == 500].groupby("benchmark"):
        display = table.pivot(index=["instance", "new_model"], columns="embedding", values="A_mean").reset_index()
        lines += [f"**{benchmark}**", "", markdown_table(display), "",
                  f"![{benchmark} unseen release curves](@DATA@/{benchmark}_unseen_releases.png)", ""]
    if balanced is not None:
        balanced = Path(balanced)
        balance_seen, balance_unseen, balance_coverage = balanced_comparison(root, balanced, main)
        lines += ["### Concatenation scaling: original versus balanced", "",
            "`combined` means the original concatenation `[e(q), h(q)]`: a unit-norm sentence "
            "vector and train-standardized handcrafted features. Standardizing individual columns "
            "does not balance these blocks. Theme features can dominate Euclidean distance, favoring "
            "same-theme neighbors. The original tables and figures above refer to this unweighted version.", "",
            "`combined_balanced` uses `[e(q), alpha * h(q)]`, where "
            "`alpha = sqrt(mean_train(||e||²) / mean_train(||h||²))`. This fits one scalar using "
            "training queries only and gives the blocks equal average squared norms on train. "
            "It preserves within-block geometry; it does not force equal norms for each query or "
            "guarantee equal distance contributions for every pair. No test labels select the weight.", "",
            f"Both versions were evaluated on identical main and sensitivity grids. The additional "
            f"balanced run has **{balance_coverage['main_actual']:,} main rows** and "
            f"**{balance_coverage['sensitivity_actual']:,} sensitivity rows**, with zero missing or "
            "duplicate keys. Original results were not overwritten. As with other deterministic "
            "baselines, training-seed labels reuse identical results.", "",
            "Final-pool seen comparison (means over the same three splits and training-seed labels):", "",
            markdown_table(balance_seen[["benchmark", "embedding", "A_mean", "A_split_sd", "gain_mean"]]), "",
            "Balancing slightly lowers mean A on LLMRouterBench and raises it on RouterBench. "
            "These are descriptive differences; neither scaling is established as the best "
            "concatenation, and no significance claim is made.", "",
            "Every unseen release at 500 probes, using the same k-selection/fixed-k=10 policy stated above:", ""]
        for benchmark, table in balance_unseen[balance_unseen.n_probes == 500].groupby("benchmark"):
            display = table.pivot(index=["instance", "new_model"], columns="embedding", values="A_mean").reset_index()
            lines += [f"**{benchmark}**", "", markdown_table(display), ""]
        lines += ["[Block scaling audit](@DATA@/balanced/block_scaling.csv), "
            "[balanced metrics](@DATA@/balanced/metrics.csv), "
            "[balanced protocol](@DATA@/balanced/protocol.json), "
            "[balanced coverage](@DATA@/balanced/coverage.json), "
            "[seen comparison](@DATA@/balanced/comparison_seen.csv), "
            "[all-budget unseen comparison](@DATA@/balanced/comparison_unseen.csv).", ""]
    lines += ["### Seed variability", "",
        "`seen_summary.csv` and `unseen_summary.csv` separate split SD, within-split training SD and "
        "within-split/training probe SD. These measure different sources of variation and are not added "
        "together or presented as independent test-set confidence intervals. Per-run 95% paired test-query "
        "bootstrap intervals are retained in `metrics.csv`.", "",
        "### Task-type recovery (RQ1a)", "",
        "The ratio is A_task / A_learned for the same pool, setting, split and seeds. It can exceed one "
        "when task type performs better than the learned embedding. Final-pool seen means:", ""]
    display = seen[seen.embedding.isin(["regression", "contrastive"])][
        ["benchmark", "embedding", "task_type_recovery_mean"]].copy()
    display.columns = ["Benchmark", "Learned objective", "Mean task-type recovery"]
    lines += [markdown_table(display), "", "### Probes-to-target", "",
        "Following the proposal, target = 90% of the matched seen-model A. Report the smallest **tested** "
        "probe budget meeting that target, separately for every release/split/training/probe combination.", "",
        f"Of {len(targets):,} target measurements, {len(reached):,} reached the target and "
        f"{len(targets)-len(reached):,} did not reach it by the largest tested budget. "
        f"{int((reached.probes_to_target == 1).sum()):,} reached it at one probe. "
        "This does not imply optimal routing from one probe: a high baseline A can make 90% of seen A easy to reach.", "",
        "## k and lambda sensitivity", "",
        "The original main settings were held fixed: k selected from [5, 10, 20, 50, 100, 200] using "
        "validation data and the one-standard-error rule; lambda = 0 plus 500 log-spaced values with "
        "lambda × cost-range spanning 10^-3 to 10^3. A single incumbent uses fixed k=10 because routing "
        "cannot select k in a one-candidate pool.", "",
        "The following one-factor variants were evaluated for **every main evaluation key**, including "
        "every release, probe budget and seed:", "",
        "- Fixed k: 5, 10, 20, 50, 100, 200, 400; retain the main lambda grid.",
        "- Lambda-grid density: 100 and 1,000 points, alongside the 500-point reference.",
        "- Lambda range: 10^-4 to 10^4 (wide) and 10^-2 to 10^2 (narrow), each with 500 points plus zero.", "",
        "Sensitivity rows report point metrics; the 1,000-bootstrap intervals belong to the main evaluations. "
        "Sensitivity results were not used to retune the models or select hyperparameters on test queries.", "",
        "Maximum and 95th-percentile absolute change in A below are paired differences from the matching "
        "main run, not averages of A levels across different release pools.", ""]
    for benchmark, table in sens_summary[sens_summary.variant != "reference"].groupby("benchmark"):
        lines += [f"**{benchmark}**", "",
            markdown_table(table[["variant", "runs", "max_abs_delta_A", "p95_abs_delta_A"]]), "",
            f"![{benchmark} k sensitivity](@DATA@/{benchmark}_k_sensitivity.png)", ""]
    outlier_path = root / "lambda_outlier_reference_check.json"
    if outlier_path.exists():
        checked = json.loads(outlier_path.read_text())
        values = checked["original_harness_results"]
        lines += ["**Interpretation:** k can materially change routing performance. Lambda-grid changes "
            "are usually smaller, but the maxima show that numerical stability cannot be assumed in "
            "every case. For example, the original, unmodified harness reproduced the task-type-only "
            "LLMRouterBench instance-10 unseen result (split 0, 10 probes, probe seed 1, k=200): "
            f"A={values[0]['A']:.4f} with 500 lambda points and A={values[1]['A']:.4f} with 1,000. "
            "A coarse lambda sweep can miss useful cost-quality operating points. We retain the "
            "original main settings and report this sensitivity rather than choosing the test-favorable grid.", "",
            "[Original-harness check for this example](@DATA@/lambda_outlier_reference_check.json)", ""]
    lines += ["## Validation", "",
        (f"`python -m pytest -q preproc michal-harness learned`: **{validation['passed']} passed, "
         f"{validation['skipped']} skipped**." if validation else
         "Run `python -m pytest -q preproc michal-harness learned` to check the implementation."), "",
        "**`michal-harness/router.py` is the reference implementation** for routing, area and "
        "paired-bootstrap metrics. The complete-grid accelerator must agree with it. "
        "Tests compare accelerated curves, areas, bootstrap intervals and validation-selected k to "
        "the reference. An offline integration test uses real `load_data('llmrouterbench', split_seed=0)` "
        "queries, scores and splits with handcrafted features: seen, unseen at 20 and 500 probes, "
        "and the single-incumbent k=10 case. It checks both neighbor/probe predictions and "
        "end-to-end A, gain and interval (absolute tolerance 1e-10). No encoder download is required. "
        "Tests also cover tied neighbors, exclusion of held-out model scores and "
        "external validation/test labels from training, checkpoint reloads, full-grid coverage and resumption. "
        "The coverage check requires every expected experiment key and rejects duplicates or non-finite metrics.", "",
        "## Reproduce and inspect", "",
        "From the repository root, activate the environment described in [setup instructions](@SETUP@), then:", "",
        "```bash", "python -m learned.full_experiments --output results/learned/full --workers 3 --threads 2", "",
        "python -m learned.full_experiments --output results/learned/balanced "
        "--representations combined_balanced --workers 3 --threads 2", "",
        "python -m learned.report --results results/learned/full --balanced results/learned/balanced", "```", "",
        "The full runner resumes completed shards and rejects an output directory with a different protocol. "
        "`coverage.json` verifies exact key coverage, not just total row counts. `protocol.json` stores the "
        "grid, bootstrap count, training configuration and sensitivity definitions. "
        "**The tracked `results_summary/` folder contains the reviewable results**, including "
        "the five requested files, both scaling variants, figures, audits and SHA-256 file manifests. "
        "`summary.csv` uses a two-row pandas column header (read with `header=[0, 1]`); "
        "its SD pools seed labels descriptively. Prefer `seen_summary.csv` and `unseen_summary.csv` "
        "for separate split/train/probe variability. `sensitivity.csv.gz` contains every sensitivity "
        "row, readable directly with pandas. Checkpoints and prediction caches remain gitignored.", "",
        "- [Protocol](@DATA@/protocol.json)",
        "- [Main per-run metrics](@DATA@/metrics.csv)",
        "- [Summary](@DATA@/summary.csv)",
        "- [Seen seed summary](@DATA@/seen_summary.csv)",
        "- [Unseen seed summary](@DATA@/unseen_summary.csv)",
        "- [Probes-to-target](@DATA@/probes_to_target.csv)",
        "- [Sensitivity measurements (gzip)](@DATA@/sensitivity.csv.gz)",
        "- [Sensitivity summary](@DATA@/sensitivity_summary.csv)",
        "- [Coverage verification](@DATA@/coverage.json)", "",
        "- [Training-input audit](@DATA@/training_audit.csv)", "",
        "Raw checkpoints, training histories, cached predictions, explicit probe IDs, and per-run main "
        "cost-quality curves are retained under `results/learned/full/`. The small export contains the "
        "metrics and summary figures rather than duplicating those larger caches.", "",
        "## What is left", "",
        "**No implementation or experiment work remains from the three selected tasks.** All release "
        "instances, the complete three-split/three-training-seed/three-probe-seed grid, and the specified "
        "k/lambda sensitivity grid are complete. No additional representation or routing model is required "
        "for the agreed proposal scope.", "",
        "The remaining project work is the final course-paper narrative: interpret the RQ1/RQ2/RQ1a "
        "comparisons, discuss dataset limitations and sensitivity findings, and assemble the final report "
        "and presentation if required. The old raw-data rebuild test remains skipped because its external "
        "raw inputs are not downloaded; all experiments use the checked-in processed datasets.", ""]
    text = "\n".join(lines)
    snapshot = repo / "results_summary"
    export_snapshot(root, snapshot)
    if balanced is not None:
        export_snapshot(balanced, snapshot / "balanced")
    (repo / "README.md").write_text(text.replace("@DATA@", "results_summary").replace("@SETUP@", "learned/README.md"))
    export.mkdir(parents=True, exist_ok=True)
    export_snapshot(root, export)
    if balanced is not None:
        export_snapshot(balanced, export / "balanced")
    shutil.copy2(repo / "learned/README.md", export / "run-instructions.md")
    (export / "README.md").write_text(text.replace("@DATA@", str(export.resolve()))
                                    .replace("@SETUP@", str(export.resolve() / "run-instructions.md")))
    print("Wrote", repo / "README.md", "and", export / "README.md")
    return seen, unseen, sens_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="results/learned/full")
    parser.add_argument("--export", default="../outputs/learned-embedding-full")
    parser.add_argument("--balanced", default="results/learned/balanced",
                        help="Separate, complete combined_balanced run for the scaling comparison")
    args = parser.parse_args()
    build_report(args.results, Path(__file__).resolve().parents[1], args.export, args.balanced)
