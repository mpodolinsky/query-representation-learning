# Worklog

Append an entry after every commit: date, short commit message, and what changed.

Format: `- YYYY-MM-DD — <commit message>: <what changed>`

- 2026-11-08 — Add router and evaluation harness (phase 1): `router.py` with kNN estimator, routing, λ sweep, single-best baseline, oracle, log-cost area, gain over the single best, and `evaluate` for the seen and unseen settings; 12 synthetic-data tests; `walkthrough.ipynb`; `decision.md`. Probes-to-target left as a TODO.
- 2026-11-08 — Add bootstrap interval and k tuning to the harness: `evaluate` returns `gain_ci` (paired bootstrap over test queries) and takes `tune_k` (one-standard-error rule on the validation split, per embedding, seen pool only, warning when the best k is at the grid edge); `Data.val` split reserved for tuning; 21 tests; notebook sections for both and a plot after tuning, with the unseen section on the tuned k; `decision.md` records the rules (validation split off-limits to embedding training, Alexandros carves his own early-stopping set).
