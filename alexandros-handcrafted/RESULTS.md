# Handcrafted query features: results

Runs of 2026-11-16 at commit `cde8206` (`results/2026-11-16_22-49-5*_split{0,1,2}` = LLMRouterBench,
`results/2026-11-16_22-51-5*_split{0,1,2}` = RouterBench; every `meta.json` records the clean commit). Tables and
figures: [`analysis/`](analysis/), produced by `analyze_handcrafted.py --pca --diagnostics`. The earlier runs with
`handcrafted` = L1+L2+L3 and a k grid capped at 200 are in `results/archive_2026-11-15_L123-handcrafted_k200/`.

Setup: Michal's kNN router (`michal-harness/router.py`), 3 train/val/test splits per benchmark, k tuned on the
validation split by the harness's one-standard-error rule over the grid 5 … 1000. `gain` is the relative gain of the
router's area A over the full-information single best. The seen setting uses all models; the unseen setting holds
each model out in turn, reveals it through n probe queries (5 probe seeds) and reports the gain over the same single
best, plus `recovery` = unseen gain / seen gain of the same embedding and split.

The variants: `task_type_raw` = one-hot of the benchmark's own `theme` (spec item (i), literally); `task_type_L1`,
`L2`, `L12`, `L123` = one-hot of the LLM-assigned hierarchical task type (11 domains / ~85 subdomains / free-text
level 3); `stats` = 15 z-scored query statistics (lengths, code and math markers, non-ASCII share, …);
`stats_whitened` = the same after PCA whitening; `stats_within_theme` = stats, with the kNN forced to stay inside the
query's theme; `handcrafted` = L1 + L2 + stats (d = 111, the default); `handcrafted_L1`, `handcrafted_L123`,
`handcrafted_whitened` = the ablations.

## Seen setting (all models known), 3 splits

| benchmark | embedding | gain (mean ± std over splits) | A | A single best | k per split |
|---|---|---|---|---|---|
| llmrouterbench | **handcrafted** | **+4.73% ± 0.33** | 0.7285 ± 0.0024 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | handcrafted_L1 | +4.88% ± 0.48 | 0.7295 ± 0.0019 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | handcrafted_L123 | +4.68% ± 0.35 | 0.7282 ± 0.0024 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | handcrafted_whitened | +4.33% ± 0.33 | 0.7257 ± 0.0023 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | stats | +4.42% ± 0.39 | 0.7263 ± 0.0022 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | stats_whitened | +3.53% ± 0.41 | 0.7202 ± 0.0017 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | stats_within_theme | **+5.47% ± 0.62** | 0.7337 ± 0.0022 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | task_type_L1 | +3.94% ± 0.06 | 0.7230 ± 0.0033 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | task_type_L12 | +4.14% ± 0.43 | 0.7244 ± 0.0034 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | task_type_L123 | +4.16% ± 0.41 | 0.7245 ± 0.0034 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | task_type_L2 | +3.48% ± 0.50 | 0.7198 ± 0.0019 | 0.6956 | 1000 1000 1000 † |
| llmrouterbench | task_type_raw | +4.77% ± 0.85 | 0.7287 ± 0.0042 | 0.6956 | 1000 1000 1000 † |
| routerbench | **handcrafted** | **+7.41% ± 0.28** | 0.7690 ± 0.0024 | 0.7159 | 1000 1000 1000 † |
| routerbench | handcrafted_L1 | +7.33% ± 0.30 | 0.7684 ± 0.0023 | 0.7159 | 1000 1000 1000 † |
| routerbench | handcrafted_L123 | +7.62% ± 0.48 | 0.7705 ± 0.0024 | 0.7159 | 500 500 1000 † |
| routerbench | handcrafted_whitened | +7.42% ± 0.43 | 0.7691 ± 0.0027 | 0.7159 | 500 1000 1000 † |
| routerbench | stats | +7.07% ± 0.30 | 0.7666 ± 0.0022 | 0.7159 | 1000 1000 1000 † |
| routerbench | stats_whitened | +7.15% ± 0.19 | 0.7671 ± 0.0024 | 0.7159 | 1000 1000 1000 † |
| routerbench | stats_within_theme | +7.42% ± 0.40 | 0.7691 ± 0.0019 | 0.7159 | 1000 1000 1000 † |
| routerbench | task_type_L1 | +2.62% ± 0.33 | 0.7347 ± 0.0006 | 0.7159 | 200 200 200 |
| routerbench | task_type_L12 | +3.70% ± 0.42 | 0.7424 ± 0.0050 | 0.7159 | 100 50 200 |
| routerbench | task_type_L123 | +4.89% ± 0.93 | 0.7509 ± 0.0084 | 0.7159 | 100 200 200 |
| routerbench | task_type_L2 | +3.97% ± 0.71 | 0.7444 ± 0.0078 | 0.7159 | 100 50 100 |
| routerbench | task_type_raw | +3.85% ± 0.42 | 0.7435 ± 0.0054 | 0.7159 | 50 100 50 |

