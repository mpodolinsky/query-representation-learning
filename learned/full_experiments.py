"""Complete release/split/seed grid and one-factor k/lambda sensitivity, with resumable shards.

python -m learned.full_experiments --output results/learned/full --workers 3
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import time

import numpy as np
import pandas as pd
import torch
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from preproc.data import load_data, unseen_instances, sample_probes
from .features import SentenceFeatures, baselines, fingerprint
from .train import TrainConfig, make_fit
from .evaluation import MetricContext, Policy, lambda_grid, select_k
from .experiments import REPRESENTATIONS, save_metrics

K_GRID = (5, 10, 20, 50, 100, 200)
SENSITIVITY_K = K_GRID + (400,)
VARIANTS = ["reference"] + [f"k{k}" for k in SENSITIVITY_K] + [
    "lambda_points100", "lambda_points1000", "lambda_range_wide", "lambda_range_narrow"]
KEYS = ["benchmark", "split_seed", "instance", "train_seed", "embedding", "setting", "n_probes", "probe_seed"]


def atomic_json(value, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2))
    temporary.replace(path)


def predict_all_k(data, embeddings, cache, ks=SENSITIVITY_K):
    """Exact per-k neighbor searches (important: ties need not have consistent prefixes).

    Compute columns together, but the caller selects only incumbent columns for unseen
    routing/tuning; the new model's estimate is constructed from probe labels separately.
    """
    signature = hashlib.sha256(embeddings.tobytes() + data.train.tobytes()
                               + data.S[data.train].tobytes()).hexdigest()[:24]
    path = Path(cache) / f"neighbors-{signature}.npz"
    if path.exists():
        with np.load(path) as z:
            return {name: z[name] for name in z.files}
    outputs = {}
    query_ids = np.r_[data.val, data.test]
    train_scores = data.S[data.train]
    for k in ks:
        nn = NearestNeighbors(n_neighbors=min(k, len(data.train))).fit(embeddings[data.train])
        neighbors = nn.kneighbors(embeddings[query_ids], return_distance=False)
        scores = sum(train_scores[neighbors[:, j]] for j in range(neighbors.shape[1])) / neighbors.shape[1]
        outputs[f"val{k}"] = scores[:len(data.val)]
        outputs[f"test{k}"] = scores[len(data.val):]
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **outputs)
    return outputs


def probe_predictions(data, embeddings, new, budget, seed, ks=SENSITIVITY_K):
    ids = sample_probes(data.train, budget, seed)
    scores = data.S[ids, new]
    result, computed = {}, {}
    for k in ks:
        effective = min(k, budget)
        if effective not in computed:
            if effective == budget:
                computed[effective] = np.full(len(data.test), scores.mean())
            else:
                nn = NearestNeighbors(n_neighbors=effective).fit(embeddings[ids])
                neighbors = nn.kneighbors(embeddings[data.test], return_distance=False)
                computed[effective] = sum(scores[neighbors[:, j]] for j in range(effective)) / effective
        result[k] = computed[effective]
    return result, float(scores.mean()), ids


def sensitivity_settings(tuned_k):
    return [("reference", tuned_k, 500, -3, 3)] + [
        (f"k{k}", k, 500, -3, 3) for k in SENSITIVITY_K] + [
        ("lambda_points100", tuned_k, 100, -3, 3),
        ("lambda_points1000", tuned_k, 1000, -3, 3),
        ("lambda_range_wide", tuned_k, 500, -4, 4),
        ("lambda_range_narrow", tuned_k, 500, -2, 2)]


def run_unit(args, benchmark, split):
    """One independent benchmark/split worker; no fitting is shared across processes."""
    torch.set_num_threads(args["threads"])
    root = Path(args["output"])
    unit = root / benchmark / f"split{split}"
    unit.mkdir(parents=True, exist_ok=True)
    full = load_data(benchmark, split_seed=split)
    sentences = SentenceFeatures(full.queries, args["feature_cache"])
    frozen = baselines(full, sentences)
    instances = [-1] + list(range(len(unseen_instances(benchmark))))
    main_rows, sensitivity_rows = [], []
    start = time.monotonic()
    with threadpool_limits(limits=args["threads"]):
        for instance in instances:
            data = full if instance == -1 else load_data(benchmark, split_seed=split, instance=instance)
            cols = [full.models.index(m) for m in data.models]
            new = None if instance == -1 else data.models.index(data.new_model)
            old = [i for i in range(len(data.models)) if i != new]
            truth = data.S[data.test]
            means = data.S[data.train].mean(axis=0)
            context = MetricContext(truth, data.cost, means)
            for train_seed in args["training_seeds"]:
                for name in args["representations"]:
                    shard = unit / f"instance{instance}" / f"train{train_seed}" / f"{name}.json"
                    if shard.exists():
                        stored = json.loads(shard.read_text())
                        main_rows.extend(stored["main"])
                        sensitivity_rows.extend(stored["sensitivity"])
                        continue
                    deterministic = name not in ("regression", "contrastive")
                    source = unit / f"instance{instance}" / f"train{args['training_seeds'][0]}" / f"{name}.json"
                    if deterministic and train_seed != args["training_seeds"][0] and source.exists():
                        stored = json.loads(source.read_text())
                        for row in stored["main"] + stored["sensitivity"]:
                            row["train_seed"] = train_seed
                        stored["deterministic_reuse"] = True
                        atomic_json(stored, shard)
                        main_rows.extend(stored["main"])
                        sensitivity_rows.extend(stored["sensitivity"])
                        continue
                    print(f"{benchmark} split={split} instance={instance} train={train_seed} {name}", flush=True)
                    if deterministic:
                        E_seen = E_unseen = frozen[name](full.queries)
                    else:
                        config = TrainConfig(objective=name, seed=train_seed)
                        fit = make_fit(data, sentences, config, root / "cache/checkpoints")
                        E_seen = fit(data.models)(data.queries)
                        E_unseen = None if new is None else fit([data.models[i] for i in old])(data.queries)
                    predictions_seen = predict_all_k(full, E_seen, root / "cache/predictions")
                    if new is not None:
                        predictions_unseen = (predictions_seen if deterministic else
                            predict_all_k(full, E_unseen, root / "cache/predictions"))
                    local_main, local_sens, saved_curves, probes = [], [], {}, {}
                    settings = [("seen", 0, -1)]
                    if new is not None:
                        settings += [("unseen", n, s) for s in args["probe_seeds"] for n in args["probe_budgets"]]
                    selected = {}
                    for setting, budget, probe_seed in settings:
                        prediction = predictions_seen if setting == "seen" else predictions_unseen
                        pool = list(range(len(data.models))) if setting == "seen" else old
                        if setting not in selected:
                            val = {k: prediction[f"val{k}"][:, np.asarray(cols)[pool]] for k in K_GRID}
                            selected[setting] = select_k(val, data.S[data.val][:, pool], data.cost[pool], K_GRID)
                        tuned = selected[setting]
                        estimates = {k: prediction[f"test{k}"][:, cols].copy() for k in SENSITIVITY_K}
                        probe_mean = None
                        if setting == "unseen":
                            predicted_new, new_mean, ids = probe_predictions(data, E_unseen, new, budget, probe_seed)
                            for k in SENSITIVITY_K:
                                estimates[k][:, new] = predicted_new[k]
                            probe_mean = means.copy()
                            probe_mean[new] = new_mean
                            probes[f"seed{probe_seed}_n{budget}"] = ids
                        policies = {k: Policy(estimates[k], truth, data.cost) for k in SENSITIVITY_K}
                        metadata = dict(benchmark=benchmark, split_seed=split, instance=instance,
                            new_model=data.new_model or "", train_seed=train_seed, embedding=name,
                            setting=setting, n_probes=budget, probe_seed=probe_seed)
                        metrics, points = context.evaluate(policies[tuned], lambda_grid(data.cost),
                            n_boot=args["n_boot"], seed=max(0, probe_seed), probe_mean=probe_mean)
                        row = dict(metadata, k=tuned, **metrics)
                        local_main.append(row)
                        tag = f"{setting}_n{budget}_seed{probe_seed}"
                        saved_curves[tag] = points
                        for variant, k, num, low, high in sensitivity_settings(tuned):
                            if variant == "reference" or (k == tuned and num == 500 and low == -3 and high == 3):
                                result = {key: value for key, value in metrics.items() if not key.startswith("gain_ci")}
                            else:
                                grid = lambda_grid(data.cost, num, low, high)
                                result, _ = context.evaluate(policies[k], grid, probe_mean=probe_mean)
                                result.pop("gain_ci_low")
                                result.pop("gain_ci_high")
                            local_sens.append(dict(metadata, variant=variant, k=k, tuned_k=tuned,
                                                   n_lambdas=num, lambda_low=low, lambda_high=high, **result))
                    # Curves and explicit probe IDs make the individual runs inspectable.
                    shard.parent.mkdir(parents=True, exist_ok=True)
                    np.savez_compressed(shard.with_suffix(".npz"), **saved_curves, **probes)
                    stored = {"main": local_main, "sensitivity": local_sens, "deterministic_reuse": False}
                    atomic_json(stored, shard)
                    main_rows.extend(local_main)
                    sensitivity_rows.extend(local_sens)
                    print(f"  saved {len(main_rows)} main / {len(sensitivity_rows)} sensitivity rows; "
                          f"{(time.monotonic()-start)/60:.1f} minutes", flush=True)
            pd.DataFrame(main_rows).to_csv(unit / "metrics.csv", index=False)
            pd.DataFrame(sensitivity_rows).to_csv(unit / "sensitivity.csv", index=False)
    return benchmark, split


def expected_keys(args):
    expected = set()
    for b in args["benchmarks"]:
        for split in args["splits"]:
            for instance in [-1] + list(range(len(unseen_instances(b)))):
                settings = [("seen", 0, -1)]
                if instance != -1:
                    settings += [("unseen", n, s) for s in args["probe_seeds"] for n in args["probe_budgets"]]
                for train in args["training_seeds"]:
                    for name in args["representations"]:
                        for setting, budget, probe in settings:
                            expected.add((b, split, instance, train, name, setting, budget, probe))
    return expected


def verify_coverage(main, sensitivity, args):
    expected = expected_keys(args)
    actual = set(main[KEYS].itertuples(index=False, name=None))
    assert len(actual) == len(main), "Duplicate main experiment keys"
    assert actual == expected, f"Missing={len(expected-actual)}, unexpected={len(actual-expected)} main runs"
    observed = set(sensitivity[KEYS + ["variant"]].itertuples(index=False, name=None))
    wanted = {key + (variant,) for key in expected for variant in VARIANTS}
    assert len(observed) == len(sensitivity), "Duplicate sensitivity experiment keys"
    assert observed == wanted, f"Missing={len(wanted-observed)} sensitivity runs"
    for frame in (main, sensitivity):
        assert np.isfinite(frame[["A", "A_single_best", "gain", "gain_abs"]]).all().all()
        assert frame[frame.setting == "unseen"].gain_same_probes.notna().all()
    if args["n_boot"]:
        assert np.isfinite(main[["gain_ci_low", "gain_ci_high"]]).all().all()
    return {"complete": True, "main_expected": len(expected), "main_actual": len(main),
            "sensitivity_expected": len(wanted), "sensitivity_actual": len(sensitivity),
            "missing_main": 0, "missing_sensitivity": 0}


def run_full(args):
    root = Path(args["output"])
    root.mkdir(parents=True, exist_ok=True)
    protocol = {key: value for key, value in args.items() if key not in ("workers", "threads")}
    protocol.update(k_grid=list(K_GRID), sensitivity_k=list(SENSITIVITY_K), variants=VARIANTS,
                    training=asdict(TrainConfig()), validation_bootstrap=200)
    manifest = root / "protocol.json"
    if manifest.exists():
        if json.loads(manifest.read_text()) != protocol:
            raise ValueError("Output directory belongs to a different experiment protocol")
    else:
        atomic_json(protocol, manifest)
        git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        atomic_json({"git_commit_at_start": git, "threads_per_worker": args["threads"],
                     "workers": args["workers"], "started": time.time()}, root / "execution.json")
    jobs = [(b, split) for b in args["benchmarks"] for split in args["splits"]]
    if args["workers"] == 1:
        for benchmark, split in jobs:
            run_unit(args, benchmark, split)
    else:
        with ProcessPoolExecutor(max_workers=args["workers"], mp_context=multiprocessing.get_context("spawn")) as executor:
            futures = [executor.submit(run_unit, args, b, split) for b, split in jobs]
            for future in as_completed(futures):
                print("Completed unit:", future.result(), flush=True)
    main = pd.concat([pd.read_csv(root / b / f"split{s}/metrics.csv", keep_default_na=False)
                      for b, s in jobs], ignore_index=True)
    sens = pd.concat([pd.read_csv(root / b / f"split{s}/sensitivity.csv", keep_default_na=False)
                      for b, s in jobs], ignore_index=True)
    # Empty CI / same-probe fields are intentional only for unbootstrapped / seen rows.
    for frame in (main, sens):
        for column in ("gain_ci_low", "gain_ci_high", "gain_same_probes"):
            if column in frame:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
    coverage = verify_coverage(main, sens, args)
    # Reuse the proposal's task-type recovery and probes-to-target implementation.
    main = save_metrics(main.to_dict("records"), root, 0.9)
    sens.to_csv(root / "sensitivity.csv", index=False)
    atomic_json(coverage, root / "coverage.json")
    print(json.dumps(coverage, indent=2), flush=True)
    return root


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default="results/learned/full")
    p.add_argument("--feature-cache", default="results/learned/cache")
    p.add_argument("--benchmarks", nargs="+", default=["llmrouterbench", "routerbench"])
    p.add_argument("--splits", nargs="+", type=int, default=[0, 1, 2])
    p.add_argument("--training-seeds", nargs="+", type=int, default=[0, 1, 2])
    p.add_argument("--probe-seeds", nargs="+", type=int, default=[0, 1, 2])
    p.add_argument("--representations", nargs="+", choices=REPRESENTATIONS, default=list(REPRESENTATIONS))
    p.add_argument("--probe-budgets", nargs="+", type=int, default=[1, 5, 10, 20, 50, 100, 500])
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--threads", type=int, default=2)
    return p


if __name__ == "__main__":
    run_full(vars(parser().parse_args()))
