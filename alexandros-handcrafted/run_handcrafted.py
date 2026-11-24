"""Run the handcrafted-feature variants through Michal's harness, mirroring the README loop.

For each benchmark and split seed: load the data (Arman's loader), attach the task labels, build the frozen
embeddings once, run the seen-model setting for every variant with tune_k=True, then the unseen-model setting for
the `--unseen-variants` (default: `handcrafted` only) and every release event (each model in release order as the
new model) over a grid of probe budgets and several probe seeds.
Results land in results/<timestamp>_split<seed>/results.csv (the harness's format) plus k_tuning.csv (the tuned k
of every run, its grid, and whether it sits at the edge of the grid); analyze_handcrafted.py reads both.

    python run_handcrafted.py --dry-run                                   # print the plan, run nothing
    python run_handcrafted.py --benchmarks llmrouterbench --split-seeds 0  # the main split first
    python run_handcrafted.py                                             # everything (both benchmarks, 3 splits)

k tuning. The harness's `select_k` depends only on the embedding, the pool and the validation split, not on the
probe budget or the probe seed, so in the unseen loop it is run once per (variant, held-out model) and the chosen
k is passed to every budget x seed run of that pair (`tune_k=False, k=k` in results.csv, "once per held-out model"
in k_tuning.csv). The numbers are identical to tuning inside every run; the cost is 1/40th (HARNESS_NOTES.md, 6).

The loader is resolved in this order: --loader, $QRL_LOADER, then a few default names (see find_load_data).
A missing loader gives a clear error, not a traceback."""
from __future__ import annotations

import argparse
import contextlib
import csv
import dataclasses
import importlib
import importlib.util
import io
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "michal-harness"))
sys.path.insert(0, str(HERE))

import router  # noqa: E402
from router import Results  # noqa: E402
from handcrafted import (DEFAULT_K_GRID, DEFAULT_LEVEL_COLUMNS, DEFAULT_UNSEEN_VARIANTS, DEFAULT_VARIANTS,  # noqa: E402
                         VARIANTS, MissingLevels, level_labels)
import task_taxonomy  # noqa: E402

# Where Arman's loader may live, tried in order: "module:function". A path to a .py file also works.
DEFAULT_LOADERS = ("preproc.data:load_data", "data:load_data", "arman_data:load_data", "arman-data/data.py:load_data",
                   "arman-data/load_data.py:load_data", "load_data:load_data", "loader:load_data")
LABELS_DIR = REPO / "preproc" / "data"          # <benchmark>/task_labels.parquet, written by labeling/merge_labels.py


def find_load_data(spec: str | None = None):
    """Return Arman's `load_data(benchmark, split_seed=0) -> Data`. Raises SystemExit with a readable message."""
    specs = [spec] if spec else ([os.environ["QRL_LOADER"]] if os.environ.get("QRL_LOADER") else list(DEFAULT_LOADERS))
    tried = []
    for s in specs:
        mod_spec, _, func = s.rpartition(":")
        if not mod_spec:
            mod_spec, func = s, "load_data"
        try:
            if mod_spec.endswith(".py"):
                path = (REPO / mod_spec) if not Path(mod_spec).is_absolute() else Path(mod_spec)
                if not path.exists():
                    tried.append(f"{s}: no file {path}")
                    continue
                m = importlib.util.module_from_spec(ms := importlib.util.spec_from_file_location(path.stem, path))
                ms.loader.exec_module(m)
            else:
                for extra in [REPO, *sorted(REPO.glob("*arman*"))]:
                    if str(extra) not in sys.path:
                        sys.path.append(str(extra))
                m = importlib.import_module(mod_spec)
            fn = getattr(m, func, None)
            if fn is None:
                tried.append(f"{s}: module found but it has no `{func}`")
                continue
            return fn
        except ModuleNotFoundError as e:
            tried.append(f"{s}: {e}")
    raise SystemExit("Arman's data loader was not found. Tried:\n  " + "\n  ".join(tried) +
                     "\nPoint to it with --loader module:function (or path/to/file.py:function), or set $QRL_LOADER. "
                     "It must provide load_data(benchmark, split_seed=0) -> router.Data (see README.md, 'Open assumptions').")


