# Decisions

Michal's component (paper §7.2): router and evaluation harness. Decisions made 2026-11-08.
Items marked **[team]** affect other components and need sign-off from the owner named.

## Code style and layout

- Concise, readable, clean code. Keep the number of files to a minimum.
- `router.py`: kNN estimator, routing, single-best baseline, λ sweep, area `A`, gain, `evaluate`. (Probes-to-target is optional.)
- `plots.py`: one shared style and all figures: cost-quality curves, gain against probes, the PCA views, probes, neighbors (see the Plots section).
- `test_router.py`: sanity tests on synthetic data (oracle gives `A = 1`, perfect `q̂` matches the oracle).
- Data loading belongs to Arman; embeddings belong to Nikhilesh and Alexandros.

## Router

- Estimator: kNN average of observed scores among the `k` nearest labeled queries, per model (paper Eq. 2).
- Each model has its own estimate `q̂_m(x)`: one embedding space, but neighbors are searched only among the queries that model has labels for.
  Models sharing the same labeled set share one neighbor search (same result, cheaper): `knn_estimate(E_labeled, S_labeled, E_query, k)` with one score column per model.
  `evaluate` calls it once for the pool and once for the new model `m'` on its probes.
- Neighbor search: scikit-learn `NearestNeighbors` (installed in the project `.venv`, together with pytest).
- Routing rule: `argmax_m q̂_m(x) − λ·c_t(m)` (paper Eq. 1).
  - Ties (equal `q̂ − λ·c`) go to the cheaper model. See the area section.
- Distance: **Euclidean (L2)**, `d(x, y) = ‖x − y‖₂`.
  - It preserves the scale information of each feature, which matters for the standardized handcrafted features (the paper standardizes them so no single feature dominates the distance).
  - It behaves better on concatenated vectors (handcrafted + sentence embedding). Cosine ignores magnitude and mixes the two parts awkwardly.
  - Each embedding owns its scaling. Sentence embeddings are L2-normalized inside the embedding, where Euclidean and cosine give the same neighbor ranking.
  - Rejected: cosine (discards scale), Mahalanobis (noisy covariance estimate in high dimensions, more code).
- Few labels: a model with fewer than `k` labels (`n_probes` < k) uses `min(k, n_probes)` neighbors.
- **`k` tuning (implemented, `evaluate(..., tune_k=True)`):**
  - Tuned **per embedding**, on the validation split only, so each embedding is compared at its own best `k` with the same procedure. The objective an embedding was trained with changes its geometry and therefore its best `k`.
  - Metric: the router's area on the validation queries, over the pool models. Grid `(5, 10, 20, 50, 100, 200)`.
  - **One-standard-error rule:** pick the largest `k` (the smoothest estimate) whose area is within one bootstrap standard error (200 resamples of the validation queries) of the best `k`.
  - Seen pool only. In the unseen setting `k` is tuned on the pool without `m'`, with the embedding retrained without `m'`, and `m'`'s labels are never used (they are what the probe budget limits).
  - Not k-fold cross-validation: a learned embedding has seen its training queries, so tuning on them would be optimistic, and refitting it per fold is too expensive.
  - Grid-edge warning: if the best `k` (the argmax, before the 1-SE rule) is the smallest or largest value of the grid, `select_k` prints a warning, because the grid may be too narrow. Extend the grid and rerun.

## Cost **[team: Arman]**

- `c_t(m)` is a per-model scalar: the mean per-query cost at the epoch's price, not the per-query cost in the data table.
- Reason: in practice we don't know how many tokens a model will produce for a specific query, so the router can't use per-query cost.
- **Missing implementation:** depends on Arman's format. We need him to provide, or let us derive, the mean cost per query for each model and epoch.

## Area `A` and the gain (all decided 2026-11-08)

The paper fixes: `A` is the area under the cost-quality curve traced by sweeping λ, divided by the oracle's area. The remaining choices:

