# Paired comparisons against `handcrafted`

d_gain = gain(a) - gain(b) on the same split and pool; the interval is the 95% paired bootstrap over the test queries; p is the two-sided bootstrap p-value. `wins` counts splits (x seeds) where a > b, `ci_excludes_0` those whose paired interval excludes zero.

## Seen setting (final pool and instance pools)

| benchmark | setting | instance | new_model | n_probes | a | b | n | d_gain_mean | d_gain_sd | d_A_mean | wins | ci_excludes_0 | min_p | median_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llmrouterbench | seen | -1 |  | 0 | handcrafted_L1 | handcrafted | 3 | 0.0015 | 0.0016 | 0.0010 | 2 | 0 | 0.2760 | 0.2900 |
| llmrouterbench | seen | -1 |  | 0 | handcrafted_L123 | handcrafted | 3 | -0.0005 | 0.0002 | -0.0003 | 0 | 0 | 0.6400 | 0.7620 |
| llmrouterbench | seen | -1 |  | 0 | handcrafted_whitened | handcrafted | 3 | -0.0040 | 0.0001 | -0.0028 | 0 | 0 | 0.1220 | 0.1440 |
| llmrouterbench | seen | -1 |  | 0 | stats | handcrafted | 3 | -0.0032 | 0.0007 | -0.0022 | 0 | 0 | 0.2560 | 0.4200 |
| llmrouterbench | seen | -1 |  | 0 | stats_whitened | handcrafted | 3 | -0.0120 | 0.0011 | -0.0083 | 0 | 3 | 0.0040 | 0.0060 |
| llmrouterbench | seen | -1 |  | 0 | stats_within_theme | handcrafted | 3 | 0.0074 | 0.0030 | 0.0052 | 3 | 1 | 0.0260 | 0.0700 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0079 | 0.0027 | -0.0055 | 0 | 2 | 0.0100 | 0.0140 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0059 | 0.0018 | -0.0041 | 0 | 1 | 0.0100 | 0.1120 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L123 | handcrafted | 3 | -0.0057 | 0.0016 | -0.0039 | 0 | 1 | 0.0120 | 0.1280 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0126 | 0.0018 | -0.0087 | 0 | 3 | 0.0000 | 0.0060 |
| llmrouterbench | seen | -1 |  | 0 | task_type_raw | handcrafted | 3 | 0.0004 | 0.0052 | 0.0002 | 2 | 0 | 0.1280 | 0.1780 |
| routerbench | seen | -1 |  | 0 | handcrafted_L1 | handcrafted | 3 | -0.0008 | 0.0002 | -0.0006 | 0 | 0 | 0.2760 | 0.5160 |
| routerbench | seen | -1 |  | 0 | handcrafted_L123 | handcrafted | 3 | 0.0021 | 0.0021 | 0.0015 | 2 | 2 | 0.0020 | 0.0120 |
| routerbench | seen | -1 |  | 0 | handcrafted_whitened | handcrafted | 3 | 0.0002 | 0.0015 | 0.0001 | 2 | 0 | 0.1800 | 0.2300 |
| routerbench | seen | -1 |  | 0 | stats | handcrafted | 3 | -0.0033 | 0.0003 | -0.0024 | 0 | 0 | 0.0820 | 0.1020 |
| routerbench | seen | -1 |  | 0 | stats_whitened | handcrafted | 3 | -0.0026 | 0.0010 | -0.0019 | 0 | 0 | 0.0920 | 0.2000 |
| routerbench | seen | -1 |  | 0 | stats_within_theme | handcrafted | 3 | 0.0002 | 0.0015 | 0.0001 | 2 | 0 | 0.3300 | 0.3480 |
| routerbench | seen | -1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0478 | 0.0033 | -0.0343 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0371 | 0.0040 | -0.0265 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_L123 | handcrafted | 3 | -0.0252 | 0.0085 | -0.0180 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0344 | 0.0087 | -0.0246 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_raw | handcrafted | 3 | -0.0355 | 0.0048 | -0.0254 | 0 | 3 | 0.0000 | 0.0000 |
