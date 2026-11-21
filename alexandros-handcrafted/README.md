# Handcrafted query representation (Alexandros)

Representation (i) of the proposal, and the task-type-only variant for RQ1a, for the kNN router in
[`../michal-harness/`](../michal-harness/README.md). Everything here is **frozen**: no model-dependent training,
so `fit(train_models)` ignores its argument and returns the same `embed`.

```
phi(x) = [ w_task * ( w_1 * onehot(L1 domain), w_2 * onehot(L2 subdomain) ),
           w_stats * zscore(statistics of the query text)   (optionally PCA-whitened) ]
```

**Results and findings: [`RESULTS.md`](RESULTS.md).** The tables and figures it quotes are in [`analysis/`](analysis/).

Task type is a coarse-to-fine hierarchy (proposal, Figure 1): Level 1 domain (math, code, science, ...), Level 2
subdomain (linear algebra, algorithms, biology, ...), Level 3 specific task. Levels 1-3 come from the offline LLM
labeling in [`../labeling/`](../labeling/README.md) (`preproc/data/<benchmark>/task_labels.parquet`, read
automatically); without that file Level 1 is read off a taxonomy table keyed by the raw label Arman provides (the
dataset name) and the finer levels are skipped. The main representation uses Levels 1 and 2. Level 3 is free text
with thousands of categories (6,200 on LLMRouterBench, 11,400 on RouterBench), nearly one per query, so its one-hot
is kept as a named ablation (`handcrafted_L123`), not in the default.

## Files

