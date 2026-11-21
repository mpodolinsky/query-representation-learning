"""Every representation of the project on one protocol, through Michal's harness, with our task-type levels.

Representations (the name written to the results):
  task_type_theme  one-hot of the benchmark's own theme (Nikhilesh's `task_type`, the proposal's flat label)
  task_type_L1 / task_type_L2 / task_type_L12   one-hot of our LLM-assigned hierarchical task type
  stats            our 15 z-scored query statistics
  handcrafted      ours: Level 1 + Level 2 one-hots + the statistics (representation (i))
  handcrafted_nik  Nikhilesh's handcrafted features (theme one-hot + 3 raw length statistics, standardized)
  frozen           the frozen sentence encoder (all-MiniLM-L6-v2, L2-normalized), representation (ii)
  combined         frozen + our handcrafted block, balanced (representation (iii))
  regression / contrastive        Nikhilesh's MLP on the sentence vectors, trained with either objective (iv)
  regression_hc / contrastive_hc  the same MLP trained on [sentence vector, our handcrafted block]

Protocol (Nikhilesh's full grid, so the numbers line up with results_summary/): per benchmark and split seed, the
final pool (seen setting) and every unseen release instance of preproc.data.unseen_instances (the pool released
before the event plus the new model): a seen run on the instance pool, then the new model held out with the
probe budgets x probe seeds. k is tuned on the validation split (once per pool and representation); a one-model
pool (the first LLMRouterBench instance) uses fixed k = 10, as in his runs. Learned representations are retrained
per split, pool and training seed; the held-out model's scores never enter training.

Outputs (under --output, default results_compare/):
  metrics.csv                     one row per evaluation, Nikhilesh's columns + recovery and the results folder
  shards/*.json                   one per (benchmark, split, instance, representation, train seed): resumable
  <benchmark>/split<k>/inst<i>/<name>/train<s>/<timestamp>_split<k>/   the harness's own results folders
  embeddings/<benchmark>/split<k>/<name>.npy + labels.npz               for embedding_views.py (final pool, train seed 0)

    python compare_representations.py --encode-only                      # cache the sentence vectors first
    python compare_representations.py --benchmarks llmrouterbench --split-seeds 0 --threads 8
    python compare_representations.py --encoder stub --dry-run           # plan without the encoder
The runner resumes: finished shards are skipped. Several processes may share --output if they cover different
(benchmark, split) pairs (see run_compare_all.sh)."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for p in (REPO, REPO / "michal-harness", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import router  # noqa: E402
from handcrafted import (DEFAULT_K_GRID, HandcraftedEmbedding, fit_concat, fit_handcrafted, fit_stats_only,  # noqa: E402
                         fit_task_type_only, level_labels)
from run_handcrafted import Tuning, labels_for, make_results  # noqa: E402

FROZEN = ["task_type_theme", "task_type_L1", "task_type_L2", "task_type_L12", "stats", "handcrafted",
          "handcrafted_nik", "frozen", "combined"]
LEARNED = ["regression", "contrastive", "regression_hc", "contrastive_hc"]
REPRESENTATIONS = FROZEN + LEARNED
COLUMNS = ["benchmark", "split_seed", "instance", "new_model", "train_seed", "embedding", "setting", "n_probes",
           "probe_seed", "k", "k_tuned", "A", "A_single_best", "gain", "gain_abs", "gain_same_probes",
           "gain_ci_low", "gain_ci_high", "recovery", "results_dir", "run"]


# ---------------------------------------------------------------- sentence features (real, cached, or a stub)

class StubSentenceFeatures:
    """Stand-in for learned.features.SentenceFeatures without the encoder: hashed character trigrams, L2-normalized.
    Same duck-typed interface (values, key, positions, embed). For tests, dry runs and smoke runs only."""

    def __init__(self, queries, dim=32):
        self.queries, self.dim = list(queries), dim
        self.key = f"stub-{dim}-" + hashlib.sha256("\n".join(self.queries).encode()).hexdigest()[:12]
        self.positions = {q: i for i, q in enumerate(self.queries)}
        self.values = self._encode(self.queries)

    def _encode(self, queries):
        X = np.zeros((len(queries), self.dim), dtype=np.float32)
        for i, q in enumerate(queries):
            s = f"  {q.lower()}  "
            for j in range(len(s) - 2):
                h = int(hashlib.blake2b(s[j:j + 3].encode(), digest_size=4).hexdigest(), 16)
                X[i, h % self.dim] += 1.0 if (h >> 16) & 1 else -1.0
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        return X / np.where(norms > 0, norms, 1.0)

    def embed(self, queries):
        queries = list(queries)
        if all(q in self.positions for q in queries):
            return self.values[[self.positions[q] for q in queries]]
        return self._encode(queries)


def sentence_features(queries, args):
    if args.encoder == "stub":
        return StubSentenceFeatures(queries)
    from learned.features import SentenceFeatures
    return SentenceFeatures(queries, args.cache, args.encoder, batch_size=args.batch_size, device=args.device)


class ConcatFeatures:
    """[sentence vector, w * handcrafted block] as the input of the learned MLP (the `_hc` representations).
    w balances the two blocks' total variance on the training queries, like `fit_concat`."""

    def __init__(self, sentences, hand: HandcraftedEmbedding, data):
        self.sentences, self.hand = sentences, hand
        tr = np.asarray(data.train)
        A, B = np.asarray(sentences.values, dtype=np.float64), hand(list(data.queries))
        va, vb = A[tr].var(0).sum(), B[tr].var(0).sum()
        self.weight = math.sqrt(va / vb) if va > 0 and vb > 0 else 1.0
        self.values = np.hstack([A, self.weight * B]).astype(np.float32)
        self.key = hashlib.sha256(f"{sentences.key}|{hand.describe()}|{self.weight:.6g}".encode()).hexdigest()[:20]
        self.positions = dict(sentences.positions)

    def embed(self, queries):
        queries = list(queries)
        if all(q in self.positions for q in queries):
            return self.values[[self.positions[q] for q in queries]]
        return np.hstack([np.asarray(self.sentences.embed(queries), dtype=np.float32),
                          (self.weight * self.hand(queries)).astype(np.float32)])


