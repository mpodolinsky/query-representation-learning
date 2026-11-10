# Handcrafted query representation (Alexandros)

Representation (i) of the proposal, and the task-type-only variant for RQ1a, for the kNN router in
[`../michal-harness/`](../michal-harness/README.md). Everything here is **frozen**: no model-dependent training,
so `fit(train_models)` ignores its argument and returns the same `embed`.

```
phi(x) = [ w_task * ( w_1 * onehot(L1 domain), w_2 * onehot(L2 subdomain), w_3 * onehot(L3 task) ),
           w_stats * zscore(statistics of the query text)   (optionally PCA-whitened) ]
```

Task type is a coarse-to-fine hierarchy (proposal, Figure 1): Level 1 domain (math, code, science, ...), Level 2
subdomain (linear algebra, algorithms, biology, ...), Level 3 specific task. Level 1 is read off a taxonomy table
keyed by the raw label Arman provides (the dataset name); Levels 2 and 3 come from an offline classification step
run separately and arrive as extra per-query columns. A level without labels is skipped, so everything works with
Level 1 alone until the finer labels exist.

## Files

| File | What |
|---|---|
| `handcrafted.py` | the features (`FEATURES`), the hierarchical one-hot block, the standardization and whitening, `HandcraftedEmbedding`, the `fit` factories and `VARIANTS` |
| `task_taxonomy.py` | raw task-type label (dataset name) -> Level-1 domain, for the 21 LLMRouterBench and 8 RouterBench datasets, MMLU subjects and MMLU-Pro categories; `report`, `todos` |
| `run_handcrafted.py` | the experiment loop (seen + unseen settings, all splits, both benchmarks) writing harness `results/` folders |
| `analyze_handcrafted.py` | tables and figures from the `results/*/results.csv` files |
| `test_handcrafted.py` | 33 tests on fake data, including the two scripts end to end (`python -m pytest -q` in this folder, about 10 s) |
| `HARNESS_NOTES.md` | proposed harness changes and interface questions for Michal and Arman |

## The features

Query statistics, computed from the query string only (`handcrafted.FEATURES`, one list, add a `Feature` to extend):

| Feature | Note |
|---|---|
| `n_tokens` | tokenizer count: tiktoken `cl100k_base` by default, `hf:<model>` possible, whitespace fallback if neither loads |
| `n_chars`, `n_words`, `n_sentences`, `n_lines` | counts |
| `n_question_marks` | count of `?` |
| `n_code_markers`, `has_code` | backticks, braces, brackets, `;`, `==`, `def`, `return`, `import`, `class`, `function`, `SELECT`, `#include`, ... |
| `digit_density`, `math_symbol_density`, `punct_density` | per character (`+ - * / = ^ < > %`, LaTeX markers, unicode math symbols) |
| `frac_uppercase` | upper-case letters over letters |
| `frac_non_ascii` | non-ASCII characters over characters |
| `avg_word_length` | characters per whitespace word |
| `chars_per_token` | how badly the text tokenizes (code and math tokenize into more, shorter tokens) |

Count features (`log=True` in the list) get `log1p` before standardization, since lengths are heavy-tailed.
Standardization is a z-score **fitted on `data.train` only**, applied to every query, clipped at ±5 standard
deviations. A constant feature stays at 0. The harness measures Euclidean distance, so without this one feature
would dominate every neighbor search (the harness notebook shows this).

**Whitening (`whiten=True`).** n_tokens, n_chars, n_words and chars_per_token are strongly correlated, so in the
Euclidean distance "length" counts several times. The whitened variants replace the z-scored block by its PCA
whitening fitted on the training split (identity covariance on train; components with zero variance are dropped).
`analyze_handcrafted.py --diagnostics` prints the correlated pairs and draws the correlation matrix.

## The task-type block

One one-hot block per level, categories = the labels present in the **training** split, an unknown category (or a
query without a label) = an all-zero row for that level. Where the labels of a level come from, in this order:

1. the `labels` argument (`{level: array aligned with data.queries}`), e.g. loaded from the classifier's CSV
   (`run_handcrafted.py --level-labels file.csv`);
