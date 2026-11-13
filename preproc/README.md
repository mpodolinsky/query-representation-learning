# Data and timeline replay

Arman's component. It turns LLMRouterBench and RouterBench into one score matrix per benchmark (every model on
every query, in [0, 1]), with costs, task-type labels, release epochs, unseen-model instances, train/val/test splits
and a probe sampler, in the form Michal's harness (`michal-harness/router.py`) takes.

## Quick start

```python
from preproc.data import load_data, unseen_instances, sample_probes

d = load_data("llmrouterbench", split_seed=0)              # final pool, all 13 models
d = load_data("llmrouterbench", split_seed=0, epoch=4)     # seen-model setting at release epoch 4
d = load_data("routerbench", split_seed=1, instance=6)     # unseen instance 6: gpt-4-1106-preview joins 7 incumbents
evaluate(d, fit, new_model=d.new_model, n_probes=20, seed=0)  # the harness, unchanged
```

`d` is a `Data` (`preproc/data.py`): `queries`, `models`, `S` (Q × M scores), `cost` (M mean costs), `train`, `val`,
`test`, `theme`, `split_seed`, plus `benchmark`, `query_ids`, `subtask`, `epoch` and `new_model`.
`load_data(..., text="prompt")` returns the full prompts instead of the bare questions.

Run the tests from the repo root with `python -m pytest preproc`. They need numpy ≥ 2 for the harness test:

```bash
python3 -m venv .venv && .venv/bin/pip install "numpy>=2" pandas pyarrow scikit-learn pytest
.venv/bin/python -m pytest preproc michal-harness
```

## What is in `data/<benchmark>/`

| File | Content |
|---|---|
| `queries.parquet` | `query_id`, `theme`, `subtask`, `query` (bare question), `prompt` (as sent to the models), `n_chars`. Row order = query index. |
| `scores.parquet` | **The (query, model, score, cost) table**: `query_id`, `model`, `score` ∈ [0, 1], `cost` (USD), `cost_imputed`. |
| `models.csv` | `model`, `display_name`, `release`, `epoch`, `price_in_per_1m`, `price_out_per_1m`, `mean_cost`, `mean_score`, `n_cost_imputed`. |
| `epochs.csv` | One row per release event: `epoch`, `date`, `new_models`, `pool` (`;`-separated). |
| `epoch_costs.csv` | Mean cost per query of each model at each epoch (blank = not released yet). |
| `instances.csv` | Unseen-model instances: `instance`, `epoch`, `date`, `new_model`, `pool`. |
| `splits/seed{0,1,2}.npz` | `train`, `val`, `test` query indices. |

`reports/build_report.md` has the counts, coverage, cost audit, per-theme scores, epochs, instances and probe coverage.

**Setup.** `deps/LLMRouterBench` and `deps/routerbench` are Git submodules (Arman's forks, over SSH, so you need a
GitHub SSH key): clone with `git clone --recurse-submodules`, or run `git submodule update --init` in an existing
clone. To change the benchmark code, commit and push inside the submodule first, then commit the updated submodule
in this repo (`git add deps/LLMRouterBench`); pushing only the parent leaves teammates with a commit they cannot
fetch. `git submodule update --remote` moves both to their fork's `main`. If you had `prepoc/v0.0` checked out before
the switch to submodules, move `deps/LLMRouterBench/results/` aside before `git submodule update --init` (it fails on a
non-empty folder) and move it back afterwards.