1. **Cost axis: log.** Prices span more than 10×, and a linear axis gives the expensive end most of the weight. The curve is linear in cost between operating points (mixing two routers is achievable by randomizing), and the area is integrated over `log(cost)`.
2. **Integration range: `[cheapest, most expensive]` model cost of the routing pool.** A curve that ends before the end of the range (or starts after its start) is extended flat: it cannot get better quality for more budget. This is neutral and easy to explain.
3. **Ties go to the cheaper model**, for every policy (router, single best, oracle). Ties are common because `q̂` is a multiple of `1/k` for 0/1 scores. Ties are detected within 1e-9, so float rounding does not decide them. The result no longer depends on the order of `data.models`.
4. **λ grid: `λ = 0` plus 500 log-spaced values**, scaled so that `λ·(cost range)` spans `1e-3 … 1e3`. 500 is a design decision, not a derived value. It is the hyperparameter `n_lambdas` of `evaluate` (default 500) so the optional sensitivity check can vary it.
5. **Curve: monotone envelope** (best quality within a budget) with linear interpolation between operating points. A noisy router is not penalized for wiggles that cost nothing in practice, since it could always spend less.
6. **Oracle: routes by the observed (noisy) test scores**, `argmax_m s_m(x) − λ·c(m)`, as the paper defines it ("best model per query"). It is unattainable. It only affects the secondary number `A`, not the headline gain.
7. **Comparability: only within one benchmark and release epoch.** The cost range depends on the model set, so gains from different epochs are not on the same axis. Seen and unseen runs of the same epoch share the pool (including the new model), so their ranges match.

Y-axis: mean observed test score of the routed models. X-axis: realized mean cost per query, using the per-model mean cost.

Cost of this setup at full scale (80k test queries, 33 models, 500 λ): about 5 s of routing per policy, about 20 s for 1000 bootstrap resamples, about 2 GB peak memory.

## Baselines and the unseen-setting reporting (decided 2026-11-08)

- Single best model: for each λ, the fixed model with the highest mean `q_m − λ·c_t(m)` on training queries.
- **Main baseline, in both settings: the full-information single best.** It knows every model's quality, the new model included, from all training queries. It is fixed, so it does not change with `n_probes`, and the seen and unseen runs of the same epoch share it exactly.
  Reason: the curve against `n` should reflect the router only. A baseline that moves with the probe draw mixes router quality with baseline noise.
- A 2×2 view: {single best, router} × {full information, `n` probes}. The router with full information is the seen-model result (the ceiling), and the router with `n` probes is the unseen result.
- **Three numbers are reported for every unseen run:**
  1. `gain`: the router over the full-information single best (main).
  2. `gain_same_probes`: the router over the single best that knows the new model only from the same `n` probes (secondary, more realistic but noisier; larger at small `n` because that baseline is weaker). Its curve is `single_best_probes`.
  3. `recovery`: `gain_unseen / gain_seen`, both over the same full-information single best, i.e. the fraction of the seen-model gain recovered with `n` probes. `nan` if the seen gain is not positive. In `Results`, an unseen run gets its recovery against the seen run of the same embedding name, so run the seen setting first.
- The router can legitimately ignore the new model (a much worse and more expensive model is never the argmax), and then nothing changes with `n`. Recovery is only informative when the full-information router uses the new model. A diagnostic for that (the share of test queries routed to the new model) is optional.
- For learned embeddings the seen-to-unseen gap at `n` equal to all training queries is the **representation transfer** loss (the embedding has not seen the new model), and the rest is the **probe budget** loss. For frozen embeddings the first is zero.

## Interface `evaluate(data, fit, ...)` **[team: all]**

- `data` is a `Data` container (queries, models, scores `S`, mean costs, train/val/test indices, optional `theme`) in `router.py`. It is a stand-in for Arman's table until his schema is fixed.