| File | What |
|---|---|
| `handcrafted.py` | the features (`FEATURES`), the hierarchical one-hot block, the standardization and whitening, the within-category block, `HandcraftedEmbedding`, the `fit` factories, `VARIANTS`, the default k grid |
| `task_taxonomy.py` | raw task-type label (dataset name) -> Level-1 domain, for the 21 LLMRouterBench and 8 RouterBench datasets, MMLU subjects and MMLU-Pro categories; `report`, `todos` |
| `run_handcrafted.py` | the experiment loop (seen + unseen settings, all splits, both benchmarks) writing harness `results/` folders plus `k_tuning.csv` |
| `analyze_handcrafted.py` | tables, figures and diagnostics from the `results/*/results.csv` files |
| `test_handcrafted.py` | 39 tests on fake data, including the two scripts end to end (`python -m pytest -q` in this folder, about 15 s) |
| `RESULTS.md` | the final tables and the findings, in plain sentences |
| `HARNESS_NOTES.md` | proposed harness changes and interface questions for Michal and Arman |
| `compare_representations.py` | **the unified comparison**: every representation of the project (ours, Nikhilesh's frozen / regression / contrastive, the concatenations, the MLP on [sentence, handcrafted]) on his protocol with our Level-1/2 labels; resumable; exports embeddings |
| `embedding_views.py` | PCA and t-SNE small multiples of any representation by theme / Level 1 / Level 2, plus kNN label purity, linear-probe accuracy and silhouette ("is it just task type?") |
| `paired_tests.py` | paired bootstrap over the test queries of the *difference* between two representations (interval, p-value), per split and summarized across splits |
| `build_report.py` | assembles `REPORT.md` from Nikhilesh's `results_summary/`, `analysis/`, `analysis_compare/` and `results_compare/` |
| `test_compare.py` | 6 tests of the four scripts above on fake data with a stub sentence encoder (needs torch) |
| `run_compare_all.sh`, `sbatch/` | launch the unified comparison (six detached processes, or the Vista SLURM job), create the environment, download the encoder |
| `REPORT.md` | the generated report (methods, data, results, observations, what is pending) |

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

**The within-category block (`within_level`).** A one-hot of one level (0 = the raw theme) with a weight so large
(`within_weight`, default 100) that two queries of different categories are always farther apart than any two of
the same category (the statistics block is clipped at ±5 over 15 dimensions, so two queries of one category are at
most 39 apart; two categories are 141 apart). The harness's Euclidean kNN then stays inside the query's own
category as long as the category has neighbors left, and only then spills over, ordered by the other blocks.
`stats_within_theme` is the statistics block with this restriction on the theme: compared with `task_type_raw`
(the per-theme mean) it says whether the statistics carry signal *inside* a task type.

## The variants (`handcrafted.VARIANTS`, the names written to `results.csv`)

| Name | Blocks | Role |
|---|---|---|
| `task_type_raw` | one-hot of the raw label (dataset name, `data.theme`) | the proposal's flat one-hot; the baseline of RQ1a |
| `task_type_L1` | one-hot Level 1 (domain) | RQ1a per level |
| `task_type_L2` | one-hot Level 2 (subdomain) | RQ1a per level (needs the Level-2 labels) |
| `task_type_L3` | one-hot Level 3 (task) | not in the default: free text, thousands of categories |
| `task_type_L12` | one-hot Levels 1 and 2 side by side | RQ1a, coarse + fine |
| `task_type_L123` | one-hot Levels 1, 2 and 3 | ablation: the free-text Level 3 as a one-hot |
| `stats`, `stats_whitened` | the 15 statistics, z-scored / PCA-whitened | ablation: does the label add anything over the text statistics; the whitened block counts length once |
| `stats_within_theme` | the 15 statistics, kNN restricted to the query's theme | do the statistics add signal beyond the task type |
| `handcrafted_L1` | Level 1 + statistics | representation (i) with the coarse label only |
| `handcrafted` | Levels 1 + 2 + statistics | **representation (i), the main one** |
| `handcrafted_L123` | Levels 1 + 2 + 3 + statistics | ablation: + the free-text Level 3 |
| `handcrafted_whitened` | Levels 1 + 2 + whitened statistics | representation (i), decorrelated numeric block |
| (iii) | `fit_concat(other_embed, data)`: any other embedding + the `handcrafted` block | one-liner once the sentence embedding exists |

The run script's default seen-setting list (`handcrafted.DEFAULT_VARIANTS`) is every row above except
`task_type_L3`; variants whose levels have no labels are skipped automatically. The unseen loop (8 budgets x 5 seeds
per held-out model) runs `handcrafted` only by default (`DEFAULT_UNSEEN_VARIANTS`, `--unseen-variants ... | all`).
The factories behind the names: `fit_task_type_only(data, levels=(1,))`, `fit_stats_only(data, whiten=False)`,
`fit_stats_within(data, level=0)`, `fit_handcrafted(data, levels=(1, 2))`, and `fit_concat` / `fit_concat_factory`
(the latter takes a `fit` factory, for a learned embedding retrained per pool; `features_weight="balanced"` gives my
block the same total training variance as the other embedding).

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
out.run("handcrafted", fit_handcrafted(data), tune_k=True)                      # Levels 1 + 2 + statistics
out.run("sentence+handcrafted", fit_concat(sentence_embed, data), tune_k=True)   # representation (iii)
```

## How to run

Environment: the harness's (`numpy>=2`, `scikit-learn`, `matplotlib`, `pytest`) plus `pandas` and `pyarrow` (the
loader, the labels, the tables) and `tiktoken` (token counts; optional, falls back to whitespace tokens with a
warning). `../.venv` (gitignored) is an aarch64 build for Vista; on Lonestar6 (x86, no `lahf_lm`, so NumPy must be
2.2) a micromamba env does it: `micromamba create -p $SCRATCH/qrl_env/env -c conda-forge python=3.11 "numpy=2.2"
scikit-learn pandas pyarrow matplotlib pytest tiktoken`, and run its python with `-s` (a stray `~/.local` pandas).

```bash
cd alexandros-handcrafted
python -m pytest -q                                                      # plumbing, fake data only

python run_handcrafted.py --dry-run                                      # loads the data, prints the plan, runs nothing
python run_handcrafted.py --benchmarks llmrouterbench --split-seeds 0    # main split first (development, plots)
python run_handcrafted.py                                                # both benchmarks, splits 0 1 2, all variants
python run_handcrafted.py --skip-unseen                                  # the seen setting only (minutes per split)
python run_handcrafted.py --unseen-variants handcrafted stats            # more variants in the unseen loop ('all' for every one)
python run_handcrafted.py --timeline replay                              # per-release-event pools and costs (see below)

python analyze_handcrafted.py                                            # tables -> analysis/, figures -> analysis/figures/
python analyze_handcrafted.py --pca --diagnostics                        # + PCA views, correlation / whitening / label-prediction diagnostics
python analyze_handcrafted.py --learned-name learned                     # RQ1a ratio once the learned rows exist
```

Defaults of `run_handcrafted.py`: variants `DEFAULT_VARIANTS` (see the table; the ones without labels are skipped),
unseen loop for `handcrafted` only; probe budgets `1 2 5 10 20 50 100 500`; 5 probe seeds; `tune_k=True` on the
grid `5 10 20 50 100 200 300 500 1000` (`handcrafted.DEFAULT_K_GRID`; the harness's own grid stops at 200, where
every variant landed in the first runs); 1000 bootstrap resamples for seen runs and 200 for unseen runs (`--n-boot`,
`--n-boot-unseen`; `0` skips). The loader is found through `--loader module:function` (or
`path/to/file.py:function`), `$QRL_LOADER`, or a few default names, `preproc.data:load_data` (Arman's) first. A
missing loader prints what was tried and how to point to it. `--dry-run` also prints, per split, which levels have
labels and the taxonomy coverage of the raw labels (unknown labels marked).

**k tuning.** `select_k` depends on the embedding, the pool and `data.val` only, never on the probes, so in the
unseen loop the script tunes once per (variant, held-out model) and passes the k to every budget x seed run (same
numbers as tuning inside each run, 40 times cheaper; `HARNESS_NOTES.md`, 6). `k_tuning.csv` next to `results.csv`
records, per run, the k, the grid, how it was obtained, and two edge flags: `best_k_at_edge` (the harness's own
warning: the best validation k was the grid's first or last value) and `selected_k_at_edge` (the one-standard-error
choice is). The analysis marks such embeddings with † in `seen_table.md` and summarizes them in `k_tuning_summary.csv`.

**Task labels.** `--level-labels auto` (default) reads `preproc/data/<benchmark>/task_labels.parquet` (written by
`labeling/merge_labels.py`: `query_id, level1, level2, level3`) and matches it on `data.query_ids`; when the file is
missing, Level 1 comes from the taxonomy and Levels 2-3 are skipped. `none` ignores the file. A `.parquet` or a CSV
path can be given instead: the CSV has a `query` column (the text) or an `index` column (position in
`data.queries`), plus `task_level1/2/3`. Queries without a row get the category `unlabeled`.

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

- `seen_table.csv`, `seen_table.md`: gain, `A` and the tuned `k` per variant, mean ± std over split seeds (and per
  epoch in replay mode); `k_per_split` lists the k of every split and † marks a variant whose k hit the edge of
  the grid on any split. `k_tuning_summary.csv` has the same per setting (seen / unseen) with the share of runs at
  the edge.
- `unseen_table.csv`: per variant, held-out model and `n`: gain, `gain_same_probes`, `recovery`, `A`, mean over
  probe seeds, then mean ± std over splits (the spread over seeds is kept in `*_std_seeds`).
- `A_unseen_curves.csv`: gain(n), recovery(n) and `A_unseen(n)` per variant, averaged over held-out models and
  splits (a summary; the harness README asks to report the events one by one, which `unseen_table.csv` does).
- `rq1a_ratio.csv`: `A(task_type_<levels>) / A(other)` per split, for every task-type-only variant (one row set per
  level combination) and every other embedding found in the results. The RQ1a rows are the ones against the learned
  embedding (`--learned-name`, default `learned`); until those rows exist the script says so and reports the ratios
  against the other embeddings. The seen and unseen tables are per embedding name, so per level combination too.
- `probes_to_target.csv`: per case (variant, held-out model, split) and summarized (median, share of cases that
  reach the target within the grid), the smallest `n` with **`recovery >= 0.9`** (`median_n_recovery`,
  `share_reached_recovery`: the headline, as the harness decision log prefers). The paper's wording, the smallest
  `n` with `A_unseen(n) >= 0.9 A_seen`, is also there (`median_n_A`, `share_reached_A`) but it is **vacuous on these
  benchmarks**: the single best model alone has `A_single_best / A_seen` ≈ 0.96 (`single_best_ratio`), above the 0.9
  target, so even `n = 1` "reaches the target" whatever the router does with the probes. `A_target_vacuous` says
  when that is the case; use the recovery definition then (it measures the part of the gain that routing adds).
- with `--diagnostics` (loads the data): `stats_correlation_<bench>.csv/.png` (Pearson correlation of the z-scored
  statistics on the training split), the pairs with |r| >= 0.7 printed, the whitened block's off-diagonal check,
  `stats_explained_variance_<bench>.png` (z-scored against whitened), and **how well the 15 statistics predict the
  label**: `stats_predict_labels.csv` (per benchmark and target, theme and Level 1: majority-class test accuracy,
  logistic-regression train and test accuracy, 50-NN test accuracy) with the row-normalized confusion matrices
  `stats_predict_<target>_<bench>.csv` and heatmaps in `figures/`. Read next to `stats_within_theme`: the
  classifier says how much of the task type the statistics already encode; the within-theme variant says whether
  they carry anything beyond it.
- `figures/`: cost-quality curves of the seen runs (`plots.plot_curves`, rebuilt from the saved `runs/*.npz`),
  gain against probes per held-out model (`plots.plot_gain_vs_probes`), **gain against probes per variant**
  (`gain_vs_probes_by_variant_<bench>_epoch-1.png`: one panel per variant with unseen runs, one thin line per
  held-out model, the mean in bold, the seen gain dashed, and the region where the router does worse than the
  single best shaded), `A_unseen(n)` per variant, and with `--pca` the task-type panels, the per-model quality map
  and the explained-variance plot of the three variants.

## The unified comparison (all representations, our labels)

Nikhilesh's grid (`results_summary/`) uses the benchmark theme as the task type and his own three-statistic
handcrafted block. `compare_representations.py` reruns his protocol (final pool + every release instance, probe
budgets 1 … 500, three probe seeds, three training seeds, k tuned on the validation split, 1,000 bootstrap resamples)
with every representation side by side: `task_type_theme`, `task_type_L1`, `task_type_L2`, `task_type_L12`, `stats`,
`handcrafted`, `handcrafted_nik`, `frozen`, `combined` (frozen + ours), `regression`, `contrastive`, and
`regression_hc` / `contrastive_hc` (his MLP trained on [sentence vector, our handcrafted block]). It writes the
harness's own results folders plus one flat `results_compare/metrics.csv` in his column layout, and exports the
final-pool embedding of every representation for the views. It needs torch and the sentence encoder
(`learned/requirements.txt`; `sbatch/setup_env.sh`, `sbatch/download_encoder.sh`), or `--encoder stub` for a dry run.

```bash
python compare_representations.py --encode-only                         # cache the sentence vectors (GPU: --device cuda)
PY=$SCRATCH/envs/qrl/bin/python THREADS=8 bash run_compare_all.sh        # six processes; resumable; logs in results_compare/logs
python compare_representations.py --dry-run --encoder stub               # how many shards are done
python embedding_views.py                                                # PCA / t-SNE / label purity of the exported embeddings
python paired_tests.py --compare-root ../results_compare --reference handcrafted --n-probes 5 50 500
python build_report.py                                                   # REPORT.md
```

`paired_tests.py --results-root ../results` and `embedding_views.py --from-variants stats handcrafted ...` work on the
handcrafted-only runs without the encoder.

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
large (the per-label mean), which is why the default grid goes to 1000 and why `seen_table.md` flags a `k` at the
edge of it (`HARNESS_NOTES.md`, item 3). The coarser the level, the fewer the points and the stronger this effect.

## The task labels from `../labeling/` (Levels 1-3 for every query)

[`../labeling/`](../labeling/README.md) labels every query of both benchmarks with a local LLM (Qwen3-32B through
vLLM, closed taxonomy in `labeling/taxonomy.py`, 11 domains x 90 subdomains plus a free-text Level 3). Its
`merge_labels.py` writes `preproc/data/<benchmark>/task_labels.parquet` with `query_id, level1, level2, level3,
consistent` (committed), which `run_handcrafted.py --level-labels auto` reads and matches on `data.query_ids`.

How the columns map onto the levels (`handcrafted.DEFAULT_LEVEL_COLUMNS`):

| labels file | this module | note |
|---|---|---|
| `level1` | `task_level1` | a provided Level 1 **bypasses** `task_taxonomy.level1_of(theme)`; the two domain sets differ (11 LLM domains vs the 19 in `task_taxonomy.DOMAINS`), so `task_type_L1` means the LLM's domain once the labels are in, and `task_type_raw` is the dataset name |
| `level2` | `task_level2` | enables `task_type_L2`, `task_type_L12`, the main `handcrafted` |
| `level3` | `task_level3` | free text, 2-5 words; 6,200 / 11,400 distinct values, so only the `_L123` ablations use it |
| `consistent` | (not used) | False when the model's Level 2 is not a subdomain of its Level 1; the labels keep the model's choice |

If Arman's loader ever exposes `Data.task_level1/2/3` itself (one `merge` on `query_id` in `preproc/data.py`), the
columns take precedence over the file and nothing changes here. Without the file the behavior is the old one: Level 1
from the taxonomy table, Levels 2 and 3 skipped.

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
