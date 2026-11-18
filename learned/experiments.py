"""Run the proposal's representations through Michal's existing evaluation harness.

Examples (from repo root):
    python -m learned.experiments
    python -m learned.experiments --representations task_type handcrafted frozen combined regression contrastive \
        --instances 11 --probe-seeds 0 1 2
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from preproc.data import BENCHMARKS, load_data, unseen_instances
from .features import DEFAULT_ENCODER, SentenceFeatures, baselines
from .train import TrainConfig, make_fit

# The existing harness directory has a hyphen and is not a Python package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "michal-harness"))
from router import Results  # noqa: E402
import plots  # noqa: E402,F401  (also applies the team's shared plotting style)

REPRESENTATIONS = ("task_type", "handcrafted", "frozen", "combined", "regression", "contrastive")
REPRESENTATION_CHOICES = REPRESENTATIONS + ("combined_balanced",)


def probes_to_target(budgets, areas, seen_area, fraction=0.9):
    """Smallest TESTED probe budget with A_unseen >= fraction * A_seen; None if not reached."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0,1]")
    if len(budgets) != len(areas):
        raise ValueError("budgets and areas must have matching lengths")
    if not np.isfinite(seen_area) or seen_area <= 0:
        return None
    reached = [int(n) for n, a in zip(budgets, areas) if np.isfinite(a) and a >= fraction * seen_area]
    return min(reached) if reached else None


def task_recovery(task_area, learned_area):
    return task_area / learned_area if np.isfinite(learned_area) and learned_area > 0 else float("nan")


def save_metrics(rows, output, target_fraction):
    """Write raw harness metrics and the proposal's two additional measurements."""
    frame = pd.DataFrame(rows)
    context = ["benchmark", "split_seed", "instance", "train_seed", "setting", "n_probes", "probe_seed"]
    frame["task_type_recovery"] = np.nan
    task = frame[frame.embedding == "task_type"].set_index(context).A
    for idx, row in frame[frame.embedding.isin(["regression", "contrastive"])].iterrows():
        key = tuple(row[c] for c in context)
        if key in task.index:
            frame.loc[idx, "task_type_recovery"] = task_recovery(float(task.loc[key]), row.A)
    frame.to_csv(output / "metrics.csv", index=False)

    targets = []
    groups = ["benchmark", "split_seed", "instance", "train_seed", "embedding"]
    for keys, group in frame.groupby(groups, dropna=False):
        seen = group[group.setting == "seen"]
        if seen.empty:
            continue
        for probe_seed, unseen in group[group.setting == "unseen"].groupby("probe_seed"):
            n = probes_to_target(unseen.n_probes, unseen.A, float(seen.iloc[0].A), target_fraction)
            targets.append(dict(zip(groups, keys), probe_seed=probe_seed,
                                target_fraction=target_fraction, seen_A=float(seen.iloc[0].A),
                                probes_to_target=n, status="reached" if n is not None else "not reached"))
    pd.DataFrame(targets, columns=groups + ["probe_seed", "target_fraction", "seen_A",
                                           "probes_to_target", "status"]).to_csv(
                                               output / "probes_to_target.csv", index=False)
    # Descriptive seed spread; the per-run paired bootstrap intervals remain in metrics.csv.
    frame.groupby(["benchmark", "instance", "setting", "embedding", "n_probes"], dropna=False)[
        ["A", "gain", "task_type_recovery"]].agg(["mean", "std"]).to_csv(output / "summary.csv")
    return frame


