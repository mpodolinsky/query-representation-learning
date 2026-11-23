"""Assemble REPORT.md (and report_data.json) from everything the project has produced:
  ../results_summary/            Nikhilesh's complete grid (seen_summary, unseen_summary, metrics, probes_to_target,
                                 sensitivity_summary, figures)
  analysis/                      the handcrafted-variant runs (seen_table, unseen_table, A_unseen_curves, k_tuning,
                                 stats_predict_labels, figures)
  analysis_compare/              paired bootstrap comparisons and the embedding views / label structure
  ../results_compare/metrics.csv the unified comparison with our task-type levels (when it has been run)
  ../labeling/reports/           the task-label hand check
Sections whose inputs are missing say so instead of failing, so the report can be rebuilt as results arrive.

    python build_report.py                      # writes REPORT.md next to this file
    python build_report.py --out ../REPORT.md"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for p in (REPO, REPO / "michal-harness", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

NIK = REPO / "results_summary"
MINE = HERE / "analysis"
CMP = HERE / "analysis_compare"
UNIFIED = REPO / "results_compare" / "metrics.csv"

WHAT = {  # representation name -> (plain description, who)
    "task_type": ("one-hot of the benchmark's theme (source dataset)", "Nikhilesh"),
    "task_type_theme": ("one-hot of the benchmark's theme (source dataset)", "shared"),
    "task_type_raw": ("one-hot of the benchmark's theme (source dataset)", "Alexandros"),
    "task_type_L1": ("one-hot of the LLM-assigned Level-1 domain (11)", "Alexandros"),
    "task_type_L2": ("one-hot of the Level-2 subdomain (~85)", "Alexandros"),
    "task_type_L12": ("one-hots of Level 1 and Level 2 side by side", "Alexandros"),
    "task_type_L123": ("Levels 1, 2 and the free-text Level 3 (thousands of columns)", "Alexandros"),
    "stats": ("15 z-scored query statistics (lengths, code/math markers, ...)", "Alexandros"),
    "stats_whitened": ("the statistics after PCA whitening", "Alexandros"),
    "stats_within_theme": ("the statistics, neighbours restricted to the query's theme", "Alexandros"),
    "handcrafted": ("Level 1 + Level 2 one-hots + the 15 statistics (representation i)", "Alexandros"),
    "handcrafted_L1": ("Level 1 one-hot + the statistics", "Alexandros"),
    "handcrafted_L123": ("Levels 1-3 one-hots + the statistics", "Alexandros"),
    "handcrafted_whitened": ("Levels 1-2 + whitened statistics", "Alexandros"),
    "handcrafted_nik": ("theme one-hot + 3 length statistics, standardized (Nikhilesh's handcrafted)", "Nikhilesh"),
    "frozen": ("all-MiniLM-L6-v2 sentence embedding, 384-d, L2-normalized (representation ii)", "Nikhilesh"),
    "combined": ("frozen + handcrafted block (representation iii)", "both"),
    "combined_balanced": ("frozen + handcrafted block with equal mean squared norms", "Nikhilesh"),
    "regression": ("MLP on the sentence vector, trained to predict every model's score (iv)", "Nikhilesh"),
    "contrastive": ("MLP on the sentence vector, trained to pull together queries with similar score profiles (iv)", "Nikhilesh"),
    "regression_hc": ("the regression MLP on [sentence vector, our handcrafted block]", "both"),
    "contrastive_hc": ("the contrastive MLP on [sentence vector, our handcrafted block]", "both"),
}


# ---------------------------------------------------------------- helpers

def pct(v, digits=2, sign=True):
    return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{100 * v:{'+' if sign else ''}.{digits}f}%"


def num(v, digits=4):
    return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{digits}f}"


def table(rows, header):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def read(path, **kw):
    path = Path(path)
    return pd.read_csv(path, **kw) if path.exists() else None


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=REPO).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO).stdout.strip()
        return out + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def rel(path):
    """Path relative to the report's folder."""
    try:
        return str(Path(path).resolve().relative_to(HERE))
    except ValueError:
        return "../" + str(Path(path).resolve().relative_to(REPO))


# ---------------------------------------------------------------- data section

