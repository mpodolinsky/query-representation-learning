# Handcrafted query representation (Alexandros)

Representation (i) of the proposal, and the task-type-only variant for RQ1a, for the kNN router in
[`../michal-harness/`](../michal-harness/README.md). Everything here is **frozen**: no model-dependent training,
so `fit(train_models)` ignores its argument and returns the same `embed`.

```
phi(x) = [ w_onehot * onehot(task type of x) ,  w_stats * zscore(statistics of the query text) ]
```

## Files

| File | What |
|---|---|
| `handcrafted.py` | the features (`FEATURES`), the one-hot encoder, the standardization, `HandcraftedEmbedding`, and the `fit` factories |
| `run_handcrafted.py` | the experiment loop (seen + unseen settings, all splits, both benchmarks) writing harness `results/` folders |
| `analyze_handcrafted.py` | tables and figures from the `results/*/results.csv` files |
| `test_handcrafted.py` | 18 tests on fake data, including the two scripts end to end (`python -m pytest -q` in this folder, about 5 s) |
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

The task-type block is a one-hot over the task types present in the **training** split (`data.theme`); a type
never seen in training is an all-zero row.

**Relative weight of the two blocks.** `onehot_weight` multiplies the one-hot block, `stats_weight` the numeric
block. The default `onehot_weight="balanced"` scales the one-hot block so that its total variance on the training
queries equals that of the numeric block, i.e. neither block dominates the squared distance by construction. Any
float can be passed instead (e.g. `3.0` makes two queries of different type at least 3·√2 apart). This weight is
the main knob of the representation; it is a CLI argument of the run script (`--onehot-weight`).

## The variants (`handcrafted.VARIANTS`, the names written to `results.csv`)

| Name | Factory | Blocks | Role |
|---|---|---|---|
| `task_type` | `fit_task_type_only(data)` | one-hot only | RQ1a: how much the task-type label alone captures |
| `stats` | `fit_stats_only(data)` | statistics only | ablation: does the label add anything over the text statistics |
| `handcrafted` | `fit_handcrafted(data)` | both | representation (i) |
| (iii) | `fit_concat(other_embed, data)` | any other embedding + the `handcrafted` block | one-liner once the sentence embedding exists |

`fit_concat` takes a frozen `embed(list[str]) -> ndarray`; `fit_concat_factory` takes a `fit` factory instead
(for a learned embedding retrained per pool). `features_weight="balanced"` gives my block the same total training
variance as the other embedding; pass a float to set it by hand.

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
out.run("task_type", fit_task_type_only(data), tune_k=True)
out.run("handcrafted", fit_handcrafted(data), tune_k=True)
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

python analyze_handcrafted.py --benchmark llmrouterbench                 # tables -> analysis/, figures -> analysis/figures/
python analyze_handcrafted.py --benchmark llmrouterbench --pca           # also the PCA views (loads the data)
python analyze_handcrafted.py --learned-name learned                     # RQ1a ratio once the learned rows exist
```

Defaults of `run_handcrafted.py`: variants `task_type stats handcrafted`; probe budgets `1 2 5 10 20 50 100 500`;
5 probe seeds; `tune_k=True` with the harness grid `5 10 20 50 100 200`; 1000 bootstrap resamples for seen runs
and 200 for unseen runs (`--n-boot`, `--n-boot-unseen`; `0` skips). The loader is found through `--loader
module:function` (or `path/to/file.py:function`), `$QRL_LOADER`, or a few default names (`data:load_data`,
`arman_data:load_data`, ...). A missing loader prints what was tried and how to point to it.

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
- `rq1a_ratio.csv`: `A(task_type) / A(other)` per split, for every other embedding found in the results. The RQ1a row
  is the one against the learned embedding (`--learned-name`, default `learned`); until those rows exist the script
  says so and reports the ratios against `handcrafted` and `stats`.
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
- [ ] `theme` is filled: **one task-type label per query**, aligned with `queries`. Without it the `task_type` and
      `handcrafted` variants raise; `stats` still runs. If his field is called differently (`task_type`, `category`,
      `domain`), set `data.theme = data.<field>` in a one-line adapter.
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

Design notes worth knowing when reading results: the `task_type` representation has only as many distinct points
as there are types, so the kNN picks an arbitrary subset of same-type queries; the sensible `k` is large (the per-type
mean), and the harness warns when the tuned `k` hits the top of the grid (`HARNESS_NOTES.md`, item 3).