# ---------------------------------------------------------------- the representations

def build_frozen(names, full, sentences, labels, args, log):
    """name -> fit factory for the frozen representations, built once per split on the full-pool Data (the queries,
    splits and labels do not change between pools)."""
    kw = dict(tokenizer=args.tokenizer, **({"labels": labels} if labels else {}))
    fits, hand = {}, None
    if any(n in names for n in ("handcrafted", "combined", "regression_hc", "contrastive_hc")):
        hand = HandcraftedEmbedding(full, levels=(1, 2), **kw)
    for name in names:
        if name == "task_type_theme":
            fits[name] = fit_task_type_only(full, levels=(0,), **kw)
        elif name.startswith("task_type_L"):
            levels = tuple(int(c) for c in name[len("task_type_L"):])
            fits[name] = fit_task_type_only(full, levels=levels, **kw)
        elif name == "stats":
            fits[name] = fit_stats_only(full, **kw)
        elif name == "handcrafted":
            fits[name] = hand.fit
        elif name == "handcrafted_nik":
            from learned.features import baselines
            embed = baselines(full, sentences)["handcrafted"]
            fits[name] = lambda train_models, embed=embed: embed
        elif name == "frozen":
            fits[name] = lambda train_models: sentences.embed
        elif name == "combined":
            fits[name] = fit_concat(sentences.embed, full, levels=(1, 2), **kw)
    for name, fit in fits.items():
        E = fit(full.models)(full.queries[:2])
        log(f"  {name}: d = {E.shape[1]}" + (f" ({fit(None).describe()})" if hasattr(fit(None), "describe") else ""))
    return fits, hand