def data_section(facts):
    lines = ["## 2. Data", ""]
    try:
        from preproc.data import load_data, unseen_instances
        rows = []
        for b in ("llmrouterbench", "routerbench"):
            d = load_data(b, split_seed=0)
            inst = unseen_instances(b)
            labels = read(REPO / "preproc" / "data" / b / "task_labels.parquet") if False else None
            lab = pd.read_parquet(REPO / "preproc" / "data" / b / "task_labels.parquet") if (REPO / "preproc" / "data" / b / "task_labels.parquet").exists() else None
            rows.append([b, f"{len(d.queries):,}", len(d.models), f"{len(d.train):,} / {len(d.val):,} / {len(d.test):,}",
                         len(set(d.theme)), len(inst), "—" if lab is None else f"{lab.level1.nunique()} / {lab.level2.nunique()} / {lab.level3.nunique():,}"])
            facts[f"{b}_queries"], facts[f"{b}_models"], facts[f"{b}_instances"] = len(d.queries), len(d.models), len(inst)
        lines += [table(rows, ["benchmark", "queries", "models", "train / val / test (split 0)", "themes", "release instances",
                               "task labels L1 / L2 / L3"]), ""]
    except Exception as e:  # the loader needs the processed data
        lines += [f"_(data tables unavailable: {e})_", ""]
    lines += [
        "**Benchmarks.** LLMRouterBench (primary): 21 source datasets reduced by Arman's preprocessing to 9 themes, 13 flagship "
        "models with list prices (DeepSeek-V3 to GLM-4.6, released March to September 2025), one score per model and query "
        "in [0, 1]. RouterBench (secondary): 8 datasets (12 themes, MMLU per subject), 11 models of 2023. Each benchmark has "
        "three random train/validation/test splits (70/10/20, stratified by theme), shared by every representation; the "
        "validation split is used only to choose the neighbourhood size k.",
        "",
        "**Release timeline.** Models are replayed in release order. An *unseen instance* is one model held out: the pool is "
        "every model released before it plus the new one, whose scores are unknown except on n probe queries drawn from the "
        "training split (budgets 1, 5, 10, 20, 50, 100, 500; nested, the same probes for every representation).",
        "",
        "**Task-type labels.** Besides the benchmark's own theme, every query carries a three-level task type assigned "
        "offline by Qwen3-32B with a closed taxonomy (11 Level-1 domains, 90 Level-2 subdomains, free-text Level 3). A "
        "stratified hand check of 200 rows per benchmark found Level 1 correct in 94.0% (LLMRouterBench) and 92.5% "
        "(RouterBench) of rows, Levels 1 and 2 both correct in 82.5% and 88.0% (`labeling/reports/handcheck_summary.md`).",
        ""]
    return lines


# ---------------------------------------------------------------- methods

def methods_section():
    return ["## 3. Representations and methods", "",
        "### 3.1 The query representations", "",
        table([[k, v[0], v[1]] for k, v in WHAT.items()], ["name in the tables", "what it is", "who"]), "",
        "**The 15 query statistics** (Alexandros, `handcrafted.py`): token count (tiktoken cl100k), characters, words, "
        "sentences, lines, question marks, code-marker count and a code flag (backticks, braces, `def`, `return`, SQL, ...), "
        "digit, math-symbol and punctuation density, upper-case and non-ASCII fractions, average word length, characters per "
        "token. Counts are log1p-transformed, every statistic is z-scored on the training split and clipped at ±5 sd. The "
        "task-type block is one one-hot per level over the categories seen in training; it is scaled so that its total "
        "training variance equals the statistics block's (\"balanced\"), so neither block dominates the Euclidean distance.",
        "",
        "**Nikhilesh's handcrafted features** differ: theme one-hot plus three raw length counts (characters, lexical tokens, "
        "lines), standardized column-wise. His `combined` concatenates the unit-norm sentence vector with that block "
        "(unweighted; a balanced version was also run).", "",
        "### 3.2 The learned embeddings: regression and contrastive", "",
        "Both start from the frozen MiniLM sentence vector (384-d) and train a small MLP, 384 → 128 → ReLU → 64, whose "
        "L2-normalized output is the embedding the router uses. They differ only in the training signal, which comes from "
        "the score table of the training queries and the models allowed in the pool:",
        "",
        "- **Regression.** A linear head with a sigmoid predicts, from the 64-d embedding, the score of every allowed "
        "model on the query (its *quality profile*); the loss is the mean squared error. The head is discarded after "
        "training: only the embedding is used, so two queries end up close when the MLP needs similar coordinates to "
        "predict similar profiles.",
        "- **Contrastive.** Pairs of queries in a minibatch are *positive* when the mean squared difference of their "
        "quality profiles is at most 0.1 (the models behave the same on them) and *negative* otherwise. Positives are "
        "pulled together (squared distance), negatives are pushed apart up to a margin of 1 (hinge, squared); the two "
        "terms are averaged separately so the many negatives do not drown the positives.",
        "",
        "Training: Adam, learning rate 0.001, batch 128, at most 50 epochs, early stopping (patience 5) on 10% of the "
        "training queries held out for that purpose; `data.val` and `data.test` never enter training. In the unseen "
        "setting the held-out model's column is removed from the profiles, so the embedding is retrained without it; "
        "three training seeds. The `_hc` variants feed the MLP the concatenation [sentence vector, our handcrafted block] "
        "instead of the sentence vector alone.", "",
        "### 3.3 The router and the metrics (Michal's harness)", "",
        "For a query x and a model m, the router estimates the quality q̂_m(x) as the mean score of m over the k nearest "
        "training queries in the representation (Euclidean distance; a new model uses its probes as the labeled set). "
        "It then picks argmax_m q̂_m(x) − λ·cost(m), where cost(m) is the model's mean cost per query. Sweeping λ (0 plus "
        "500 log-spaced values) traces a cost–quality curve on the test queries; **A** is the area under that curve "
        "(log-cost axis, best-quality-within-budget envelope) divided by the oracle's area (the oracle routes by the "
        "true test scores). The **single best** is the fixed model with the best q − λ·cost on the training queries; "
        "**gain** = area(router) / area(single best) − 1 is the main number, and it is the same baseline in the seen and "
        "the unseen setting, so the unseen curve against n reflects the router only. **Recovery** = unseen gain / seen "
        "gain of the same representation and pool. k is chosen on the validation split by the one-standard-error rule "
        "(largest k whose validation area is within one bootstrap standard error of the best).", "",
        "### 3.4 Statistics", "",
        "- **Bootstrap intervals.** Every run has a 95% paired percentile bootstrap interval of its gain over 1,000 "
        "resamples of the test queries (the router and the single best are resampled together).",
        "- **Paired differences between representations** (`paired_tests.py`): on the same split and pool, the "
        "difference of two representations' gains is recomputed on 1,000 shared resamples of the test queries, which "
        "gives an interval and a two-sided bootstrap p-value for the difference itself.",
        "- **Three sources of spread, kept separate:** across the three splits (reported as ± sd of split means), "
        "across training seeds (learned embeddings) and across probe draws (unseen). With three splits these are "
        "descriptive, not tests; the paired test-query intervals are the inferential evidence.",
        "- **Task-type recovery** (RQ1a) = A(task-type one-hot) / A(learned embedding), same pool and seeds; "
        "**probes-to-target** = the smallest budget whose A_unseen reaches 90% of the seen A (the proposal's "
        "definition) or whose recovery reaches 90%.",
        "- **Embedding structure** (`embedding_views.py`): PCA and t-SNE small multiples by theme, Level 1 and Level 2, "
        "plus the share of a test query's 10 nearest training neighbours with the same label (what the router sees), "
        "a linear probe's test accuracy and the silhouette of the labels.", ""]