2. a per-query column of the data: `task_level1`, `task_level2`, `task_level3` by default (`level_columns`);
3. for Level 1 only: the taxonomy (`task_taxonomy.level1_of`) applied to the raw label in `data.theme`;
4. Level 0 is the raw label itself (the dataset name), for comparison with the flat one-hot.

If the loader already provides a Level-1 column, the taxonomy is bypassed. Asking only for levels that have no
source raises `MissingLevels` (the run script skips such variants and says so).

**The taxonomy** (`task_taxonomy.py`) maps forgiving keys ("MMLU-Pro", "mmlu_pro", "MMLU Pro" are the same; split
suffixes like ".val.5" are ignored) to the fixed domain set `DOMAINS`: math, code, logic, science, engineering,
medicine, law, business, finance, humanities, social_science, knowledge, commonsense, affective,
instruction_following, conversation, tool_use, rag, other. Per-subject labels (`mmlu-astronomy`, `mmlu_pro_law`)
resolve through the MMLU subject and MMLU-Pro category maps. Unknown labels map to `other` with one warning listing
them; `python -c "import task_taxonomy; print(task_taxonomy.report(data.theme))"` (or `run_handcrafted.py
--dry-run`) prints the coverage of a real label column. Entries whose domain is a judgment call carry a `todo`
(`task_taxonomy.todos()`), see the list at the end.

**Relative weights.** `onehot_weight` multiplies the whole task-type block, `stats_weight` the numeric block, and
`level_weights` (`{1: w1, 2: w2, 3: w3}`, default equal) the levels inside the task-type block. The default
`onehot_weight="balanced"` scales the task-type block so that its total variance on the training queries equals that
of the numeric block, i.e. neither block dominates the squared distance by construction. Any float can be passed
instead. These are the main knobs of the representation (`--onehot-weight`, `--level-weights` in the run script).

## The variants (`handcrafted.VARIANTS`, the names written to `results.csv`)

| Name | Blocks | Role |
|---|---|---|
| `task_type_L1` | one-hot Level 1 (domain) | RQ1a per level |
| `task_type_L2` | one-hot Level 2 (subdomain) | RQ1a per level (needs the Level-2 labels) |
| `task_type_L3` | one-hot Level 3 (task) | RQ1a per level (needs the Level-3 labels) |
| `task_type_L12`, `task_type_L123` | one-hot of several levels side by side | RQ1a, coarse + fine |
| `task_type_raw` | one-hot of the raw label (dataset name) | the old flat one-hot, for comparison |
| `stats`, `stats_whitened` | the 15 statistics, z-scored / PCA-whitened | ablation: does the label add anything over the text statistics |
| `handcrafted_L1` | Level 1 + statistics | representation (i) with the coarse label only |
| `handcrafted` | all available levels + statistics | representation (i), the main one |
| `handcrafted_whitened` | all available levels + whitened statistics | representation (i), decorrelated numeric block |
| (iii) | `fit_concat(other_embed, data)`: any other embedding + the `handcrafted` block | one-liner once the sentence embedding exists |

The run script's default list is `task_type_L1 task_type_L2 task_type_L12 task_type_L123 stats handcrafted`; variants
whose levels have no labels are skipped automatically, so with Level 1 only it runs `task_type_L1 stats handcrafted`.
The factories behind the names: `fit_task_type_only(data, levels=(1,))`, `fit_stats_only(data, whiten=False)`,
`fit_handcrafted(data, levels=(1, 2, 3))`, and `fit_concat` / `fit_concat_factory` (the latter takes a `fit` factory,
for a learned embedding retrained per pool; `features_weight="balanced"` gives my block the same total training
variance as the other embedding).

Why the factories take `data`: the harness passes `embed` a plain list of query strings, so the task-type label
(which comes with the data, not from the text) is attached through a `query text -> theme` lookup built from
`data.theme`, and the scaler needs `data.train`. The rows for `data.queries` are precomputed once per split, so the
hundreds of `evaluate` calls of the unseen loop cost nothing in feature extraction. See `HARNESS_NOTES.md`, item 1,
for the interface change that would make this cleaner.