To rebuild everything: `python preproc/build.py` (about 10 s). It needs the LLMRouterBench bundle extracted to
`deps/LLMRouterBench/results/bench-release/` ([Hugging Face](https://huggingface.co/datasets/NPULH/LLMRouterBench),
`bench-release.tar.gz`) and `routerbench_0shot.pkl` in the folder above the repo (or pass `--llmrb-dir` and
`--routerbench-pkl`). It downloads two small metadata files into `preproc/raw/` (gitignored) and checks them against
the Git LFS pointers in `deps/` (with `git-lfs` installed, the submodule already holds them and nothing is downloaded).

## Decisions (2026-11-09)

**Benchmarks.**
- *LLMRouterBench*: the 13 flagship models (Table 1) on the 9 datasets where all 13 have results: AIME, ARC-AGI v1,
  ArenaHard, GPQA, HLE, LiveCodeBench, LiveMathBench, MMLU-Pro (`test_3000`), SimpleQA. **12,068 queries × 13
  models.** SWE-Bench (no qwen3-thinking results) and τ²-Bench (no gpt-5-chat results) are dropped rather than
  imputed. This is not the LLMRouterBench paper's 10-dataset cost setting: ARC-AGI is in, SWE-Bench and τ²-Bench are out.
- *RouterBench*: the 0-shot file. **36,478 queries × 11 models**, after dropping 16 duplicate prompts (a copy in
  train and one in test would be a distance-0 neighbor) and the 3 `test-match` sanity prompts.
- Scores are already in [0, 1] in both benchmarks, so "normalize per benchmark" is a check, not a transformation.
  ArenaHard (LLM judge) and RouterBench's GSM8K, MT-Bench and consensus_summary have non-binary scores.

**Query text.** `query` is the bare question (LLMRouterBench `origin_query`; the question part of RouterBench's
prompt, the first turn for MT-Bench). `prompt` is the full text sent to the models. The full prompts carry
dataset-specific templates (MMLU-Pro's even names the subject), which would let any text embedding recover the task
type trivially, so `query` is the default. **Exception:** ARC-AGI's `origin_query` is only a task id, so its `query`
is the full prompt, template included.

**Task type.** `theme` is the source dataset (LLMRouterBench, 9) or the eval family (RouterBench, 12: the 57 MMLU
subjects collapsed to `mmlu`, the Chinese tasks to `chinese`, the three MT-Bench sets to `mtbench`). Splits are
stratified on it, and it is the harness's `Data.theme`. `subtask` is the finest label available: the MMLU-Pro subject
(14), the HLE category (8), the ArenaHard subcategory (coding, math, creative writing), the RouterBench `eval_name`,
and otherwise the theme.

**Cost.** `c_t(m)` is a per-model scalar, the mean per-query cost over all queries (the harness's definition). Prices
are fixed, so it does not change across epochs; epochs only decide which models are in the pool. Price changes over
time are out of scope.
- *LLMRouterBench*: per-query cost = `prompt_tokens × input price + completion_tokens × output price` with Table 1
  prices, not the recorded `cost`. The recorded cost is 0 on 532 records that do have tokens, and Qwen3's differs
  from Table 1 (tiered pricing). 1,879 records (1.2%; 1,408 of them qwen3-thinking) have no token counts at all; their cost is
  the model's mean cost on the same dataset, flagged by `cost_imputed`.
- *RouterBench*: the recorded `total_cost` (there are no token counts). The prices in `models.csv` are those in
  `deps/routerbench/routers/common.py` as that code applies them, for information only.

**Release epochs and unseen instances.** The replay is the timeline of pools: there is no query stream, and queries
carry no timestamps (the paper assumes a fixed query distribution). One unseen instance per model released after the
first event. Its pool is every model released strictly before that event, plus the new model. Models released the
same day are left out, since they have no labels yet either. That gives **11 events and 12 instances (LLMRouterBench)**
and **6 events and 9 instances (RouterBench)**. The first event is the initial pool. Early instances are thin: for
Claude-Sonnet-4 (instance 0) the only incumbent is DeepSeek-V3, so a learned φ sees a one-model quality profile.

**Splits.** 70/10/20 train/val/test, random at the query level, stratified by theme, seeds 0, 1 and 2, saved to
disk so everyone uses identical indices. A split seed gives the same split at every epoch and instance.

**Probes.** `sample_probes(train, n, seed)` is the harness's rule (the first `n` of
`default_rng(seed).permutation(len(train))`, as query indices). Probes are nested across budgets and are the same for
every embedding and every instance. With `theme=d.theme`, the sampler is proportional stratified and still nested:
the theme mix stays within about one query of proportional (random drifts by up to 20 at n = 1000), but a theme
smaller than 1/n of train can still be missed. No probe lists are written to disk; the report compares both samplers.

## Data caveats

- **RouterBench GSM8K scores are not accuracy.** They take the values {0, 0.25, 0.5, 0.75, 1}, mostly 0.75 and 0.25,
  and gpt-4-1106-preview averages 0.66. GSM8K is 20% of RouterBench, so check results with and without it.
- **RouterBench MMLU**: llama-2-70b-chat (0.03) and code-llama-34b (0.00) score near zero, likely an answer-parsing
  artifact of the benchmark. Kept as published.
- **LLMRouterBench empty outputs**: 2,636 records have no output, mostly reasoning models hitting their token limit
  (GLM-4.6 at 65,536 tokens, Intern-S1 at about 20K). They were billed, and scored as the benchmark scored them
  (almost all 0). Only 8 are API failures ("failed to generate").

## Corrections for the proposal

- "400K+ query instances … each answered by 33 models" is not what we replay: the replay is about **12K queries ×
  13 models** (the 400K counts query–model pairs over both LLMRouterBench settings).
- **WizardLM-13B-V1.2 was released in July 2023, not September** (Hugging Face `createdAt` 2023-07-25). RouterBench
  still has 6 events.
- "queries arrive in time order" does not apply to the offline design; the replay is the pool timeline only.

## Harness changes requested (Michal)

Not made here, for Michal to review:
1. Replace the stand-in `Data` dataclass in `router.py` with `from preproc.data import Data`. Field order and
   defaults match, so the 41 tests should still pass.
2. Replace the inline probe draw with `sample_probes`. The current code:
   ```python
   probes = np.random.default_rng(seed).permutation(len(tr))[:n_probes]
   probe_ids = tr[probes]
   ```
   becomes `probe_ids = sample_probes(tr, n_probes, seed)`, using `data.S[probe_ids]` where `S_tr[probes]` was used.
   The result is identical (`test_harness_runs_on_load_data` checks it), and a stratified option becomes one argument.
3. Put the repo root on the path for the import: a `sys.path` line in `router.py`, or a minimal `pyproject.toml` and
   `pip install -e .`.

Until then, `load_data` already works with `evaluate`, because the harness only reads attributes from `Data`.