- `fit` is a factory `fit(train_models) -> embed_fn`, with `embed_fn(list[str]) -> ndarray`.
  Frozen embeddings ignore the `train_models` argument. Learned `φ_θ` retrains without `m'` for each leave-model-out run.
  `evaluate` calls `fit` once per run with the pool minus the held-out model.
- The setting is passed as plain arguments, not an object: `evaluate(fit, new_model=None, n_probes=None, seed=0)`.
  `new_model=None` is the seen-model setting. Otherwise it is the unseen setting with `n_probes` probes.
- Full signature: `evaluate(data, fit, new_model=None, n_probes=None, seed=0, k=10, tune_k=False, k_grid=(5, 10, 20, 50, 100, 200), n_boot=1000, n_lambdas=500)`. It returns `gain`, `gain_same_probes` (unseen only), `gain_abs`, `gain_ci`, `A`, `A_single_best`, `k` (the one used), the λ grid, the three curves (router, single best, oracle), the test `Q_hat`, `q_mean` (full-information baseline), `q_mean_probes` (unseen only), the `probes` (query indices, None in the seen setting) and the `cost_range`. `n_boot=0` skips the bootstrap. `tune_k=True` ignores `k`.
- Splits and probe sets come from Arman's output. **Stand-in:** probes are currently drawn by a seeded random sampler inside `evaluate`, to be replaced by his probe sets.
- `Data` has a `train`, a `val` and a `test` index set. The validation split comes from Arman's output.

## Results format **[team: all]** (implemented: `Results` in `router.py`)

- Every experiment writes into its own folder `results/YYYY-MM-DD_HH-MM-SS/`. These folders are **gitignored** (`results/` in `.gitignore`), so outputs are kept locally for reuse and never committed.
- Contents:
  - `results.csv`: one row per run (one per seed), columns
    `run, benchmark, embedding, new_model, n_probes, seed, tune_k, k, n_lambdas, gain, gain_abs, gain_same_probes, recovery, gain_ci_low, gain_ci_high, A, A_single_best`.
    `new_model` and `n_probes` are empty for the seen setting, and the interval is empty if the bootstrap was skipped (`n_boot=0`).
  - `runs/NNNN.npz`: per run, the λ grid, the three cost-quality curves (router, single best, oracle), the test `q̂` (float64) and the mean qualities used by the single best.
  - `split.npz`: the train/val/test indices. `meta.json`: creation time, benchmark, git commit (`-dirty` if uncommitted changes), model names and mean costs.
- Reuse: with `q̂`, the test scores and the costs, the routing, curves, area and gain can be recomputed (a test checks this reproduces the saved curves exactly) without refitting an embedding or rerunning the kNN. This matters because the area definition may be revisited in the sensitivity check.
- `seed` covers the probe draw and, for learned embeddings, the training seed. The bootstrap interval is per row.
- Report the mean gain over seeds, the spread across seeds, and the bootstrap interval, kept separate (a two-stage bootstrap is optional).
- `plots.py` functions take arrays and `evaluate` results. Plotting straight from a saved results folder is not implemented yet.

## Plots (`plots.py`)

- One style for every figure. Categorical colors: scatter plots keep to three, because more cannot be validated for all pairs. Group plots are therefore **small multiples** (one panel per group, the group in blue over all points in gray).
- k is shown with an ordinal blue ramp (light to dark, up to 4 values); the selected k is thicker.
- **PCA views** (`pca_project` fits two axes on the training queries; axis labels give the variance share): groups by task type, mean score of each model in hexagonal bins, the model the router picks at one λ, cumulative explained variance (illustrates why raw features would dominate Euclidean distance), the probes of the new model, and one query with its neighbors.
- **Neighbor plot:** the pool models' neighbors are the `k` nearest training queries. The new model's are the `k` nearest of its probes. Neighbors are computed in the full space, so they can look far apart in 2D. The plot carries that note.
- Requires `Data.theme` (task type per query) for the theme plot; it comes from Arman's data (the synthetic data uses the cluster).
- For large data the gray background of a scatter is a fixed random subset of at most 20,000 points.
- PCA is linear and keeps two directions. A non-linear projection (UMAP, t-SNE) is a possible later addition.