# ---------------------------------------------------------------- results: Nikhilesh's grid

def nik_seen(facts):
    seen, metrics = read(NIK / "seen_summary.csv"), read(NIK / "metrics.csv")
    if seen is None:
        return ["_(results_summary/seen_summary.csv not found)_", ""]
    ci = None
    if metrics is not None:
        m = metrics[(metrics.setting == "seen") & (metrics.instance == -1)].copy()
        m["half"] = (m.gain_ci_high - m.gain_ci_low) / 2
        ci = m.groupby(["benchmark", "embedding"])["half"].mean()
    rows = []
    for r in seen.sort_values(["benchmark", "gain_mean"], ascending=[True, False]).itertuples():
        half = ci.get((r.benchmark, r.embedding), np.nan) if ci is not None else np.nan
        rows.append([r.benchmark, r.embedding, f"{pct(r.gain_mean)} ± {pct(r.gain_split_sd, sign=False)}",
                     "± " + pct(half, sign=False), num(r.A_mean), num(r.A_training_sd) if r.A_training_sd else "0"])
        facts[f"nik_seen_{r.benchmark}_{r.embedding}"] = {"gain": r.gain_mean, "sd": r.gain_split_sd, "A": r.A_mean, "ci_half": half}
    return ["Means over 3 splits × 3 training seeds (deterministic representations are identical across training seeds). "
            "The bootstrap column is the mean half-width of the per-run 95% test-query interval.", "",
            table(rows, ["benchmark", "representation", "gain ± sd over splits", "bootstrap 95% half-width", "A", "A sd over training seeds"]), ""]


def seen_unseen_table(metrics: pd.DataFrame, budgets=(5, 50, 500)):
    """Per benchmark and representation: seen gain on the final pool, mean unseen gain at each budget over all
    instances, and the mean recovery (unseen / seen gain of the same instance pool). Ranks per setting."""
    out = []
    m = metrics.copy()
    m["n_probes"] = pd.to_numeric(m["n_probes"], errors="coerce").fillna(0).astype(int)
    for bench, g in m.groupby("benchmark"):
        final = g[(g.setting == "seen") & (g.instance == -1)].groupby("embedding").gain.mean()
        inst_seen = g[(g.setting == "seen") & (g.instance != -1)].groupby(["embedding", "instance"]).gain.mean()
        unseen = g[g.setting == "unseen"].groupby(["embedding", "instance", "n_probes"]).gain.mean()
        for emb in sorted(final.index):
            row = {"benchmark": bench, "embedding": emb, "gain_seen": final[emb]}
            for n in budgets:
                vals = unseen.xs(emb, level=0) if emb in unseen.index.get_level_values(0) else pd.Series(dtype=float)
                vals = vals[vals.index.get_level_values("n_probes") == n] if len(vals) else vals
                row[f"gain_unseen_{n}"] = vals.mean() if len(vals) else np.nan
                if len(vals):
                    rec = []
                    for (inst, _), v in vals.items():
                        s = inst_seen.get((emb, inst), np.nan)
                        if np.isfinite(s) and s > 0:
                            rec.append(v / s)
                    row[f"recovery_{n}"] = float(np.mean(rec)) if rec else np.nan
                else:
                    row[f"recovery_{n}"] = np.nan
            out.append(row)
    df = pd.DataFrame(out)
    if df.empty:
        return df
    for col in ["gain_seen"] + [f"gain_unseen_{n}" for n in budgets]:
        df[f"rank_{col}"] = df.groupby("benchmark")[col].rank(ascending=False, method="min")
    return df


def seen_unseen_markdown(df, budgets=(5, 50, 500)):
    if df is None or df.empty:
        return ["_(no metrics)_", ""]
    header = ["benchmark", "representation", "seen gain (rank)"] + [f"unseen gain, n={n} (rank)" for n in budgets] + [f"recovery n={n}" for n in budgets]
    rows = []
    for r in df.sort_values(["benchmark", "gain_seen"], ascending=[True, False]).itertuples():
        cells = [r.benchmark, r.embedding, f"{pct(r.gain_seen)} ({int(r.rank_gain_seen)})"]
        cells += [f"{pct(getattr(r, f'gain_unseen_{n}'))} ({int(getattr(r, f'rank_gain_unseen_{n}'))})" if np.isfinite(getattr(r, f'gain_unseen_{n}')) else "—" for n in budgets]
        cells += [num(getattr(r, f"recovery_{n}"), 2) for n in budgets]
        rows.append(cells)
    return [table(rows, header), ""]