```python
import sys; sys.path += ["michal-harness", "alexandros-handcrafted"]
from router import Results
from handcrafted import fit_handcrafted, fit_task_type_only, fit_stats_only, fit_concat

out = Results(data, "llmrouterbench")
out.run("task_type_L1", fit_task_type_only(data, levels=(1,)), tune_k=True)
out.run("task_type_L12", fit_task_type_only(data, levels=(1, 2)), tune_k=True)
out.run("handcrafted", fit_handcrafted(data), tune_k=True)                      # all available levels + statistics
out.run("sentence+handcrafted", fit_concat(sentence_embed, data), tune_k=True)   # representation (iii)
```

## How to run (once Arman's loader exists)

Environment: the harness's (`numpy>=2`, `scikit-learn`, `matplotlib`, `pytest`) plus `pandas` (tables) and
`tiktoken` (token counts; optional, falls back to whitespace tokens with a warning). A venv with all of it is
`../.venv` (gitignored): `uv pip install --python .venv/bin/python "numpy>=2" scikit-learn matplotlib pytest pandas tiktoken`.

```bash
cd alexandros-handcrafted
python -m pytest -q                                                      # plumbing, fake data only

python run_handcrafted.py --dry-run                                      # loads the data, prints the plan, runs nothing
python run_handcrafted.py --benchmarks llmrouterbench --split-seeds 0    # main split first (development, plots)
python run_handcrafted.py                                                # both benchmarks, splits 0 1 2, all variants
python run_handcrafted.py --timeline replay                              # per-release-event pools and costs (see below)
python run_handcrafted.py --level-labels my_levels.csv                   # finer labels from the offline classifier (CSV)

python analyze_handcrafted.py --benchmark llmrouterbench                 # tables -> analysis/, figures -> analysis/figures/
python analyze_handcrafted.py --benchmark llmrouterbench --pca           # also the PCA views (loads the data)
python analyze_handcrafted.py --learned-name learned                     # RQ1a ratio once the learned rows exist
python analyze_handcrafted.py --diagnostics --loader <module>:load_data  # correlation matrix and whitening check of the stats block
```

Defaults of `run_handcrafted.py`: variants `task_type_L1 task_type_L2 task_type_L12 task_type_L123 stats handcrafted`
(the ones without labels are skipped); probe budgets `1 2 5 10 20 50 100 500`;
5 probe seeds; `tune_k=True` with the harness grid `5 10 20 50 100 200`; 1000 bootstrap resamples for seen runs
and 200 for unseen runs (`--n-boot`, `--n-boot-unseen`; `0` skips). The loader is found through `--loader
module:function` (or `path/to/file.py:function`), `$QRL_LOADER`, or a few default names (`data:load_data`,
`arman_data:load_data`, ...). A missing loader prints what was tried and how to point to it. `--dry-run` also prints,
per split, which levels have labels and the taxonomy coverage of the raw labels (unknown labels marked), which is
the first thing to look at when the data lands.

`--level-labels file.csv` loads the finer labels from the classifier's output when they are not yet in Arman's data:
a `query` column (the text) or an `index` column (position in `data.queries`), plus `task_level2` and/or
`task_level3` (and `task_level1` to override the taxonomy). Queries without a row get the category `unlabeled`.

**Two timeline modes.** `--timeline full-pool` (default, the README loop) keeps all models in the pool and holds
each model out in turn; one results folder per split. `--timeline replay` restricts the pool at release event `t`
to the models released up to `t` and uses that epoch's cost, one results folder per split and event with an
`epoch.json` (`epoch`, `pool`, `new_model`); the seen run is repeated per event because gains are only comparable
within an epoch. Events 0 and 1 are skipped (no pool to route among without the new model).

Cost: one `evaluate` with `tune_k=True` is a few seconds at full scale (the harness README estimates about 5 s of
routing per policy plus the bootstrap). The default unseen loop is `events x 3 variants x 8 budgets x 5 seeds`
runs per split, about 1300 for LLMRouterBench's 11 events; the feature extraction is cached, so the kNN and the
bootstrap are the whole cost. Reduce `--probe-seeds`, `--n-grid` or `--n-boot-unseen 0` for a first pass.

## What the analysis produces (`analysis/`)

- `seen_table.csv`, `seen_table.md`: gain and `A` per variant, mean ± std over split seeds (and per epoch in replay mode).
- `unseen_table.csv`: per variant, held-out model and `n`: gain, `gain_same_probes`, `recovery`, `A`, mean over
  probe seeds, then mean ± std over splits (the spread over seeds is kept in `*_std_seeds`).