def learned_fit(name, data, sentences, hand, train_seed, args):
    """Nikhilesh's `make_fit` for one objective, training seed and (for `_hc`) the concatenated input."""
    from learned.train import TrainConfig, make_fit
    objective = name.replace("_hc", "")
    features = ConcatFeatures(sentences, hand, data) if name.endswith("_hc") else sentences
    config = TrainConfig(objective=objective, seed=train_seed, epochs=args.epochs, patience=args.patience,
                         hidden_dim=args.hidden_dim, embedding_dim=args.embedding_dim, batch_size=args.train_batch_size,
                         learning_rate=args.learning_rate, device=args.device)
    return make_fit(data, features, config, Path(args.cache) / "checkpoints")


# ---------------------------------------------------------------- the loop

def shard_path(root, benchmark, split, instance, name, train_seed):
    return Path(root) / "shards" / f"{benchmark}_split{split}_inst{instance}_{name}_train{train_seed}.json"


def write_metrics(root, rows):
    pd.DataFrame(rows, columns=COLUMNS).to_csv(Path(root) / "metrics.csv", index=False)


def save_embedding(root, benchmark, split, name, fit, data, labels):
    """The final-pool embedding of every query (float32) and, once, the labels embedding_views.py colors by."""
    folder = Path(root) / "embeddings" / benchmark / f"split{split}"
    folder.mkdir(parents=True, exist_ok=True)
    E = np.asarray(fit(data.models)(data.queries), dtype=np.float32)
    np.save(folder / f"{name}.npy", E)
    if not (folder / "labels.npz").exists():
        extra = {}
        for l in (1, 2):  # from the label file, the data's columns or (Level 1) the taxonomy, like the embeddings
            labs = level_labels(data, l, labels, warn=False)
            if labs is not None:
                extra[f"task_level{l}"] = np.asarray(labs, dtype=str)
        np.savez_compressed(folder / "labels.npz", theme=np.asarray(data.theme, dtype=str), train=data.train, val=data.val,
                            test=data.test, models=np.asarray(data.models, dtype=str), **extra)


def run_unit(args, root, benchmark, split, instance, data, name, train_seed, fit, log, labels):
    """One (pool, representation, training seed): the seen run, then (instances only) the unseen loop. Returns rows."""
    unit_root = Path(root) / benchmark / f"split{split}" / f"inst{instance}" / name / f"train{train_seed}"
    out = make_results(data, benchmark, unit_root)
    tuning = Tuning(out, args.k_grid)
    common = dict(n_lambdas=args.n_lambdas)
    rows = []

    def row(res, setting, n_probes=0, probe_seed=-1, k_tuned=True):
        ci = res["gain_ci"] or (None, None)
        last = out.rows[-1]
        return {"benchmark": benchmark, "split_seed": split, "instance": instance, "new_model": data.new_model or "",
                "train_seed": train_seed, "embedding": name, "setting": setting, "n_probes": n_probes,
                "probe_seed": probe_seed, "k": int(res["k"]), "k_tuned": k_tuned, "A": res["A"],
                "A_single_best": res["A_single_best"], "gain": res["gain"], "gain_abs": res["gain_abs"],
                "gain_same_probes": res["gain_same_probes"], "gain_ci_low": ci[0], "gain_ci_high": ci[1],
                "recovery": last["recovery"] if last["recovery"] != "" else None,
                "results_dir": str(out.dir.relative_to(root)), "run": last["run"]}

    res, info = tuning.run_seen(name, fit, n_boot=args.n_boot, **common)
    rows.append(row(res, "seen"))
    log(f"  seen   {name:16s} inst={instance:>2} train={train_seed} gain={res['gain']:+.4f} A={res['A']:.4f} k={res['k']}")
    if instance != -1:
        pool = [m for m in data.models if m != data.new_model]
        if len(pool) < 2:  # a single incumbent: no cost range to tune k on (Nikhilesh's rule: fixed k = 10)
            k, info, tuned = 10, {"best_k_at_edge": False, "best_k": ""}, False
        else:
            k, info = tuning.select_k_once(fit, data.new_model, args.n_lambdas)
            tuned = True
        for probe_seed in range(args.probe_seeds):
            for n in args.probe_budgets:
                res = tuning.run_unseen(name, fit, data.new_model, n, probe_seed, k, info, n_boot=args.n_boot_unseen, **common)
                rows.append(row(res, "unseen", n, probe_seed, tuned))
        log(f"  unseen {name:16s} inst={instance:>2} train={train_seed} new={data.new_model} k={k}"
            f"{'' if tuned else ' (fixed)'} budgets={args.probe_budgets} x {args.probe_seeds} seeds, last gain={res['gain']:+.4f}")
    return rows