def nik_unseen(facts):
    metrics = read(NIK / "metrics.csv")
    lines = []
    if metrics is None:
        return ["_(results_summary/metrics.csv not found)_", ""]
    df = seen_unseen_table(metrics)
    facts["nik_seen_unseen"] = df.to_dict("records")
    lines += ["Seen gain on the final pool against the unseen gain (mean over every release instance, 3 splits, 3 training "
              "seeds, 3 probe seeds) at three probe budgets, with the rank of each representation per column; recovery is the "
              "unseen gain divided by the seen gain of the same instance pool, averaged over instances.", ""]
    lines += seen_unseen_markdown(df)
    us = read(NIK / "unseen_summary.csv")
    if us is not None:
        t = us[us.n_probes == 500]
        for bench, g in t.groupby("benchmark"):
            piv = g.pivot(index=["instance", "new_model"], columns="embedding", values="A_mean")
            rows = [[i, m] + [num(piv.loc[(i, m), c]) for c in piv.columns] for i, m in piv.index]
            lines += [f"A at 500 probes, every release instance of {bench} (mean over seeds; compare within a row, pools differ):", "",
                      table(rows, ["instance", "new model"] + list(piv.columns)), ""]
    for b in ("llmrouterbench", "routerbench"):
        if (NIK / f"{b}_unseen_releases.png").exists():
            lines += [f"![{b} unseen releases]({rel(NIK / f'{b}_unseen_releases.png')})", ""]
    return lines


def nik_rq1a_ptt_sens():
    lines = []
    seen = read(NIK / "seen_summary.csv")
    if seen is not None:
        rows = [[r.benchmark, r.embedding, num(r.task_type_recovery_mean), num(r.task_type_recovery_split_sd)]
                for r in seen[seen.embedding.isin(["regression", "contrastive"])].itertuples()]
        lines += ["Task-type recovery with the *theme* one-hot (Nikhilesh's grid): A(task_type) / A(learned), final pool.", "",
                  table(rows, ["benchmark", "learned objective", "recovery", "sd over splits"]), ""]
    ptt = read(NIK / "probes_to_target.csv")
    if ptt is not None:
        reached = ptt[ptt.status == "reached"]
        lines += [f"Probes-to-target (90% of the seen A): {len(reached):,} of {len(ptt):,} cases reach it within the tested budgets, "
                  f"{int((reached.probes_to_target == 1).sum()):,} at one probe. The A-based target is uninformative here: the "
                  "single best alone already has A ≥ 0.9·A_seen (0.955 on LLMRouterBench, 0.931 on RouterBench), so the recovery-"
                  "based target in section 5.2 is the one to read.", ""]
    sens = read(NIK / "sensitivity_summary.csv")
    if sens is not None:
        rows = [[r.benchmark, r.variant, num(r.p95_abs_delta_A), num(r.max_abs_delta_A)]
                for r in sens[sens.variant != "reference"].itertuples()]
        lines += ["Sensitivity (one factor at a time, every main run; paired absolute change of A from the reference run):", "",
                  table(rows, ["benchmark", "variant", "95th percentile |ΔA|", "max |ΔA|"]), "",
                  "k matters (fixed k = 5 or 10 moves A by up to 0.1–0.3), the λ grid barely (95th percentile below 0.002).", ""]
    for b in ("llmrouterbench", "routerbench"):
        if (NIK / f"{b}_k_sensitivity.png").exists():
            lines += [f"![{b} k sensitivity]({rel(NIK / f'{b}_k_sensitivity.png')})", ""]
    return lines


# ---------------------------------------------------------------- results: my variants

def mine_seen(facts):
    t = read(MINE / "seen_table.csv")
    if t is None:
        return ["_(analysis/seen_table.csv not found)_", ""]
    rows = []
    for r in t.sort_values(["benchmark", "gain_mean"], ascending=[True, False]).itertuples():
        rows.append([r.benchmark, r.embedding, f"{pct(r.gain_mean)} ± {pct(r.gain_std, sign=False)}", "± " + pct(r.ci_width_mean / 2, sign=False),
                     num(r.A_mean), r.k_per_split + (" †" if r.k_edge else "")])
        facts[f"mine_seen_{r.benchmark}_{r.embedding}"] = {"gain": r.gain_mean, "sd": r.gain_std, "A": r.A_mean}
    return ["Handcrafted variants (Alexandros' runs of 2026-11-16, commit cde8206; 3 splits, k grid 5 … 1000). "
            "† = the selected k is the top of the grid on at least one split (the validation curve is flat up to the top, see RESULTS.md).", "",
            table(rows, ["benchmark", "variant", "gain ± sd over splits", "bootstrap 95% half-width", "A", "k per split"]), ""]


