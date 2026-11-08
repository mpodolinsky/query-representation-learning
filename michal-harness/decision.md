# Decisions

Michal's component (paper §7.2): router and evaluation harness. Decisions made 2026-11-08.
Items marked **[team]** affect other components and need sign-off from the owner named.

## Code style and layout

- Concise, readable, clean code. Keep the number of files to a minimum.
- `router.py`: kNN estimator, routing, single-best baseline, λ sweep, area `A`, gain, `evaluate`. (Probes-to-target is a TODO.)
- `plots.py`: shared figure style and plot functions.
- `test_router.py`: sanity tests on synthetic data (oracle gives `A = 1`, perfect `q̂` matches the oracle).
- Data loading belongs to Arman; embeddings belong to Nikhilesh and Alexandros.

## Router

- Estimator: kNN average of observed scores among the `k` nearest labeled queries, per model (paper Eq. 2).
- Each model has its own estimate `q̂_m(x)`: one embedding space, but neighbors are searched only among the queries that model has labels for.
  Models sharing the same labeled set share one neighbor search (same result, cheaper): `knn_estimate(E_labeled, S_labeled, E_query, k)` with one score column per model.
  `evaluate` calls it once for the pool and once for the new model `m'` on its probes.
- Neighbor search: scikit-learn `NearestNeighbors` (installed in the project `.venv`, together with pytest).
- Routing rule: `argmax_m q̂_m(x) − λ·c_t(m)` (paper Eq. 1).
- Distance: **Euclidean (L2)**, `d(x, y) = ‖x − y‖₂`.
  - It preserves the scale information of each feature, which matters for the standardized handcrafted features (the paper standardizes them so no single feature dominates the distance).
  - It behaves better on concatenated vectors (handcrafted + sentence embedding). Cosine ignores magnitude and mixes the two parts awkwardly.
  - Each embedding owns its scaling. Sentence embeddings are L2-normalized inside the embedding, where Euclidean and cosine give the same neighbor ranking.
  - Rejected: cosine (discards scale), Mahalanobis (noisy covariance estimate in high dimensions, more code).
- Few labels: a model with fewer than `k` labels (`n_probes` < k) uses `min(k, n_probes)` neighbors.
- `k` is tuned on a validation split, possibly separately for seen and unseen settings.

## Cost **[team: Arman]**

- `c_t(m)` is a per-model scalar: the mean per-query cost at the epoch's price, not the per-query cost in the data table.
- Reason: in practice we don't know how many tokens a model will produce for a specific query, so the router can't use per-query cost.
- **Missing implementation:** depends on Arman's format. We need him to provide, or let us derive, the mean cost per query for each model and epoch.

## Area `A`

- Fixed by the paper: `A` is the area under the cost-quality curve traced by sweeping λ, divided by the oracle's area.
- **Cost axis: log (decided 2026-11-08).** Prices span more than 10×, and a linear axis would give the expensive end most of the weight. On a log axis each price decade weighs the same.
  The curve is linear in cost between operating points (mixing two routers is achievable by randomizing), and the area is integrated over `log(cost)`.
- Other choices (provisional, not yet discussed in detail):
  - Y-axis is mean observed quality on the test queries. The curve is made monotone (best quality within a budget).
  - Integration range is `[min cost, max cost]` of the routing pool.
  - Oracle routes by the observed test scores: `argmax_m s_m(x) − λ·c(m)`.
  - λ grid: `0` plus 100 log-spaced values scaled so that `λ·(cost range)` spans `1e-3 … 1e3`.

## Baselines

- Single best model: for each λ, the fixed model with the highest mean `q_m − λ·c_t(m)` on training queries.
- It is also run in the unseen setting, so `A_unseen` has a comparison point.

## Interface `evaluate(data, fit, ...)` **[team: all]**

- `data` is a `Data` container (queries, models, scores `S`, mean costs, train/test indices) in `router.py`. It is a stand-in for Arman's table until his schema is fixed.

- `fit` is a factory `fit(train_models) -> embed_fn`, with `embed_fn(list[str]) -> ndarray`.
  Frozen embeddings ignore the `train_models` argument. Learned `φ_θ` retrains without `m'` for each leave-model-out run.
  `evaluate` calls `fit` once per run with the pool minus the held-out model.
- The setting is passed as plain arguments, not an object: `evaluate(fit, new_model=None, n_probes=None, seed=0)`.
  `new_model=None` is the seen-model setting. Otherwise it is the unseen setting with `n_probes` probes.
- Full signature: `evaluate(data, fit, new_model=None, n_probes=None, seed=0, k=10)`. It returns `gain`, `A`, `A_single_best`, the λ grid and the three curves (router, single best, oracle).
- Splits and probe sets come from Arman's output. **Stand-in:** probes are currently drawn by a seeded random sampler inside `evaluate`, to be replaced by his probe sets.
- Not implemented yet: validation split for tuning `k` (phase 3).

## Results format **[team: all]**

- One tidy CSV with one row per run (one per seed) and columns
  `benchmark, embedding, new_model, n_probes, seed, k, gain, A, A_single_best, gain_ci_low, gain_ci_high`.
- `seed` covers the probe draw and, for learned embeddings, the training seed. The bootstrap interval is per row.
- Report the mean gain over seeds, the spread across seeds, and the bootstrap interval, kept separate (a two-stage bootstrap is optional).
- Sweep curves are saved alongside, so `plots.py` only reads these files.

## Metrics

- **Reporting (decided 2026-11-08):** the main number is the gain of the router over the single-best baseline. `A` (area relative to the oracle) is reported in parentheses as the secondary metric.
  - Reason: the oracle sees the realized (noisy) outcomes, so it is not attainable. The single best is the bar to beat. Beating it means the embedding captures what each model is good at, beyond the global price-quality trade-off.
  - No "true q" ceiling in the synthetic example, since real data has none.
  - **Gain formula (decided):** `gain = area_router / area_single_best − 1`, a direct comparison with the single best that does not involve the oracle. Reported as a relative area gain, with `A` in parentheses, for example "+2.1% (A = 0.611 vs 0.598)".
  - **Uncertainty:** a bootstrap confidence interval over the test queries is planned (not implemented yet).
  - **TODO: probes-to-target.** Postponed. 90% of the seen-model `A` is already reached with 2 probes on the synthetic data, so the paper's definition is uninformative as written and needs redefining, probably on the gain.
    To decide with it: the single-best baseline in the unseen setting (currently estimated from the same `n` probes, which makes the unseen gain larger than the seen gain at small `n`).
- Seen-model `A` (RQ1) and `A_unseen(n)` (RQ2).
- Probes-to-target (paper): smallest `n` with `A_unseen(n) ≥ 0.9 · A_seen`. **TODO**, see above; not implemented.
- Task-type recovery ratio `A_task / A_learned` is computed by Nikhilesh using our `evaluate`.

## Warnings

- **The train/test split is FIXED.** We use one split (Arman's). The bootstrap interval only measures test-set sampling noise, and seeds only measure probe and training randomness.
  Variation from re-splitting the data is **not** measured, so a small gain on this split may not hold on another. Add several splits if time allows.
- **Held-out models are separate experiments,** not repeats. The 11 (LLMRouterBench) and 6 (RouterBench) release events are reported one by one. A mean across them is only a summary.

## Open

- Data schema is not published yet (Arman). The repo has no commits. Nothing here is final until the schema lands.