† the selected k is the top of the grid on at least one split (see finding 4). Source: `analysis/seen_table.md`,
`analysis/k_tuning_summary.csv`.

## Unseen setting (`handcrafted`, every model held out in turn, 3 splits x 5 probe seeds)

Mean over held-out models and splits; `gain` is over the full-information single best, `gain (same probes)` over the
single best that knows the new model only from the same n probes, `recovery` = unseen gain / seen gain.

| benchmark | n probes | gain | gain (same probes) | recovery | A |
|---|---|---|---|---|---|
| llmrouterbench | 1 | −0.25% | +2.80% | −0.05 | 0.6939 |
| llmrouterbench | 2 | +2.39% | +3.18% | 0.51 | 0.7122 |
| llmrouterbench | 5 | +2.60% | +3.99% | 0.55 | 0.7136 |
| llmrouterbench | 10 | +1.09% | +3.14% | 0.23 | 0.7031 |
| llmrouterbench | 20 | +2.59% | +3.27% | 0.54 | 0.7136 |
| llmrouterbench | 50 | +3.07% | +3.32% | 0.64 | 0.7169 |
| llmrouterbench | 100 | +2.99% | +3.42% | 0.62 | 0.7164 |
| llmrouterbench | 500 | +3.81% | +3.85% | 0.80 | 0.7221 |
| routerbench | 1 | +0.35% | +6.45% | 0.04 | 0.7184 |
| routerbench | 2 | +3.53% | +6.93% | 0.47 | 0.7411 |
| routerbench | 5 | +4.88% | +7.16% | 0.66 | 0.7508 |
| routerbench | 10 | +5.36% | +7.28% | 0.72 | 0.7543 |
| routerbench | 20 | +5.82% | +6.74% | 0.78 | 0.7576 |
| routerbench | 50 | +6.23% | +6.38% | 0.84 | 0.7605 |
| routerbench | 100 | +6.27% | +6.34% | 0.85 | 0.7608 |
| routerbench | 500 | +6.33% | +6.34% | 0.85 | 0.7612 |

Probes to reach 90% recovery (mean over seeds, per held-out model and split, budget ≤ 500): LLMRouterBench 17 of 39
cases reach it, median n = 5 among those; RouterBench 18 of 33 cases, median n = 15. The A-based target of the paper
("A_unseen(n) ≥ 0.9 A_seen") is reached at n = 1 in every case because the single best alone already has
A_single_best / A_seen = 0.955 (LLMRB) and 0.931 (RB) ≥ 0.9, so it says nothing about the router; `probes_to_target.csv`
keeps both. Source: `analysis/A_unseen_curves.csv`, `analysis/unseen_table.csv` (per model),
`analysis/probes_to_target.csv`, figures `analysis/figures/A_unseen_*.png`, `gain_vs_probes_by_variant_*.png`.

## The 15 statistics as a classifier of the theme (logistic regression, train → test)

| benchmark | target | classes | majority | logistic regression | kNN (k = 50) |
|---|---|---|---|---|---|
| llmrouterbench | theme | 9 | 35.9% | 79.1% | 78.6% |
| llmrouterbench | task level 1 | 11 | 37.0% | 71.0% | 69.9% |
| routerbench | theme | 12 | 38.5% | 99.3% | 95.7% |
| routerbench | task level 1 | 11 | 32.0% | 76.9% | 80.5% |

LLMRouterBench confusions (rows = true theme): aime → mmlupro 50% / hle 42%, gpqa → hle 54% / mmlupro 41%,
livemathbench → mmlupro 46%, arenahard → mmlupro 40%; arc-agi, livecodebench and simpleqa are recognised at 97–99%.
RouterBench: every theme except mtbench (17 test queries) is recognised at ≥ 83%. Source: `analysis/stats_predict_labels.csv`,
`analysis/stats_predict_theme_<benchmark>.csv`, `analysis/figures/stats_predict_theme_<benchmark>.png`.

## Findings

1. **The handcrafted embedding routes better than the single best model on both benchmarks, and most of the gain
   comes from the query statistics.** `handcrafted` (L1 + L2 + stats) gains +4.7% ± 0.3 on LLMRouterBench and
   +7.4% ± 0.3 on RouterBench in the seen setting. The 15 statistics alone give +4.4% and +7.1%; the LLM task type
   alone gives +3.9% (L1) on LLMRouterBench and only +2.6% on RouterBench, where the themes are datasets rather than
   domains and the 9.8k mmlu training queries span every domain. Adding the task type to the statistics is worth
   +0.3 pp on both benchmarks, about one split standard deviation. Whitening the statistics does not help (it costs
   0.9 pp on LLMRouterBench and is a tie on RouterBench): PCA whitening gives the low-variance directions of a block
   of highly correlated length counts the same weight as the leading ones.