## Metrics

- **Reporting (decided 2026-11-08):** the main number is the gain of the router over the single-best baseline. `A` (area relative to the oracle) is reported in parentheses as the secondary metric.
  - Reason: the oracle sees the realized (noisy) outcomes, so it is not attainable. The single best is the bar to beat. Beating it means the embedding captures what each model is good at, beyond the global price-quality trade-off.
  - No "true q" ceiling in the synthetic example, since real data has none.
  - **Gain formula (decided):** `gain = area_router / area_single_best − 1`, a direct comparison with the single best that does not involve the oracle. Reported as a relative area gain, with `A` in parentheses, for example "+2.1% (A = 0.611 vs 0.598)".
  - **`gain_abs` is reported alongside:** `(area_router − area_single_best) / log(c_hi / c_lo)`, the difference in mean score averaged over the price range (log-cost). Easier to interpret and independent of the baseline level, whereas the relative gain is better for comparing across benchmarks. It has no bootstrap interval, only the relative gain does.
  - **Uncertainty (implemented):** `gain_ci` is a paired percentile bootstrap interval over the test queries. 1000 resamples with replacement, the same resample for the router and the single best, 95% level, seeded by `seed`.
    The router is not retrained or re-run: each query's routed model and score are fixed, and only the averages are recomputed.
    Checked once on synthetic data (25 independent test sets): bootstrap standard error 1.98% against a real spread of 1.91%, and 92% of the 95% intervals contained the large-sample gain.
  - **Probes-to-target: optional (moved 2026-11-08).** Not implemented. 90% of the seen-model `A` is already reached with 2 probes on the synthetic data, so the paper's definition is uninformative as written and needs redefining, probably on the gain.
- Seen-model `A` (RQ1) and `A_unseen(n)` (RQ2).
- Probes-to-target (paper): smallest `n` with `A_unseen(n) ≥ 0.9 · A_seen`. **Optional**, not implemented; see the Optional section.
- Task-type recovery ratio `A_task / A_learned` is computed by Nikhilesh using our `evaluate`.

## Warnings

- **The validation split is only for tuning `k` [team: Alexandros, Arman].** Embedding training must never see it, early stopping included. Alexandros carves his own early-stopping set out of the training split. Otherwise the embedding is selected on the queries we tune `k` on, and the tuning becomes optimistic for the learned embedding only. Arman provides the `val` split.

- **The train/test split is FIXED.** We use one split (Arman's). The bootstrap interval only measures test-set sampling noise, and seeds only measure probe and training randomness.
  Variation from re-splitting the data is **not** measured, so a small gain on this split may not hold on another. Add several splits if time allows.
- **Held-out models are separate experiments,** not repeats. The 11 (LLMRouterBench) and 6 (RouterBench) release events are reported one by one. A mean across them is only a summary.

## Optional (decided 2026-11-08)

- **Probes-to-target:** the smallest probe budget `n` that recovers a fixed fraction of the seen-model result. The paper's definition (90% of the seen-model `A`) is uninformative on our data (2 probes already reach it), so it would be redefined on the recovery: the smallest `n` whose recovery reaches a target (e.g. 90%). The baseline question is decided, so this is now a small addition on top of `recovery`.
- **Sensitivity of the gain and `A` to the λ grid and to `k`:** optional, do if time allows. Not required for the main results. The λ-grid density is the `n_lambdas` hyperparameter of `evaluate` (default 500, a design decision to be evaluated here); also vary the λ range and `k`.

## Open

- Data schema is not published yet (Arman). The repo has no commits. Nothing here is final until the schema lands.
