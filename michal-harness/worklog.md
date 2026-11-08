# Worklog

Append an entry after every commit: date, short commit message, and what changed.

Format: `- YYYY-MM-DD — <commit message>: <what changed>`

- 2026-11-08 — Add router and evaluation harness (phase 1): `router.py` with kNN estimator, routing, λ sweep, single-best baseline, oracle, log-cost area, gain over the single best, and `evaluate` for the seen and unseen settings; 12 synthetic-data tests; `walkthrough.ipynb`; `decision.md`. Probes-to-target left as a TODO.
- 2026-11-08 — Add bootstrap interval and k tuning to the harness: `evaluate` returns `gain_ci` (paired bootstrap over test queries) and takes `tune_k` (one-standard-error rule on the validation split, per embedding, seen pool only, warning when the best k is at the grid edge); `Data.val` split reserved for tuning; 21 tests; notebook sections for both and a plot after tuning, with the unseen section on the tuned k; `decision.md` records the rules (validation split off-limits to embedding training, Alexandros carves his own early-stopping set).
- 2026-11-08 — Add results writer, shared plots and PCA views: `Results` saves each run to a timestamped gitignored folder (`results.csv`, per-run `.npz` with curves, test q̂ and probes, split, meta; q̂ in float64 because routing ties break differently in float32); `plots.py` with one style and all figures (cost-quality curves, curves for several k, gain against probes, PCA views of task type, mean score per model, routing map, explained variance, probes, and one query with its neighbors); `knn_indices` split out of `knn_estimate`; `Data.theme`; `evaluate` also returns probes, cost range, q̂ and mean qualities; 33 tests; notebook sections for saving results and PCA; λ and k sensitivity check marked optional in `decision.md`.

## 2026-11-08 — Decision note: area definition and gain (not tied to a commit)

Questions went through one by one. Seven decisions, all recorded in `decision.md` ("Area `A` and the gain"); the code was changed to match them.

1. **Integration range and what a curve does outside its points: accepted.** The range is `[cheapest, most expensive]` model cost of the routing pool. A curve that ends early (or starts late) is extended flat, because it cannot get better quality for more budget. Chosen because it is neutral and easy to explain.
2. **Tie-breaking: accepted, ties go to the cheaper model for every policy.** Ties are common because `q̂` is a multiple of `1/k` for 0/1 scores. Before, `argmax` took the first model in `data.models` order, which could bias the results (order may track release date or price) and made the oracle at small λ pick the first correct model, not the cheapest. Now ties are detected within 1e-9 (float rounding must not decide them) and go to the cheapest model; the result no longer depends on model order. Tests added.
3. **Oracle: accepted, unchanged.** It routes by the observed (noisy) test scores, as the paper defines it. It is unattainable and only affects the secondary number `A`, not the headline gain.
4. **λ grid: decided, `λ = 0` plus 500 log-spaced values** (was 100). Declared a design decision, not a derived value, and made the hyperparameter `n_lambdas` of `evaluate` (default 500; also stored in `results.csv`) so the optional sensitivity check can vary it. Cost at full scale (80k test queries, 33 models): about 5 s of routing per policy, about 20 s for 1000 bootstrap resamples, about 2 GB peak memory. The test suite is slower (about 7 s instead of 2 s); the slowest test loop uses `n_lambdas=100`.
5. **Curve construction: accepted.** Monotone envelope (best quality within a budget) with linear interpolation in cost between operating points. A noisy router is not penalized for wiggles that cost nothing, since it could always spend less.
6. **Units of the gain: accepted.** The relative gain stays the main number, `gain_abs` is reported alongside: `(area_router − area_single_best) / log(c_hi / c_lo)`, the difference in mean score averaged over the price range. For example on the synthetic data at `k = 10`: +3.0% relative is +0.016 in mean score. `gain_abs` is in `evaluate`'s result, in `results.csv`, and in the notebook. It has no bootstrap interval (only the relative gain does).
7. **Comparability: accepted.** Compare gains only within one benchmark and release epoch, because the cost range depends on the model set. Seen and unseen runs of the same epoch share the pool (including the new model), so their ranges match. This feeds the open probes-to-target question.

Also decided in the same session: the log-cost axis and the relative-gain definition (earlier, see `decision.md`), and that the λ and `k` sensitivity check stays optional (it should vary `n_lambdas`, the λ range and `k`).

Effect on the synthetic example: numbers barely moved (for `k = 3, 10, 50, 300` the gains are still about −4%, +3%, +9%, +11%), so the notebook text still holds. 34 tests pass; the notebook was rerun. Not committed yet.

## 2026-11-08 — Decision note: unseen-setting baseline and what is reported (not tied to a commit)

Discussed which single best to compare with in the unseen setting. Key point: the 2×2 of {single best, router} × {full information about the new model, only `n` probes}. The router with full information is the seen-model result (the ceiling); the router with `n` probes is the unseen result; comparing the two is the probes question. The router may legitimately never pick the new model (a much worse and more expensive model is never the argmax).

Decided: report three numbers for every unseen run, implemented in `evaluate` and `Results`:
1. **`gain`**: router over the **full-information single best** (knows every model's quality, the new one included, from all training queries). Fixed baseline, independent of `n_probes` and the probe seed, identical in the seen and unseen runs of an epoch. Main number, and the one the bootstrap interval is for. Chosen so the curve against `n` reflects only the router.
2. **`gain_same_probes`**: router over the single best that knows the new model only from the same `n` probes (secondary, more realistic, noisier). New curve `single_best_probes` (dashed in the plots).
3. **`recovery`**: `gain_unseen / gain_seen` over the same fixed baseline, the fraction of the seen-model gain recovered with `n` probes (`nan` if the seen gain is not positive). `recovery()` in `router.py`; `Results` fills it for an unseen run when a seen run of the same embedding name was run first.

Also noted: for learned embeddings the seen-to-unseen gap at `n` = all training queries is the representation transfer loss, the rest is the probe budget loss. Recovery is only informative when the full-information router uses the new model (optional diagnostic: share of test queries routed to it).

Probes-to-target moved to optional; with `recovery` in place it is a small addition (the smallest `n` whose recovery reaches a target such as 90%).

Result on the synthetic example (k tuned, 5 probe draws per point): the gain over the fixed baseline rises with the probe budget, about +3% with 1 to 2 probes, +8% with 500, +11% (the seen-model gain) with all training queries, so recovery goes from about 27% to 100%. The same-probes gain is larger at small `n` because that baseline is weaker there. Code: `results.csv` gets `gain_same_probes` and `recovery`; the npz files get `q_mean_probes`; `plot_gain_vs_probes` takes the second line. 38 tests pass, the notebook was rerun (section 7 rewritten). Not committed yet.
- 2026-11-08 — Implement the area definition and unseen-setting reporting: ties go to the cheaper model (within 1e-9, independent of model order); `n_lambdas = 500` hyperparameter of `evaluate`; `gain_abs` alongside the relative gain; unseen runs report `gain` over the fixed full-information single best, `gain_same_probes` and `recovery` (also in `results.csv` and the run files, plus the dashed `single_best_probes` curve in the plots); notebook section 7 rewritten; 38 tests; `decision.md` updated, probes-to-target and the λ/k sensitivity check optional. Rationale in the two decision notes above.
