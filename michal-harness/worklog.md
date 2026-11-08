# Worklog

Append an entry after every commit: date, short commit message, and what changed.

Format: `- YYYY-MM-DD — <commit message>: <what changed>`

- 2026-11-08 — Add router and evaluation harness (phase 1): `router.py` with kNN estimator, routing, λ sweep, single-best baseline, oracle, log-cost area, gain over the single best, and `evaluate` for the seen and unseen settings; 12 synthetic-data tests; `walkthrough.ipynb`; `decision.md`. Probes-to-target left as a TODO.
- 2026-11-08 — Add bootstrap interval and k tuning to the harness: `evaluate` returns `gain_ci` (paired bootstrap over test queries) and takes `tune_k` (one-standard-error rule on the validation split, per embedding, seen pool only, warning when the best k is at the grid edge); `Data.val` split reserved for tuning; 21 tests; notebook sections for both and a plot after tuning, with the unseen section on the tuned k; `decision.md` records the rules (validation split off-limits to embedding training, Alexandros carves his own early-stopping set).
- 2026-11-08 — Add results writer, shared plots and PCA views: `Results` saves each run to a timestamped gitignored folder (`results.csv`, per-run `.npz` with curves, test q̂ and probes, split, meta; q̂ in float64 because routing ties break differently in float32); `plots.py` with one style and all figures (cost-quality curves, curves for several k, gain against probes, PCA views of task type, mean score per model, routing map, explained variance, probes, and one query with its neighbors); `knn_indices` split out of `knn_estimate`; `Data.theme`; `evaluate` also returns probes, cost range, q̂ and mean qualities; 33 tests; notebook sections for saving results and PCA; λ and k sensitivity check marked optional in `decision.md`.