def mine_unseen():
    c = read(MINE / "A_unseen_curves.csv")
    lines = []
    if c is not None:
        rows = [[r.benchmark, int(r.n_probes), pct(r.gain_mean), pct(r.gain_same_probes_mean), num(r.recovery_mean, 2), num(r.A_mean)]
                for r in c.sort_values(["benchmark", "n_probes"]).itertuples()]
        lines += ["`handcrafted`, every model held out in turn from the full pool (3 splits × 5 probe seeds; mean over held-out "
                  "models). `gain (same probes)` is over the single best that knows the new model only from the same n probes.", "",
                  table(rows, ["benchmark", "n probes", "gain", "gain (same probes)", "recovery", "A"]), ""]
    for b in ("llmrouterbench", "routerbench"):
        f = MINE / "figures" / f"gain_vs_probes_by_variant_{b}_epoch-1.png"
        if f.exists():
            lines += [f"![{b} gain vs probes]({rel(f)})", ""]
    p = read(MINE / "stats_predict_labels.csv")
    if p is not None:
        rows = [[r.benchmark, r.target, int(r.n_classes), pct(r.majority_test_acc, 1, False), pct(r.logit_test_acc, 1, False), pct(r.knn50_test_acc, 1, False)]
                for r in p.itertuples()]
        lines += ["How well the 15 statistics alone identify the task type (train → test):", "",
                  table(rows, ["benchmark", "label", "classes", "majority", "logistic regression", "kNN (k = 50)"]), ""]
    return lines


# ---------------------------------------------------------------- results: unified comparison, paired tests, views

def unified_section(facts):
    m = read(UNIFIED)
    if m is None:
        return ["_Not run yet._ `compare_representations.py` puts every representation, including the learned ones and the "
                "`_hc` variants, through the same protocol with our Level-1/Level-2 labels; this section fills itself from "
                "`results_compare/metrics.csv` once the run has finished (see section 7).", ""]
    lines = []
    seen = m[(m.setting == "seen") & (m.instance == -1)].copy()
    seen["half"] = (seen.gain_ci_high - seen.gain_ci_low) / 2
    g = seen.groupby(["benchmark", "embedding"])
    agg = g.agg(gain=("gain", "mean"), A=("A", "mean"), half=("half", "mean"), n=("gain", "size"),
                sd=("gain", lambda s: seen.loc[s.index].groupby("split_seed").gain.mean().std(ddof=0))).reset_index()
    rows = [[r.benchmark, r.embedding, f"{pct(r.gain)} ± {pct(r.sd, sign=False)}", "± " + pct(r.half, sign=False), num(r.A), int(r.n)]
            for r in agg.sort_values(["benchmark", "gain"], ascending=[True, False]).itertuples()]
    splits = [int(x) for x in sorted(m.split_seed.unique())]
    lines += [f"Final pool, seen setting; splits {splits}, training seeds {[int(x) for x in sorted(m.train_seed.unique())]}.", "",
              table(rows, ["benchmark", "representation", "gain ± sd over splits", "bootstrap 95% half-width", "A", "runs"]), ""]
    facts["unified_seen"] = agg.to_dict("records")
    if (m.setting == "unseen").any():
        df = seen_unseen_table(m)
        lines += ["Seen against unseen, every release instance run so far:", ""] + seen_unseen_markdown(df)
        facts["unified_seen_unseen"] = df.to_dict("records")
    # RQ1a per level
    final = seen.groupby(["benchmark", "split_seed", "train_seed", "embedding"]).A.mean().unstack("embedding")
    tasks = [c for c in final.columns if c.startswith("task_type")]
    learned = [c for c in ("regression", "contrastive", "regression_hc", "contrastive_hc") if c in final.columns]
    if tasks and learned:
        rows = []
        for t in tasks:
            for l in learned:
                ratio = (final[t] / final[l]).dropna()
                for bench, s in ratio.groupby(level=0):
                    rows.append([bench, t, l, num(s.mean()), num(s.std(ddof=0)), len(s)])
        lines += ["Task-type recovery per level, A(task-type one-hot) / A(learned), final pool:", "",
                  table(rows, ["benchmark", "task-type variant", "learned", "recovery", "sd", "runs"]), ""]
    return lines


def paired_section():
    s = read(CMP / "paired_seen_summary.csv")
    lines = []
    if s is None:
        return ["_(analysis_compare/paired_seen_summary.csv not found: run paired_tests.py)_", ""]
    rows = [[r.benchmark, f"{r.a} − {r.b}", f"{pct(r.d_gain_mean)} ± {pct(r.d_gain_sd, sign=False)}", f"{int(r.wins)} / {int(r.n)}",
             f"{int(r.ci_excludes_0)} / {int(r.n)}", num(r.median_p, 3)]
            for r in s[(s.setting == "seen") & (s.instance == -1)].sort_values(["benchmark", "d_gain_mean"], ascending=[True, False]).itertuples()]
    lines += ["Paired bootstrap over the test queries, final pool, seen setting: difference of gains on the same split, "
              "mean ± sd over splits; `wins` = splits where a > b; `CI excl. 0` = splits whose 95% paired interval excludes "
              "zero; p = median two-sided bootstrap p over splits.", "",
              table(rows, ["benchmark", "a − b", "Δ gain", "wins", "CI excl. 0", "median p"]), ""]
    u = read(CMP / "paired_unseen_summary.csv")
    if u is not None and not u.empty:
        agg = u.groupby(["benchmark", "n_probes", "a", "b"]).agg(d=("d_gain_mean", "mean"), wins=("wins", "sum"), n=("n", "sum"),
                                                                  excl=("ci_excludes_0", "sum")).reset_index()
        rows = [[r.benchmark, int(r.n_probes), f"{r.a} − {r.b}", pct(r.d), f"{int(r.wins)} / {int(r.n)}", f"{int(r.excl)} / {int(r.n)}"]
                for r in agg.sort_values(["benchmark", "n_probes", "d"], ascending=[True, True, False]).itertuples()]
        lines += ["Unseen setting (over instances × splits):", "", table(rows, ["benchmark", "n probes", "a − b", "Δ gain", "wins", "CI excl. 0"]), ""]
    return lines