2. **The statistics add signal beyond the theme, but through different mechanisms on the two benchmarks.** On
   RouterBench the statistics identify the theme almost perfectly (99.3% test accuracy), yet they beat the theme
   one-hot by 3.2 pp (+7.1% vs +3.9%): within a theme, length and code or math markers still separate easy from hard
   queries. Restricting the neighbours to the query's theme (`stats_within_theme`, +7.4%) adds nothing there, since
   the neighbours already are within theme. On LLMRouterBench the statistics recover the theme only at 79% (the short
   maths and science themes aime, gpqa and livemathbench are confused with hle and mmlupro), and unrestricted
   statistics (+4.4%) do slightly worse than the theme one-hot (+4.8%); forcing the neighbours inside the theme and
   then using the statistics is the best variant on this benchmark (+5.5% ± 0.6, about 0.7 pp over `handcrafted`,
   one standard deviation). So the two blocks are complementary: the theme fixes which pool of queries to compare
   with, the statistics rank inside it. Note that on LLMRouterBench the plain theme one-hot — spec item (i) with
   k = 1000, i.e. the per-theme mean quality of every model — already matches `handcrafted`, with a larger split
   variance (± 0.85).

3. **The free-text level-3 task type is not worth its cost.** `handcrafted_L123` is within noise of `handcrafted`
   (+4.7% vs +4.7% on LLMRouterBench, +7.6% ± 0.5 vs +7.4% ± 0.3 on RouterBench) with a 100x larger embedding
   (d ≈ 11.5k vs 111; 90 s vs about 1 s per evaluation). Among the task-type-only variants, L3 helps on RouterBench
   (`task_type_L123` +4.9% vs `task_type_L12` +3.7%) with the largest split variance of the table (± 0.9), because
   the 15k free-text categories act as a fingerprint of the source dataset. `handcrafted` therefore stays L1 + L2 +
   stats and L123 is the named ablation.

4. **Every variant that contains the statistics selects the top of the k grid (k = 1000) on every split, in both
   benchmarks.** The harness's one-standard-error rule returns the largest k whose validation area is within one
   bootstrap standard error of the best k, so k = 1000 means the validation curve is flat from the best k up to the
   top of the grid, not that it is still rising there: the harness's own "best k at the edge" warning fired only for
   `stats_within_theme` (2 of 3 splits), `task_type_raw` (2 of 3) and `task_type_L2` (1 of 3) on LLMRouterBench, and
   for one held-out model (gpt-4-1106-preview) in the RouterBench unseen runs (`k_tuning_summary.csv`, columns
   `share_best_k_at_edge` vs `share_selected_k_at_edge`). The router is thus a wide local average (k = 1000 of 8.4k
   or 25.5k training queries); the previous grid cap at 200 (archived runs) was binding, the present one at 1000
   is at most slightly so. The task-type-only variants on RouterBench pick k = 50–200, which is simply the size of
   their subdomain cells. A grid up to 2000–5000 is cheap now (k is tuned once per held-out model) and would settle
   the remaining question.

5. **A new model is routed with a handful of probes, but the first probe can hurt.** With n = 1 probe the router
   loses against the full-information single best for 4 of 13 LLMRouterBench models and 4 of 11 RouterBench models
   (worst: deepseek-v3-0324 −8.9%, WizardLM-13B −9.1%, mixtral-8x7b −8.8%; shaded region of
   `gain_vs_probes_by_variant_llmrouterbench_epoch-1.png`). This is the cost of estimating the new model's quality from
   one query: against the single best that also knows the new model only from the same probes, the router wins in
   every case but one already at n = 1 (+2.8% / +6.5% on average). From n = 2 the mean gain is positive on both
   benchmarks and from n = 20 no held-out model is negative; n = 5 recovers 55% (LLMRB) and 66% (RB) of the
   seen-model gain, n = 50 recovers 64% and 84%, and n = 500 recovers 80% and 85%. The dip at n = 10 on
   LLMRouterBench (+1.1%, between +2.6% at n = 5 and n = 20) is one bad probe draw for a few models with 5 probe
   seeds, not a feature. Recovery of 90% within 500 probes is reached for 44% (LLMRB) and 55% (RB) of the
   model x split cases; the two code-llama / llama-2 models of RouterBench recover fully, the Yi-34B and the
   qwen3-thinking model recover only 37–50%.

## What is not in these numbers

- The unseen setting was run for `handcrafted` only (the by-variant figure therefore has one panel); the ablations
  are seen-setting only.
- `rq1a_ratio.csv` is the ratio A(task type only) / A(other embedding); the comparison against Michal's learned
  embedding (`is_rq1a`) is empty until a `learned` variant exists in the results.
- 3 splits and 5 probe seeds: differences below about 0.5 pp in the seen table are within split noise.