# ---------------------------------------------------------------- finer task-type labels (parquet or CSV)

def load_level_labels(path, data, level_columns=DEFAULT_LEVEL_COLUMNS) -> dict:
    """{level: labels aligned with data.queries} from a CSV written by the offline classification step.
    The CSV has a `query` column (the query text) or an `index` column (position in data.queries) and any of the
    level columns (task_level1, task_level2, task_level3 by default). Queries without a row get 'unlabeled'."""
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit(f"{path}: empty labels file")
    by_text = "query" in rows[0]
    if not by_text and "index" not in rows[0]:
        raise SystemExit(f"{path}: needs a `query` or an `index` column; found {list(rows[0])}")
    present = {lvl: col for lvl, col in level_columns.items() if col in rows[0]}
    if not present:
        raise SystemExit(f"{path}: none of the level columns {list(level_columns.values())} found; columns are {list(rows[0])}")
    pos = {q: i for i, q in enumerate(data.queries)} if by_text else None
    out = {lvl: np.full(len(data.queries), "unlabeled", dtype=object) for lvl in present}
    unmatched = 0
    for r in rows:
        i = pos.get(r["query"]) if by_text else int(r["index"])
        if i is None or not (0 <= i < len(data.queries)):
            unmatched += 1
            continue
        for lvl, col in present.items():
            if r[col] not in ("", None):
                out[lvl][i] = r[col]
    for lvl, labs in out.items():
        n_missing = int((labs == "unlabeled").sum())
        if n_missing:
            print(f"WARNING: level {lvl}: {n_missing} of {len(labs)} queries have no label in {path} ('unlabeled')")
    if unmatched:
        print(f"WARNING: {unmatched} rows of {path} match no query in the data")
    return out


def load_parquet_labels(path, data) -> dict:
    """{1: level1, 2: level2, 3: level3} from labeling's task_labels.parquet (`query_id, level1, level2, level3`),
    matched on `data.query_ids` (falls back to row order when the data has no query ids)."""
    import pandas as pd
    labels = pd.read_parquet(path)
    ids = getattr(data, "query_ids", None)
    if ids is not None:
        labels = labels.set_index("query_id").reindex(np.asarray(ids))
        missing = int(labels["level1"].isna().sum())
    else:
        missing = max(0, len(data.queries) - len(labels))
        labels = labels.reindex(range(len(data.queries)))
    if missing:
        print(f"WARNING: {missing} of {len(data.queries)} queries have no row in {path} ('unlabeled')")
    return {lvl: labels[f"level{lvl}"].fillna("unlabeled").to_numpy(dtype=object) for lvl in (1, 2, 3)}


def labels_for(spec, benchmark, data) -> dict | None:
    """The `labels` argument of the embeddings for `spec`: "auto" (default) reads preproc/data/<benchmark>/
    task_labels.parquet when it exists and gives None otherwise; "none" gives None; a .parquet or .csv path is read."""
    if spec in (None, "none"):
        return None
    if spec == "auto":
        path = LABELS_DIR / str(benchmark) / "task_labels.parquet"
        return load_parquet_labels(path, data) if path.exists() else None
    return load_parquet_labels(spec, data) if str(spec).endswith(".parquet") else load_level_labels(spec, data)


# ---------------------------------------------------------------- release timeline

def release_order(data) -> list[str]:
    """Models in release order. ASSUMPTION: Arman's Data carries `release_order` (list of model names, earliest first)
    or `release_date` (one per model, sortable); otherwise `data.models` is taken to already be in release order."""
    if getattr(data, "release_order", None) is not None:
        return list(data.release_order)
    if getattr(data, "release_date", None) is not None:
        dates = list(data.release_date)
        return [data.models[i] for i in np.argsort(np.asarray(dates, dtype=object), kind="stable")]
    return list(data.models)


def cost_at_epoch(data, t: int, pool_idx: list[int]) -> np.ndarray:
    """Mean cost of the pool models at release epoch t. ASSUMPTION: `data.cost_by_epoch` is (n_epochs, n_models) if
    costs vary with the epoch; otherwise `data.cost` (the cost at the evaluated epoch) is used for every epoch."""
    by_epoch = getattr(data, "cost_by_epoch", None)
    if by_epoch is not None:
        return np.asarray(by_epoch)[t][pool_idx]
    return np.asarray(data.cost)[pool_idx]


