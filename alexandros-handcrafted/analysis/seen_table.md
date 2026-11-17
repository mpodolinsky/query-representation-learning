| benchmark | epoch | embedding | gain (mean ± std over splits) | A | A single best | k per split | splits |
|---|---|---|---|---|---|---|---|
| llmrouterbench | all models | handcrafted | +4.73% ± 0.33 | 0.7285 ± 0.0024 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | handcrafted_L1 | +4.88% ± 0.48 | 0.7295 ± 0.0019 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | handcrafted_L123 | +4.68% ± 0.35 | 0.7282 ± 0.0024 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | handcrafted_whitened | +4.33% ± 0.33 | 0.7257 ± 0.0023 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | stats | +4.42% ± 0.39 | 0.7263 ± 0.0022 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | stats_whitened | +3.53% ± 0.41 | 0.7202 ± 0.0017 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | stats_within_theme | +5.47% ± 0.62 | 0.7337 ± 0.0022 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | task_type_L1 | +3.94% ± 0.06 | 0.7230 ± 0.0033 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | task_type_L12 | +4.14% ± 0.43 | 0.7244 ± 0.0034 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | task_type_L123 | +4.16% ± 0.41 | 0.7245 ± 0.0034 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | task_type_L2 | +3.48% ± 0.50 | 0.7198 ± 0.0019 | 0.6956 | 1000 1000 1000 † | 3 |
| llmrouterbench | all models | task_type_raw | +4.77% ± 0.85 | 0.7287 ± 0.0042 | 0.6956 | 1000 1000 1000 † | 3 |
| routerbench | all models | handcrafted | +7.41% ± 0.28 | 0.7690 ± 0.0024 | 0.7159 | 1000 1000 1000 † | 3 |
| routerbench | all models | handcrafted_L1 | +7.33% ± 0.30 | 0.7684 ± 0.0023 | 0.7159 | 1000 1000 1000 † | 3 |
| routerbench | all models | handcrafted_L123 | +7.62% ± 0.48 | 0.7705 ± 0.0024 | 0.7159 | 500 500 1000 † | 3 |
| routerbench | all models | handcrafted_whitened | +7.42% ± 0.43 | 0.7691 ± 0.0027 | 0.7159 | 500 1000 1000 † | 3 |
| routerbench | all models | stats | +7.07% ± 0.30 | 0.7666 ± 0.0022 | 0.7159 | 1000 1000 1000 † | 3 |
| routerbench | all models | stats_whitened | +7.15% ± 0.19 | 0.7671 ± 0.0024 | 0.7159 | 1000 1000 1000 † | 3 |
| routerbench | all models | stats_within_theme | +7.42% ± 0.40 | 0.7691 ± 0.0019 | 0.7159 | 1000 1000 1000 † | 3 |
| routerbench | all models | task_type_L1 | +2.62% ± 0.33 | 0.7347 ± 0.0006 | 0.7159 | 200 200 200 | 3 |
| routerbench | all models | task_type_L12 | +3.70% ± 0.42 | 0.7424 ± 0.0050 | 0.7159 | 100 50 200 | 3 |
| routerbench | all models | task_type_L123 | +4.89% ± 0.93 | 0.7509 ± 0.0084 | 0.7159 | 100 200 200 | 3 |
| routerbench | all models | task_type_L2 | +3.97% ± 0.71 | 0.7444 ± 0.0078 | 0.7159 | 100 50 100 | 3 |
| routerbench | all models | task_type_raw | +3.85% ± 0.42 | 0.7435 ± 0.0054 | 0.7159 | 50 100 50 | 3 |

† the tuned k hit the edge of the k grid on at least one split (the harness's `select_k` warning, or the selected k is the grid's minimum or maximum).