def run_split(args, root, benchmark, split, log):
    from preproc.data import load_data, unseen_instances
    full = load_data(benchmark, split_seed=split)
    labels = labels_for(args.level_labels, benchmark, full)
    sentences = sentence_features(full.queries, args)
    log(f"{benchmark} split {split}: {len(full.queries)} queries, {len(full.models)} models, sentence features "
        f"{sentences.values.shape} ({sentences.key[:12]}), labels {'yes' if labels else 'NONE'}")
    frozen_names = [n for n in args.representations if n in FROZEN]
    learned_names = [n for n in args.representations if n in LEARNED]
    fits, hand = build_frozen(frozen_names, full, sentences, labels, args, log)
    if any(n.endswith("_hc") for n in learned_names) and hand is None:
        hand = HandcraftedEmbedding(full, levels=(1, 2), tokenizer=args.tokenizer, **({"labels": labels} if labels else {}))
    instances = [-1] + (list(range(len(unseen_instances(benchmark)))) if args.instances is None else list(args.instances))
    if args.seen_only:
        instances = [-1]
    rows = []
    for instance in instances:
        data = full if instance == -1 else load_data(benchmark, split_seed=split, instance=instance)
        for name in frozen_names + learned_names:
            seeds = args.training_seeds if name in LEARNED else [0]
            for train_seed in seeds:
                shard = shard_path(root, benchmark, split, instance, name, train_seed)
                if shard.exists():
                    rows.extend(json.loads(shard.read_text())["rows"])
                    continue
                if args.dry_run:
                    continue
                fit = fits[name] if name in FROZEN else learned_fit(name, data, sentences, hand, train_seed, args)
                t0 = time.monotonic()
                unit_rows = run_unit(args, root, benchmark, split, instance, data, name, train_seed, fit, log, labels)
                if instance == -1 and train_seed == 0 and not args.no_embeddings:
                    save_embedding(root, benchmark, split, name, fit, data, labels)
                shard.parent.mkdir(parents=True, exist_ok=True)
                shard.write_text(json.dumps({"rows": unit_rows, "seconds": time.monotonic() - t0}, indent=1))
                rows.extend(unit_rows)
                write_metrics(root, _all_rows(root))
    return rows


def _all_rows(root):
    rows = []
    for shard in sorted((Path(root) / "shards").glob("*.json")):
        rows.extend(json.loads(shard.read_text())["rows"])
    return rows