- `A_unseen_curves.csv`: `A_unseen(n)` per variant, averaged over held-out models and splits (a summary; the harness
  README asks to report the events one by one, which `unseen_table.csv` does).
- `rq1a_ratio.csv`: `A(task_type_<levels>) / A(other)` per split, for every task-type-only variant (one row set per
  level combination) and every other embedding found in the results. The RQ1a rows are the ones against the learned
  embedding (`--learned-name`, default `learned`); until those rows exist the script says so and reports the ratios
  against `handcrafted` and `stats`. The seen and unseen tables are per embedding name, so per level combination too.
- with `--diagnostics` (loads the data): `stats_correlation_<bench>.csv/.png` (Pearson correlation of the z-scored
  statistics on the training split), the pairs with |r| >= 0.7 printed, the whitened block's off-diagonal check, and
  `stats_explained_variance_<bench>.png` (z-scored against whitened).
- `probes_to_target.csv`: smallest `n` with `A_unseen(n) >= 0.9 A_seen` (paper definition) and smallest `n` with
  `recovery >= 0.9` (the harness decision log prefers this one), per case and summarized (median, share of cases that
  reach the target within the grid).
- `figures/`: cost-quality curves of the seen runs (`plots.plot_curves`, rebuilt from the saved `runs/*.npz`),
  gain against probes per held-out model (`plots.plot_gain_vs_probes`), `A_unseen(n)` per variant, and with
  `--pca` the task-type panels, the per-model quality map and the explained-variance plot of the three variants.

## Open assumptions about Arman's data (checklist to verify when the data lands)

The code is written against the harness's `router.Data` stand-in. Check each item against `load_data`:

- [ ] `load_data(benchmark, split_seed=0)` exists, importable; `benchmark` is `"llmrouterbench"` / `"routerbench"`.
      Point `--loader` at it if the module is not one of the default names.
- [ ] It returns `router.Data` (or an object with the same fields): `queries: list[str]`, `models: list[str]`,
      `S: (Q, M)` scores in [0, 1], `cost: (M,)` mean cost per model, `train`/`val`/`test` index arrays,
      `theme`, `split_seed`.
- [ ] `theme` is filled: **one raw task-type label per query**, aligned with `queries`. Without it (and without a
      `task_level1` column) the task-type variants raise; `stats` still runs. If his field is called differently
      (`task_type`, `dataset`, `source`), set `data.theme = data.<field>` in a one-line adapter.
- [ ] **The exact label strings.** Level 1 is a lookup keyed by that string: ask for the list of distinct values
      (`sorted(set(data.theme))`) and run `task_taxonomy.report(data.theme)` (or `run_handcrafted.py --dry-run`).
      Every value must resolve to a domain other than `other`; add aliases to `task_taxonomy.TAXONOMY` for the rest.
      In particular: is MMLU one label or per subject (`mmlu-astronomy.val.5`?), does MMLU-Pro keep its category,
      does BBH keep its sub-task, what is the RouterBench RAG set called, and are split suffixes (`.val`, `.dev`)
      part of the string?
- [ ] **Finer levels.** If Arman's data carries a domain or subdomain already, the agreed column names must match
      `level_columns` (`task_level1`, `task_level2`, `task_level3`), or be passed through `level_columns=`. A
      loader-provided `task_level1` bypasses the taxonomy. Otherwise my classifier's CSV goes in through
      `--level-labels` and must use the same query text (or index) as `data.queries`.
- [ ] Query texts are **unique** (or duplicates share a label): my label lookup is by text (`HARNESS_NOTES.md`, item 1).
- [ ] `queries` are plain strings (not prompt dicts or message lists); if they are, the adapter should extract the user
      text, since the statistics are computed on it.
- [ ] `S` has no missing scores (`NaN`). The harness assumes every model on every query; if some are missing we
      need a rule (drop queries, or impute) before anything runs.
- [ ] `models` is in **release order**, or `Data` carries `release_order` (names, earliest first) or `release_date`
      (one per model). Otherwise the "each model in release order" loop is in `data.models` order.
- [ ] Cost per epoch: either one `cost` vector (used for every event) or `cost_by_epoch` of shape
      `(n_epochs, n_models)` with epoch `t` = the release of model `t`. `--timeline replay` uses it; `full-pool` does not.