def plot_comparison(results, path, title):
    fig, ax = plt.subplots()
    for name, result in results.items():
        c = result["curves"]["router"]
        ax.plot(c[:, 0], c[:, 1], label=name)
    reference = next(iter(results.values()))
    for name in ("single_best", "oracle"):
        c = reference["curves"][name]
        ax.plot(c[:, 0], c[:, 1], linestyle="--", label=name.replace("_", " "))
    ax.set(xscale="log", xlabel="mean cost per query (USD)", ylabel="mean quality", title=title)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_probe_areas(frame, path, title):
    fig, ax = plt.subplots()
    for name, group in frame[frame.setting == "unseen"].groupby("embedding", sort=False):
        stats = group.groupby("n_probes").A.agg(["mean", "min", "max"])
        line, = ax.plot(stats.index, stats["mean"], marker=".", label=name)
        ax.fill_between(stats.index, stats["min"], stats["max"], alpha=0.1, color=line.get_color())
        seen = frame[(frame.embedding == name) & (frame.setting == "seen")].A.iloc[0]
        ax.axhline(seen, linestyle=":", linewidth=1, color=line.get_color())
    ax.set(xscale="log", xlabel="number of probes", ylabel="oracle-normalized area A",
           title=title + "\nDotted lines: matched seen-model A; bands: probe-seed range")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(args):
    torch.set_num_threads(args.threads)
    output = Path(args.output) / datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    output.mkdir(parents=True)
    (output / "config.json").write_text(json.dumps(vars(args), indent=2))
    print(f"Results: {output.resolve()}", flush=True)
    rows = []
    for benchmark in args.benchmarks:
        queries = load_data(benchmark, split_seed=args.splits[0]).queries
        sentences = SentenceFeatures(queries, args.cache, args.encoder, device=args.device)
        instances = list(range(len(unseen_instances(benchmark)))) if args.all_instances else (args.instances or [])
        if any(i < 0 or i >= len(unseen_instances(benchmark)) for i in instances):
            raise ValueError(f"Invalid unseen instance for {benchmark}")
        # Final-pool seen comparison first; each instance also gets its own matching seen reference.
        for split in args.splits:
            for instance in [None] + instances:
                data = load_data(benchmark, split_seed=split, instance=instance)
                if instance is not None and any(n > len(data.train) for n in args.probe_budgets):
                    raise ValueError("Probe budget exceeds number of training queries")
                frozen = baselines(data, sentences)
                cache_key = f"baselines-{sentences.key}-split{split}.npz"
                np.savez_compressed(Path(args.cache) / cache_key,
                                    **{name: embed(data.queries) for name, embed in frozen.items()})
                for train_seed in args.training_seeds:
                    label = "final" if instance is None else f"instance{instance}"
                    unit = output / benchmark / f"split{split}" / label / f"train{train_seed}"
                    unit.mkdir(parents=True)
                    out = Results(data, benchmark, root=unit)
                    seen_results = {}
                    row_start = len(rows)
                    for name in args.representations:
                        if name in ("regression", "contrastive"):
                            config = TrainConfig(objective=name, epochs=args.epochs,
                                patience=args.patience, seed=train_seed, hidden_dim=args.hidden_dim,
                                embedding_dim=args.embedding_dim, batch_size=args.batch_size,
                                learning_rate=args.learning_rate, threshold=args.threshold,
                                margin=args.margin, device=args.device)
                            fit = make_fit(data, sentences, config, Path(args.cache) / "checkpoints")
                        else:
                            fit = lambda models, embed=frozen[name]: embed
                        print(f"{benchmark} split={split} {label} seed={train_seed} {name}: seen", flush=True)
                        common = dict(n_boot=args.n_boot, n_lambdas=args.n_lambdas, k=args.k)
                        seen = out.run(name, fit, tune_k=not args.fixed_k, **common)
                        seen_results[name] = seen

                        def record(result, setting, budget=0, probe_seed=-1):
                            ci = result["gain_ci"] or (None, None)
                            rows.append({"benchmark": benchmark, "split_seed": split,
                                "instance": -1 if instance is None else instance,
                                "new_model": data.new_model or "", "train_seed": train_seed,
                                "embedding": name, "setting": setting, "n_probes": budget,
                                "probe_seed": probe_seed, "k": result["k"], "A": result["A"],
                                "A_single_best": result["A_single_best"], "gain": result["gain"],
                                "gain_abs": result["gain_abs"], "gain_same_probes": result["gain_same_probes"],
                                "gain_ci_low": ci[0], "gain_ci_high": ci[1]})
                            print(f"  A={result['A']:.4f}, gain={result['gain']:+.2%}, k={result['k']}", flush=True)

                        record(seen, "seen")
                        save_metrics(rows, output, args.target_fraction)
                        if instance is not None:
                            # With one incumbent, the existing k-selection cost interval has width zero.
                            tune_k = not args.fixed_k and len(data.models) > 2
                            for probe_seed in args.probe_seeds:
                                for n in sorted(set(args.probe_budgets)):
                                    print(f"  unseen n={n}, probe_seed={probe_seed}", flush=True)
                                    result = out.run(name, fit, new_model=data.new_model, n_probes=n,
                                                     seed=probe_seed, tune_k=tune_k, **common)
                                    record(result, "unseen", n, probe_seed)
                                    save_metrics(rows, output, args.target_fraction)
                    plot_comparison(seen_results, unit / "cost_quality_seen.png", f"{benchmark}: {label}, seen")
                    if instance is not None:
                        plot_probe_areas(pd.DataFrame(rows[row_start:]), unit / "area_vs_probes.png",
                                         f"{benchmark}: {data.new_model}")
    print(f"Finished. Metrics and figures: {output.resolve()}", flush=True)
    return output


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--benchmarks", nargs="+", choices=BENCHMARKS, default=["llmrouterbench"])
    p.add_argument("--splits", nargs="+", type=int, choices=(0, 1, 2), default=[0])
    p.add_argument("--training-seeds", nargs="+", type=int, default=[0])
    p.add_argument("--probe-seeds", nargs="+", type=int, default=[0])
    p.add_argument("--representations", nargs="+", choices=REPRESENTATION_CHOICES, default=["frozen", "regression"])
    settings = p.add_mutually_exclusive_group()
    settings.add_argument("--instances", nargs="+", type=int, help="Release instances to evaluate in addition to final-pool seen")
    settings.add_argument("--all-instances", action="store_true")
    p.add_argument("--probe-budgets", nargs="+", type=int, default=[1, 5, 10, 20, 50, 100, 500])
    p.add_argument("--encoder", default=DEFAULT_ENCODER)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--hidden-dim", type=int, default=128)
    p.add_argument("--embedding-dim", type=int, default=64)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--learning-rate", type=float, default=1e-3)
    p.add_argument("--threshold", type=float, default=0.1)
    p.add_argument("--margin", type=float, default=1.0)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--fixed-k", action="store_true", help="Use --k instead of validation-based tuning")
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--n-lambdas", type=int, default=500)
    p.add_argument("--target-fraction", type=float, default=0.9)
    p.add_argument("--device", default="cpu")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--output", default="results/learned/runs")
    p.add_argument("--cache", default="results/learned/cache")
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    if any(n < 1 for n in args.probe_budgets) or not 0 < args.target_fraction <= 1:
        raise SystemExit("Probe budgets must be positive and target fraction must be in (0,1]")
    run(args)