def count_plan(args, benchmark):
    from preproc.data import unseen_instances
    n_inst = 1 if args.seen_only else 1 + (len(unseen_instances(benchmark)) if args.instances is None else len(args.instances))
    n_frozen = sum(n in FROZEN for n in args.representations)
    n_learned = sum(n in LEARNED for n in args.representations) * len(args.training_seeds)
    seen = n_inst * (n_frozen + n_learned)
    unseen = (n_inst - 1) * (n_frozen + n_learned) * len(args.probe_budgets) * args.probe_seeds
    return seen, unseen


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--benchmarks", nargs="+", default=["llmrouterbench", "routerbench"])
    p.add_argument("--split-seeds", nargs="+", type=int, default=[0, 1, 2])
    p.add_argument("--representations", nargs="+", default=REPRESENTATIONS, choices=REPRESENTATIONS)
    p.add_argument("--instances", nargs="*", type=int, default=None, help="unseen instances to run (default: all)")
    p.add_argument("--seen-only", action="store_true", help="final pool only, no release instances")
    p.add_argument("--probe-budgets", nargs="+", type=int, default=[1, 5, 10, 20, 50, 100, 500])
    p.add_argument("--probe-seeds", type=int, default=3, help="probe draws per budget (seeds 0..n-1)")
    p.add_argument("--training-seeds", nargs="+", type=int, default=[0, 1, 2], help="for the learned representations")
    p.add_argument("--k-grid", nargs="+", type=int, default=list(DEFAULT_K_GRID))
    p.add_argument("--n-lambdas", type=int, default=500)
    p.add_argument("--n-boot", type=int, default=1000, help="bootstrap resamples of the seen runs")
    p.add_argument("--n-boot-unseen", type=int, default=200, help="bootstrap resamples of the unseen runs (0 skips)")
    p.add_argument("--level-labels", default="auto", help="as in run_handcrafted.py (auto: preproc/data/<b>/task_labels.parquet)")
    p.add_argument("--tokenizer", default="tiktoken:cl100k_base")
    p.add_argument("--encoder", default="sentence-transformers/all-MiniLM-L6-v2", help="sentence encoder, or 'stub'")
    p.add_argument("--cache", default=str(REPO / "results" / "learned" / "cache"), help="sentence vectors + checkpoints")
    p.add_argument("--device", default="cpu")
    p.add_argument("--batch-size", type=int, default=64, help="encoder batch size")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--hidden-dim", type=int, default=128)
    p.add_argument("--embedding-dim", type=int, default=64)
    p.add_argument("--train-batch-size", type=int, default=128)
    p.add_argument("--learning-rate", type=float, default=1e-3)
    p.add_argument("--output", default=str(REPO / "results_compare"))
    p.add_argument("--no-embeddings", action="store_true", help="do not export the final-pool embeddings")
    p.add_argument("--encode-only", action="store_true", help="only compute and cache the sentence vectors")
    p.add_argument("--dry-run", action="store_true", help="print the plan and the shard status, run nothing")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    log = lambda *a: print(*a, flush=True)
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    if any(n in LEARNED for n in args.representations) or args.encode_only or args.encoder != "stub":
        try:
            import torch
            torch.set_num_threads(args.threads)
        except ImportError:
            if any(n in LEARNED for n in args.representations) or args.encoder != "stub":
                raise SystemExit("torch is not installed: `pip install -r learned/requirements.txt`, or use --encoder stub "
                                 "with frozen representations only")
    protocol = {k: v for k, v in vars(args).items() if k not in ("dry_run", "encode_only", "threads", "device")}
    manifest = root / "protocol.json"
    if manifest.exists() and not args.dry_run:
        old = json.loads(manifest.read_text())
        differing = {k for k in old if k in protocol and old[k] != protocol[k] and k not in
                     ("benchmarks", "split_seeds", "representations", "instances", "training_seeds", "seen_only", "output", "cache", "batch_size")}
        if differing:
            raise SystemExit(f"{manifest} belongs to another protocol (differs in {sorted(differing)}); use another --output")
    elif not args.dry_run:
        manifest.write_text(json.dumps(protocol, indent=2))
    if args.encode_only:
        from preproc.data import load_data
        for benchmark in args.benchmarks:
            s = sentence_features(load_data(benchmark, split_seed=args.split_seeds[0]).queries, args)
            log(f"{benchmark}: sentence vectors {s.values.shape} cached under {args.cache}")
        return
    for benchmark in args.benchmarks:
        seen, unseen = count_plan(args, benchmark)
        log(f"{benchmark}: {seen} seen + {unseen} unseen evaluations per split, representations {args.representations}")
        for split in args.split_seeds:
            if args.dry_run:
                from preproc.data import unseen_instances
                n_inst = 1 if args.seen_only else 1 + len(unseen_instances(benchmark))
                done = len(list((root / "shards").glob(f"{benchmark}_split{split}_*.json")))
                log(f"  split {split}: {done} shards done of {n_inst * (sum(n in FROZEN for n in args.representations) + sum(n in LEARNED for n in args.representations) * len(args.training_seeds))}")
                continue
            run_split(args, root, benchmark, split, log)
    if not args.dry_run:
        write_metrics(root, _all_rows(root))
        log(f"metrics: {root / 'metrics.csv'}")


if __name__ == "__main__":
    main()