def views_section():
    t = read(CMP / "label_structure.csv")
    lines = []
    if t is None:
        return ["_(analysis_compare/label_structure.csv not found: run embedding_views.py)_", ""]
    rows = [[r.benchmark, r.representation, r.label, int(r.n_classes), pct(r.majority, 1, False), pct(r.knn_purity_k10, 1, False),
             pct(r.linear_probe_acc, 1, False), num(r.silhouette, 3)]
            for r in t.sort_values(["benchmark", "label", "knn_purity_k10"], ascending=[True, True, False]).itertuples()]
    lines += ["Is a representation \"just the task type\"? Share of a test query's 10 nearest training neighbours with the same "
              "label (what the router averages over), a linear probe's test accuracy, and the silhouette of the labels:", "",
              table(rows, ["benchmark", "representation", "label", "classes", "majority", "kNN purity", "linear probe", "silhouette"]), ""]
    views = sorted((CMP / "views").glob("*.png")) if (CMP / "views").exists() else []
    if views:
        lines += ["Figures (PCA and t-SNE small multiples, one panel per category, the category in blue over all queries in gray):", ""]
        by_rep = {}
        for v in views:
            mm = re.match(r"(\w+?)_(.+)_(pca|tsne)_(theme|task_level\d)\.png", v.name)
            if mm:
                by_rep.setdefault((mm.group(1), mm.group(2)), []).append((mm.group(3), mm.group(4), v))
        for (bench, rep), items in sorted(by_rep.items()):
            lines.append(f"- {bench}, `{rep}`: " + ", ".join(f"[{kind} by {lab}]({rel(v)})" for kind, lab, v in sorted(items)))
        lines.append("")
        pick = [v for v in views if v.name.endswith("_tsne_task_level1.png")][:4]
        for v in pick:
            lines += [f"![{v.stem}]({rel(v)})", ""]
    return lines


def k_check_section():
    t = read(CMP / "k_unseen_check.csv")
    if t is None:
        return ["_(analysis_compare/k_unseen_check.csv not found: run k_unseen_check.py)_", ""]
    lines = ["The harness uses one k for every model. A new model has labels on n probes only, so its estimate averages "
             "min(k, n) probes: with k ≥ n it is one constant for every query (the probe mean). The table fixes k and "
             "shows the unseen gain at two budgets on a few release instances (split 0, one training and probe seed; "
             "checkpoints from the unified run, nothing retrained). Cells with k ≥ n are marked †.", ""]
    ks = sorted(t.k.unique())
    for (bench, n), g in t.groupby(["benchmark", "n_probes"]):
        piv = g.pivot_table(index=["representation", "instance"], columns="k", values="gain_unseen")
        rows = []
        for (rep, inst), r in piv.iterrows():
            rows.append([bench, rep, int(inst)] + [pct(r[k]) + (" †" if k >= n else "") for k in ks])
        lines += [f"n = {n} probes:", "", table(rows, ["benchmark", "representation", "instance"] + [f"k = {k}" for k in ks]), ""]
    return lines


# ---------------------------------------------------------------- observations and pending

def _u(facts, bench, emb, key="gain"):
    for r in facts.get("unified_seen", []):
        if r["benchmark"] == bench and r["embedding"] == emb:
            return r[key]
    return float("nan")


def _su(facts, bench, emb, key):
    for r in facts.get("unified_seen_unseen", []):
        if r["benchmark"] == bench and r["embedding"] == emb:
            return r.get(key, float("nan"))
    return float("nan")