- [ ] `split_seed` on the returned `Data` equals the requested seed (the results folder name uses it; the script warns).
- [ ] Splits are stratified by task type and the same for every embedding (harness decision), so every type appears
      in `train` and the one-hot has no all-zero rows in `test`.
- [ ] The language of the queries: `frac_non_ascii` and `frac_uppercase` assume mostly English text; fine either way,
      but a multilingual benchmark would make `frac_non_ascii` a language indicator rather than a style feature.

Design notes worth knowing when reading results: a task-type-only representation has only as many distinct points
as there are label combinations, so the kNN picks an arbitrary subset of same-label queries; the sensible `k` is
large (the per-label mean), and the harness warns when the tuned `k` hits the top of the grid (`HARNESS_NOTES.md`,
item 3). The coarser the level, the fewer the points and the stronger this effect.

## Incoming task labels from `../labeling/` (Levels 1-3 for every query)

The offline classification step now exists: [`../labeling/`](../labeling/README.md) labels every query of both
benchmarks with a local LLM (Qwen3-32B through vLLM, closed taxonomy in `labeling/taxonomy.py`, 11 domains x 90
subdomains plus a free-text Level 3). Its `merge_labels.py` writes `preproc/data/<benchmark>/task_labels.parquet`
with `query_id, level1, level2, level3, consistent`, in the row order of `queries.parquet` (= the query index).

How it plugs into this module, by column name (`handcrafted.DEFAULT_LEVEL_COLUMNS`):

| labels file | this module | note |
|---|---|---|
| `level1` | `task_level1` | a loader-provided Level 1 **bypasses** `task_taxonomy.level1_of(theme)`; the two domain sets differ (11 LLM domains vs the 19 in `task_taxonomy.DOMAINS`), so `task_type_L1` changes meaning once the labels are in |
| `level2` | `task_level2` | enables `task_type_L2`, `task_type_L12`, `task_type_L123`, the full `handcrafted` |
| `level3` | `task_level3` | free text, 2-5 words; high cardinality, for inspection and later clustering, use with care as a one-hot |
| `consistent` | (not used) | False when the model's Level 2 is not a subdomain of its Level 1; the labels keep the model's choice |

Two ways to get them in (to settle with Arman, see the questions in `labeling/README.md`):

1. the loader exposes them: `Data.task_level1/2/3` arrays aligned with `queries` (one `merge` on `query_id` in
   `preproc/data.py`, Arman's call), nothing changes here;
2. until then, `run_handcrafted.py --level-labels labels.csv` with an `index` column (row number in `queries.parquet`,
   which is the row order of `task_labels.parquet`) or a `query` column, plus `task_level1`, `task_level2`,
   `task_level3`:
   ```python
   import pandas as pd
   l = pd.read_parquet("preproc/data/llmrouterbench/task_labels.parquet").reset_index(names="index")
   l.rename(columns={"level1": "task_level1", "level2": "task_level2", "level3": "task_level3"}).to_csv("labels.csv", index=False)
   ```

Until `task_labels.parquet` exists the behavior is unchanged: Level 1 from the taxonomy table, Levels 2 and 3 skipped.

## Open TODOs in the taxonomy (`task_taxonomy.todos()`)

Domains that are a judgment call, to confirm before the final runs:

- **GPQA** -> `science` (authors: Knowledge). Graduate physics/chemistry/biology questions.
- **ARC Challenge** -> `science` (authors: Commonsense Reasoning). Grade-school science questions.
- **FinQA** -> `finance` (authors: Knowledge). Numerical reasoning over financial tables, also math-like.
- **HLE** -> `knowledge` (catch-all). Expert questions from every field; map its subject field if it is kept.
- **MMLU-Pro** -> `knowledge` without a category suffix, the MMLU-Pro category map with one.
- **MMLU** -> `knowledge` without a subject, the MMLU subject map with one; RouterBench stores it per subject.
- **BBH** -> `logic` (authors). 27 sub-tasks, some are language or math; a per-sub-task label would need its own map.
- **ArenaHard** -> `instruction_following` (authors). Could be merged with `conversation` (MT-Bench).
- **RAG** (RouterBench) -> `rag`. No formal name in the paper; the identifier string is unknown.