def data_at_epoch(data, order: list[str], t: int):
    """The Data restricted to the models released up to and including event t (pool of the replayed timeline)."""
    pool = order[: t + 1]
    idx = [data.models.index(m) for m in pool]
    return dataclasses.replace(data, models=pool, S=np.asarray(data.S)[:, idx], cost=cost_at_epoch(data, t, idx))


def make_results(data, benchmark, root) -> Results:
    """`Results` names its folder by the second; two folders for the same split in one second would collide."""
    while True:
        try:
            return Results(data, benchmark, root=root)
        except FileExistsError:
            time.sleep(1.05)


# ---------------------------------------------------------------- k tuning bookkeeping

_EDGE = re.compile(r"best k=(\d+) is at the (upper|lower) edge")


class Tuning:
    """Collects, per run, the tuned k, the grid, whether the harness's `select_k` reported the best k at the edge of
    the grid, and whether the selected k sits at the edge; written to k_tuning.csv next to results.csv."""

    def __init__(self, out: Results, k_grid):
        self.out, self.k_grid, self.rows = out, tuple(k_grid), []

    @contextlib.contextmanager
    def capture(self):
        """Run the harness with its stdout captured; yields a dict that receives the parsed edge warning."""
        info, buf = {"best_k_at_edge": False, "best_k": ""}, io.StringIO()
        with contextlib.redirect_stdout(buf):
            yield info
        text = buf.getvalue()
        if m := _EDGE.search(text):
            info.update(best_k_at_edge=True, best_k=int(m.group(1)))
        for line in text.splitlines():  # keep anything else the harness printed
            if not _EDGE.search(line):
                print(line)

    def record(self, res, embedding, new_model, n_probes, seed, info, tuned):
        k = int(res["k"])
        self.rows.append({"run": f"{len(self.out.rows) - 1:04d}", "benchmark": self.out.benchmark, "embedding": embedding,
                          "new_model": new_model or "", "n_probes": n_probes or "", "seed": seed,
                          "split_seed": self.out.data.split_seed, "k": k, "k_grid": " ".join(map(str, self.k_grid)),
                          "tuned": tuned, "best_k": info["best_k"], "best_k_at_edge": info["best_k_at_edge"],
                          "selected_k_at_edge": k in (min(self.k_grid), max(self.k_grid))})
        with open(self.out.dir / "k_tuning.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.rows[0])
            w.writeheader()
            w.writerows(self.rows)

    def run_seen(self, embedding, fit, **kw):
        with self.capture() as info:
            res = self.out.run(embedding, fit, tune_k=True, k_grid=self.k_grid, **kw)
        self.record(res, embedding, None, None, 0, info, "per run")
        return res, info

    def select_k_once(self, fit, new_model, n_lambdas):
        """The harness's `select_k` for the pool without `new_model` (what `evaluate(tune_k=True)` would do)."""
        data = self.out.data
        new = data.models.index(new_model)
        pool = [m for m in range(len(data.models)) if m != new]
        E = np.asarray(fit([data.models[m] for m in pool])(data.queries))
        with self.capture() as info:
            k = router.select_k(E, data, pool, self.k_grid, n_lambdas=n_lambdas)
        return k, info

    def run_unseen(self, embedding, fit, new_model, n_probes, seed, k, info, **kw):
        res = self.out.run(embedding, fit, new_model=new_model, n_probes=n_probes, seed=seed, tune_k=False, k=k, **kw)
        self.record(res, embedding, new_model, n_probes, seed, info, "once per held-out model")
        return res


# ---------------------------------------------------------------- the loop

def plan_runs(args, data):
    """Yield (epoch, pool_data, new_model) for the unseen setting. `epoch` is None in full-pool mode."""
    order = release_order(data)
    if args.new_models:
        order = [m for m in order if m in args.new_models]
    if args.timeline == "full-pool":
        for m in order:
            yield None, data, m
    else:
        full = release_order(data)
        for t, m in enumerate(full):
            # event 0 has no pool; at event 1 the pool without the new model is one model, so there is nothing to
            # route among and the harness's k tuning divides by a zero cost range (see HARNESS_NOTES.md)
            if t < 2 or m not in order:
                continue
            yield t, data_at_epoch(data, full, t), m


def build_fits(args, benchmark, data, log):
    """One frozen `fit` per variant, built once per split. Variants whose task-type levels have no labels are skipped."""
    kw = dict(onehot_weight=args.onehot_weight if args.onehot_weight == "balanced" else float(args.onehot_weight),
              tokenizer=args.tokenizer, level_weights=dict(zip((1, 2, 3), args.level_weights)))
    labels = labels_for(args.level_labels, benchmark, data)
    if labels is not None:
        kw["labels"] = labels
    fits = {}
    for name in args.variants:
        try:
            fits[name] = VARIANTS[name](data, **kw)
        except MissingLevels as e:
            log(f"  {name}: skipped ({e})")
            continue
        log(f"  {name}: {fits[name](None).describe()}")
    return fits


def unseen_variants(args) -> list[str]:
    return list(args.variants) if args.unseen_variants == ["all"] else [v for v in args.unseen_variants if v in args.variants]


def describe_levels(args, benchmark, data, log):
    """What each task-type level would be built from, and the taxonomy coverage of the raw labels (for --dry-run)."""
    labels = labels_for(args.level_labels, benchmark, data)
    for level in (0, 1, 2, 3):
        labs = level_labels(data, level, labels, warn=False)
        src = "missing" if labs is None else f"{len(set(labs.tolist()))} categories"
        if labs is not None and level == 1 and not (labels and labels.get(1) is not None) and getattr(data, "task_level1", None) is None:
            src += " (taxonomy applied to the raw label)"
        log(f"  level {level}: {src}")
    raw = getattr(data, "theme", None)
    if raw is not None:
        log("  taxonomy coverage of the raw labels:\n    " + task_taxonomy.report(raw).replace("\n", "\n    "))


def run_split(args, benchmark, data, log):
    fits = build_fits(args, benchmark, data, log)
    if not fits:
        log("  no variant could be built on this split; skipping")
        return
    common = dict(n_lambdas=args.n_lambdas)
    edge = lambda info, res: " [k at grid edge]" if info["best_k_at_edge"] or res["k"] in (min(args.k_grid), max(args.k_grid)) else ""
    un_names = [n for n in unseen_variants(args) if n in fits]

    def seen_runs(out, tuning):
        for name, fit in fits.items():
            res, info = tuning.run_seen(name, fit, n_boot=args.n_boot, **common)
            log(f"  seen  {name:22s} gain={res['gain']:+.4f} A={res['A']:.4f} k={res['k']}{edge(info, res)}")

    def unseen_runs(out, tuning, data_t, new_model):
        for name in un_names:
            fit = fits[name]
            k, info = tuning.select_k_once(fit, new_model, args.n_lambdas)
            for n in args.n_grid:
                for seed in range(args.probe_seeds):
                    res = tuning.run_unseen(name, fit, new_model, n, seed, k, info, n_boot=args.n_boot_unseen, **common)
            log(f"  unseen {name:22s} new={new_model} k={k}{edge(info, res)} n={args.n_grid} x {args.probe_seeds} seeds "
                f"done (last gain={res['gain']:+.4f})")

    if args.timeline == "full-pool":
        out = make_results(data, benchmark, args.results_root)
        tuning = Tuning(out, args.k_grid)
        log(f"  -> {out.dir}")
        if not args.skip_seen:
            seen_runs(out, tuning)
        if args.skip_unseen:
            return
        for _, _, new_model in plan_runs(args, data):
            unseen_runs(out, tuning, data, new_model)
    else:  # replay: one Results per release event, seen run per epoch (gains are only comparable within an epoch)
        for t, data_t, new_model in plan_runs(args, data):
            out = make_results(data_t, benchmark, args.results_root)
            tuning = Tuning(out, args.k_grid)
            (out.dir / "epoch.json").write_text(json.dumps({"epoch": t, "pool": data_t.models, "new_model": new_model}, indent=2))
            log(f"  epoch {t} new={new_model} pool={len(data_t.models)} -> {out.dir}")
            if not args.skip_seen:
                seen_runs(out, tuning)
            if not args.skip_unseen:
                unseen_runs(out, tuning, data_t, new_model)


def count_runs(args, data):
    n_events = sum(1 for _ in plan_runs(args, data))
    seen = len(args.variants) * (n_events if args.timeline == "replay" else 1) * (not args.skip_seen)
    unseen = 0 if args.skip_unseen else n_events * len(unseen_variants(args)) * len(args.n_grid) * args.probe_seeds
    return seen, unseen


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--benchmarks", nargs="+", default=["llmrouterbench", "routerbench"])
    p.add_argument("--split-seeds", nargs="+", type=int, default=[0, 1, 2])
    p.add_argument("--variants", nargs="+", default=DEFAULT_VARIANTS, choices=list(VARIANTS),
                   help="variants of the seen setting; those whose task-type levels have no labels are skipped")
    p.add_argument("--unseen-variants", nargs="+", default=DEFAULT_UNSEEN_VARIANTS,
                   help="variants of the unseen loop (subset of --variants), or 'all'")
    p.add_argument("--level-labels", default="auto",
                   help="task labels: 'auto' (preproc/data/<benchmark>/task_labels.parquet if present), 'none', "
                        "a .parquet (query_id, level1-3) or a CSV (query|index + task_level1-3)")
    p.add_argument("--level-weights", nargs=3, type=float, default=[1.0, 1.0, 1.0], metavar=("W1", "W2", "W3"),
                   help="relative weights of levels 1, 2, 3 inside the task-type block")
    p.add_argument("--n-grid", nargs="+", type=int, default=[1, 2, 5, 10, 20, 50, 100, 500], help="probe budgets")
    p.add_argument("--probe-seeds", type=int, default=5, help="probe draws per budget (seeds 0..n-1)")
    p.add_argument("--timeline", choices=["full-pool", "replay"], default="full-pool",
                   help="full-pool: pool = all models, each model in turn held out (README loop). "
                        "replay: pool = models released up to each event, one results folder per event")
    p.add_argument("--new-models", nargs="*", default=None, help="restrict the held-out models (default: all)")
    p.add_argument("--skip-seen", action="store_true")
    p.add_argument("--skip-unseen", action="store_true")
    p.add_argument("--n-boot", type=int, default=1000, help="bootstrap resamples for seen runs")
    p.add_argument("--n-boot-unseen", type=int, default=200, help="bootstrap resamples for unseen runs (0 skips)")
    p.add_argument("--k-grid", nargs="+", type=int, default=list(DEFAULT_K_GRID))
    p.add_argument("--n-lambdas", type=int, default=500)
    p.add_argument("--results-root", default=str(REPO / "results"))
    p.add_argument("--onehot-weight", default="balanced", help="'balanced' or a float: weight of the one-hot block")
    p.add_argument("--tokenizer", default="tiktoken:cl100k_base", help="tiktoken:<enc> | hf:<name> | whitespace")
    p.add_argument("--loader", default=None, help="module:function or path.py:function giving load_data")
    p.add_argument("--dry-run", action="store_true",
                   help="load the data, print the plan, the run counts, the task-type levels and the taxonomy coverage; run nothing")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    load_data = find_load_data(args.loader)
    log = lambda *a: print(*a, flush=True)
    for benchmark in args.benchmarks:
        for split_seed in args.split_seeds:
            data = load_data(benchmark, split_seed=split_seed)
            if getattr(data, "split_seed", None) != split_seed:
                log(f"WARNING: load_data({benchmark!r}, split_seed={split_seed}) returned Data.split_seed="
                    f"{getattr(data, 'split_seed', None)}; the results folder uses Data.split_seed")
            seen, unseen = count_runs(args, data)
            log(f"{benchmark} split {split_seed}: {len(data.queries)} queries, {len(data.models)} models, "
                f"{len(data.train)}/{len(data.val)}/{len(data.test)} train/val/test, "
                f"theme={'yes' if getattr(data, 'theme', None) is not None else 'MISSING'}; "
                f"release order: {release_order(data)}; {seen} seen + {unseen} unseen runs "
                f"(unseen variants: {unseen_variants(args)}); k grid {tuple(args.k_grid)}")
            if args.dry_run:
                describe_levels(args, benchmark, data, log)
                continue
            run_split(args, benchmark, data, log)


if __name__ == "__main__":
    main()