def observations(facts):
    f = facts
    u = lambda b, e: pct(_u(f, b, e))
    su = lambda b, e, k: pct(_su(f, b, e, k))
    rec = lambda b, e, n: num(_su(f, b, e, f"recovery_{n}"), 2)
    have = bool(f.get("unified_seen"))
    lines = ["## 6. Observations", ""]
    if not have:
        lines += ["_(The unified comparison has not been run; see the earlier observations in the git history of this file.)_", ""]
        return lines
    L, R = "llmrouterbench", "routerbench"
    lines += [
        f"1. **Every representation beats the single best model in the seen setting**: from {u(L, 'contrastive')} (contrastive) "
        f"to {u(L, 'handcrafted_nik')} on LLMRouterBench and from {u(R, 'task_type_L1')} (Level-1 label alone) to "
        f"{u(R, 'regression_hc')} on RouterBench (unified run, section 5.3). Per-run bootstrap half-widths are about ±1.3 "
        "points on LLMRouterBench and ±0.8 on RouterBench, so the gains are real but the top of each table is a cluster: "
        "on LLMRouterBench no paired interval separates `handcrafted_nik`, `task_type_theme`, `handcrafted`, "
        "`regression_hc`, `combined` or `stats` from `handcrafted` (section 5.4).",
        f"2. **Where the learned embeddings help, it is with the handcrafted block as input, and only on RouterBench.** "
        f"`regression_hc` ({u(R, 'regression_hc')}) and `contrastive_hc` ({u(R, 'contrastive_hc')}) beat `handcrafted` "
        f"({u(R, 'handcrafted')}) by 0.5–0.6 points with the paired interval excluding zero on all three splits; plain "
        f"`regression` ({u(R, 'regression')}) is a smaller, unconfirmed gain. On LLMRouterBench the learned embeddings are "
        f"at or below the frozen input and the handcrafted block ({u(L, 'regression')} regression, {u(L, 'contrastive')} "
        "contrastive, the latter significantly worse on every split). Task-type recovery A(label)/A(learned) is 0.95–1.03 "
        "for every level: a one-hot label routes about as well as either learned embedding in the seen setting.",
        f"3. **The LLM task hierarchy does not beat the benchmark's own theme as a one-hot, and adds little inside the "
        f"handcrafted block.** Theme one-hot {u(L, 'task_type_theme')} / {u(R, 'task_type_theme')} against Level 1 + 2 "
        f"{u(L, 'task_type_L12')} / {u(R, 'task_type_L12')}; our `handcrafted` (L1 + L2 + 15 statistics) "
        f"{u(L, 'handcrafted')} / {u(R, 'handcrafted')} against Nikhilesh's (theme + 3 lengths) "
        f"{u(L, 'handcrafted_nik')} / {u(R, 'handcrafted_nik')}: both pairs are within one split sd. The query statistics "
        f"carry most of the signal (`stats` alone {u(L, 'stats')} / {u(R, 'stats')}); on RouterBench, where the themes are "
        "datasets, any label alone is 3.5–4.8 points behind the statistics because the 9.8k MMLU training queries span "
        "every domain and the label cannot separate easy from hard inside a dataset.",
        f"4. **With a new model, the representations that do not depend on the model scores hold up; the learned ones "
        f"collapse, and section 5.7 shows why.** At 500 probes on LLMRouterBench: `stats` {su(L, 'stats', 'gain_unseen_500')}, "
        f"`combined` {su(L, 'combined', 'gain_unseen_500')}, `handcrafted` {su(L, 'handcrafted', 'gain_unseen_500')}, `frozen` "
        f"{su(L, 'frozen', 'gain_unseen_500')} (recovery {rec(L, 'stats', 500)}–{rec(L, 'frozen', 500)} of the seen gain), against "
        f"`regression` {su(L, 'regression', 'gain_unseen_500')} and `contrastive` {su(L, 'contrastive', 'gain_unseen_500')}: worse "
        "than the single best. The cause is not the representation itself but the shared k: every statistics- or "
        "sentence-based representation selects k = 1000 on the validation split, and with k ≥ n probes the new model's "
        "estimate is one constant. In a space organized by quality, the pool models' estimates are low exactly on the "
        "hard queries, so the constant new-model estimate wins there and the router sends the hard queries to the "
        "expensive new model, which fails on them too. With k = 200 < 500 probes (Nikhilesh's grid) `regression` is as good "
        "as `frozen` on the same instances (section 5.7, +4.2% vs +4.1% and +3.6% vs +3.4%), not better; at 50 probes the "
        "same collapse appears for k = 200 in both grids. So the answer to \"are handcrafted features best on seen models "
        "and frozen embeddings best on new ones\" is: in the seen setting they tie on LLMRouterBench and the learned-with-"
        "handcrafted MLP leads on RouterBench; with a new model the frozen and handcrafted representations are robust and "
        "the learned ones are only as good as the harness lets the new model's estimate be local. The fix is a harness "
        "change (a separate, probe-bounded k for the new model), noted in HARNESS_NOTES.md.",
        f"5. **The learned embeddings are not \"just task type\"; they carry less of it than their frozen input.** Share of "
        f"a query's 10 nearest neighbours with the same Level-1 domain (section 5.5): frozen 81% / 87%, regression 66% / 78%, "
        "contrastive 54% / 78% (majority class 37% / 32%), against 100% for the label one-hots and 99.8% for `handcrafted`. "
        "Training on quality profiles moves queries by how the models behave on them, not by topic: the t-SNE of `frozen` "
        "shows topic clusters (code, math, trivia), that of `regression` a quality-ordered band with every domain spread "
        "along it. The `_hc` variants carry more task type (76–89%) because the handcrafted block is in their input, which is "
        "where their RouterBench gain comes from.",
        "6. **k is the sensitive hyperparameter, not λ.** Fixed k = 5 or 10 changes A by up to 0.1 (LLMRouterBench) and 0.3 "
        "(RouterBench); the λ grid changes it by less than 0.002 at the 95th percentile. The one-standard-error rule selects "
        "the top of the grid for every statistics- or sentence-based representation (1000 here, 200 in Nikhilesh's grid): "
        "the validation curve is flat, the router is a wide local average, and the cap of the grid decides the unseen "
        "numbers through observation 4. The seen gains move little between the two grids (frozen +4.9% at k = 200, +4.1% at "
        "k = 1000 on LLMRouterBench).",
        ""]
    return lines


def pending():
    return ["## 7. What is pending and how to reproduce", "",
        "Done: Nikhilesh's grid (`results_summary/`), the handcrafted runs (`alexandros-handcrafted/RESULTS.md`), the task "
        "labels (`preproc/data/<benchmark>/task_labels.parquet`), the unified comparison (`results_compare/`, SLURM job "
        "1159197, 6 h 42 min on one Vista GH200 node), its paired tests, views and k check (`analysis_compare/`).", "",
        "Open:", "",
        "1. A like-for-like rerun with Nikhilesh's k grid, so that the unseen numbers of all representations are on his "
        "protocol: `OUT=results_compare_k200 ANALYSIS=alexandros-handcrafted/analysis_compare_k200 "
        "EXTRA=\"--k-grid 5 10 20 50 100 200\" sbatch alexandros-handcrafted/sbatch/compare_vista.slurm` (the MLP "
        "checkpoints and sentence vectors are cached, so it is faster than the first run).",
        "2. The harness change that removes the artefact of observation 4: a probe-bounded k for the new model "
        "(e.g. k_new = min(k, n/2)), or k_new tuned on the probes. Proposed to Michal in HARNESS_NOTES.md.",
        "3. Rebuild: `python alexandros-handcrafted/build_report.py` then `python alexandros-handcrafted/report_html.py --out <file>`.", ""]


# ---------------------------------------------------------------- main

def build():
    facts = {}
    lines = ["# Query representations for LLM routing: methods, experiments and findings", "",
             f"_Built {date.today().isoformat()} at commit {git_commit()} by `alexandros-handcrafted/build_report.py`; "
             "every table is generated from the result files named in each section._", "",
             "## 1. In one paragraph", "",
             "We route each query to one of several LLMs with a k-nearest-neighbour estimate of every model's quality in a "
             "query representation, and ask which representation routes best: a task-type label, handcrafted query "
             "statistics, a frozen sentence embedding, their concatenation, or an embedding learned from the models' "
             "scores (by regression or contrastively). Two benchmarks (LLMRouterBench, RouterBench), three splits, a "
             "replayed release timeline for the unseen-model setting, 1,000-sample bootstrap intervals per run, paired "
             "intervals for differences between representations, and PCA/t-SNE views of every representation coloured "
             "by task type at three levels of granularity. Two pipelines were run: Nikhilesh's grid (section 5.1–5.2) and "
             "the unified comparison that puts every representation, including the LLM-assigned task hierarchy and the "
             "learned embeddings with the handcrafted block as input, on one protocol (5.3–5.7). The observations are in "
             "section 6.", ""]
    lines += data_section(facts)
    lines += methods_section()
    lines += ["## 4. Protocol summary", "",
              table([["seen (final pool)", "all models known on all training queries", "test queries of the split", "gain, A, 95% bootstrap"],
                     ["seen (instance pool)", "the models released before the event plus the new one, all known", "test queries", "the reference of recovery"],
                     ["unseen", "the new model known only from n probes (1 … 500), the embedding trained without it", "test queries", "gain, gain (same probes), recovery"]],
                    ["setting", "what the router knows", "evaluated on", "reported"]), "",
              "Seeds: 3 splits (0, 1, 2); 3 training seeds for the learned embeddings; 3 probe seeds (5 in the handcrafted-only "
              "runs). k grid 5 … 200 in Nikhilesh's grid, 5 … 1000 in the handcrafted and unified runs.", ""]
    lines += ["## 5. Results", "", "### 5.1 Seen setting", "", "**Nikhilesh's grid (theme label, his handcrafted features, frozen, combined, regression, contrastive)**", ""]
    lines += nik_seen(facts)
    lines += ["**Handcrafted variants with our task-type levels**", ""]
    lines += mine_seen(facts)
    for b in ("llmrouterbench", "routerbench"):
        if (NIK / f"{b}_seen.png").exists():
            lines += [f"![{b} seen]({rel(NIK / f'{b}_seen.png')})", ""]
    lines += ["### 5.2 Unseen setting (a new model with n probes)", ""]
    lines += nik_unseen(facts)
    lines += mine_unseen()
    lines += ["### 5.3 Unified comparison with our Level-1/Level-2 labels (all representations, same protocol)", ""]
    lines += unified_section(facts)
    lines += ["### 5.4 Paired comparisons", ""]
    lines += paired_section()
    lines += ["### 5.5 Embedding structure: PCA, t-SNE and label purity", ""]
    lines += views_section()
    lines += ["### 5.6 Task-type recovery, probes-to-target and sensitivity", ""]
    lines += nik_rq1a_ptt_sens()
    lines += ["### 5.7 One k for the pool and the new model: how the neighbourhood size interacts with the probe budget", ""]
    lines += k_check_section()
    lines += observations(facts)
    lines += pending()
    return "\n".join(lines), facts


def main(argv=None):
    global UNIFIED, CMP
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(HERE / "REPORT.md"))
    p.add_argument("--unified", default=str(UNIFIED), help="metrics.csv of the unified comparison")
    p.add_argument("--analysis", default=str(CMP), help="folder of the paired tests, views and k check")
    args = p.parse_args(argv)
    UNIFIED, CMP = Path(args.unified), Path(args.analysis)
    text, facts = build()
    Path(args.out).write_text(text)
    (Path(args.out).parent / "report_data.json").write_text(json.dumps(facts, indent=1, default=float))
    print(f"wrote {args.out} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
