# Paired comparisons against `handcrafted`

d_gain = gain(a) - gain(b) on the same split and pool; the interval is the 95% paired bootstrap over the test queries; p is the two-sided bootstrap p-value. `wins` counts splits (x seeds) where a > b, `ci_excludes_0` those whose paired interval excludes zero.

## Seen setting (final pool and instance pools)

| benchmark | setting | instance | new_model | n_probes | a | b | n | d_gain_mean | d_gain_sd | d_A_mean | wins | ci_excludes_0 | min_p | median_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llmrouterbench | seen | -1 |  | 0 | combined | handcrafted | 3 | -0.0015 | 0.0017 | -0.0010 | 0 | 0 | 0.0880 | 0.9140 |
| llmrouterbench | seen | -1 |  | 0 | contrastive | handcrafted | 3 | -0.0281 | 0.0007 | -0.0195 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | -1 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0147 | 0.0040 | -0.0102 | 0 | 1 | 0.0000 | 0.0660 |
| llmrouterbench | seen | -1 |  | 0 | frozen | handcrafted | 3 | -0.0066 | 0.0031 | -0.0046 | 0 | 1 | 0.0140 | 0.2240 |
| llmrouterbench | seen | -1 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0013 | 0.0041 | 0.0009 | 2 | 0 | 0.1840 | 0.4740 |
| llmrouterbench | seen | -1 |  | 0 | regression | handcrafted | 3 | -0.0056 | 0.0081 | -0.0039 | 1 | 1 | 0.0160 | 0.1820 |
| llmrouterbench | seen | -1 |  | 0 | regression_hc | handcrafted | 3 | -0.0006 | 0.0075 | -0.0004 | 1 | 0 | 0.0560 | 0.0940 |
| llmrouterbench | seen | -1 |  | 0 | stats | handcrafted | 3 | -0.0032 | 0.0007 | -0.0022 | 0 | 0 | 0.2560 | 0.4200 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0079 | 0.0027 | -0.0055 | 0 | 2 | 0.0100 | 0.0140 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0052 | 0.0022 | -0.0036 | 0 | 1 | 0.0140 | 0.1240 |
| llmrouterbench | seen | -1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0104 | 0.0012 | -0.0072 | 0 | 3 | 0.0120 | 0.0140 |
| llmrouterbench | seen | -1 |  | 0 | task_type_theme | handcrafted | 3 | 0.0004 | 0.0052 | 0.0002 | 2 | 0 | 0.1280 | 0.1780 |
| llmrouterbench | seen | 0 |  | 0 | combined | handcrafted | 3 | 0.0011 | 0.0008 | 0.0009 | 3 | 0 | 0.5260 | 0.7760 |
| llmrouterbench | seen | 0 |  | 0 | contrastive | handcrafted | 3 | -0.0037 | 0.0049 | -0.0033 | 1 | 0 | 0.0880 | 0.6140 |
| llmrouterbench | seen | 0 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0001 | 0.0057 | -0.0001 | 2 | 0 | 0.1620 | 0.3340 |
| llmrouterbench | seen | 0 |  | 0 | frozen | handcrafted | 3 | -0.0028 | 0.0037 | -0.0025 | 1 | 0 | 0.1160 | 0.9240 |
| llmrouterbench | seen | 0 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0071 | 0.0040 | 0.0062 | 3 | 1 | 0.0140 | 0.1640 |
| llmrouterbench | seen | 0 |  | 0 | regression | handcrafted | 3 | -0.0030 | 0.0036 | -0.0026 | 1 | 0 | 0.3740 | 0.4620 |
| llmrouterbench | seen | 0 |  | 0 | regression_hc | handcrafted | 3 | -0.0001 | 0.0066 | -0.0001 | 2 | 0 | 0.1580 | 0.1920 |
| llmrouterbench | seen | 0 |  | 0 | stats | handcrafted | 3 | -0.0107 | 0.0020 | -0.0093 | 0 | 2 | 0.0040 | 0.0160 |
| llmrouterbench | seen | 0 |  | 0 | task_type_L1 | handcrafted | 3 | 0.0001 | 0.0010 | 0.0001 | 1 | 0 | 0.6180 | 0.9300 |
| llmrouterbench | seen | 0 |  | 0 | task_type_L12 | handcrafted | 3 | 0.0027 | 0.0024 | 0.0024 | 2 | 0 | 0.2880 | 0.4300 |
| llmrouterbench | seen | 0 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0062 | 0.0032 | -0.0054 | 0 | 0 | 0.0500 | 0.2460 |
| llmrouterbench | seen | 0 |  | 0 | task_type_theme | handcrafted | 3 | 0.0065 | 0.0048 | 0.0057 | 3 | 1 | 0.0180 | 0.2480 |
| llmrouterbench | seen | 1 |  | 0 | combined | handcrafted | 3 | 0.0007 | 0.0012 | 0.0006 | 2 | 0 | 0.0800 | 0.7800 |
| llmrouterbench | seen | 1 |  | 0 | contrastive | handcrafted | 3 | -0.0150 | 0.0016 | -0.0123 | 0 | 3 | 0.0040 | 0.0040 |
| llmrouterbench | seen | 1 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0054 | 0.0003 | -0.0044 | 0 | 0 | 0.2740 | 0.3060 |
| llmrouterbench | seen | 1 |  | 0 | frozen | handcrafted | 3 | -0.0023 | 0.0017 | -0.0019 | 1 | 0 | 0.4000 | 0.5260 |
| llmrouterbench | seen | 1 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0024 | 0.0008 | -0.0020 | 0 | 0 | 0.4280 | 0.4980 |
| llmrouterbench | seen | 1 |  | 0 | regression | handcrafted | 3 | -0.0142 | 0.0048 | -0.0116 | 0 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | seen | 1 |  | 0 | regression_hc | handcrafted | 3 | -0.0061 | 0.0038 | -0.0049 | 0 | 1 | 0.0300 | 0.4600 |
| llmrouterbench | seen | 1 |  | 0 | stats | handcrafted | 3 | -0.0033 | 0.0009 | -0.0027 | 0 | 1 | 0.0460 | 0.1140 |
| llmrouterbench | seen | 1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0053 | 0.0011 | -0.0043 | 0 | 0 | 0.0640 | 0.0660 |
| llmrouterbench | seen | 1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0036 | 0.0008 | -0.0029 | 0 | 0 | 0.1840 | 0.2960 |
| llmrouterbench | seen | 1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0056 | 0.0046 | -0.0046 | 1 | 1 | 0.0280 | 0.1100 |
| llmrouterbench | seen | 1 |  | 0 | task_type_theme | handcrafted | 3 | -0.0028 | 0.0038 | -0.0023 | 1 | 0 | 0.1720 | 0.2920 |
| llmrouterbench | seen | 2 |  | 0 | combined | handcrafted | 3 | 0.0014 | 0.0022 | 0.0011 | 1 | 1 | 0.0180 | 0.7560 |
| llmrouterbench | seen | 2 |  | 0 | contrastive | handcrafted | 3 | -0.0138 | 0.0015 | -0.0107 | 0 | 3 | 0.0040 | 0.0220 |
| llmrouterbench | seen | 2 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0065 | 0.0025 | -0.0050 | 0 | 0 | 0.0760 | 0.1920 |
| llmrouterbench | seen | 2 |  | 0 | frozen | handcrafted | 3 | -0.0016 | 0.0026 | -0.0012 | 1 | 0 | 0.3280 | 0.6860 |
| llmrouterbench | seen | 2 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0030 | 0.0006 | -0.0023 | 0 | 0 | 0.2960 | 0.5820 |
| llmrouterbench | seen | 2 |  | 0 | regression | handcrafted | 3 | -0.0126 | 0.0040 | -0.0097 | 0 | 2 | 0.0040 | 0.0180 |
| llmrouterbench | seen | 2 |  | 0 | regression_hc | handcrafted | 3 | -0.0111 | 0.0056 | -0.0086 | 0 | 1 | 0.0040 | 0.1740 |
| llmrouterbench | seen | 2 |  | 0 | stats | handcrafted | 3 | -0.0029 | 0.0011 | -0.0022 | 0 | 0 | 0.1040 | 0.1460 |
| llmrouterbench | seen | 2 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0059 | 0.0016 | -0.0045 | 0 | 1 | 0.0500 | 0.0560 |
| llmrouterbench | seen | 2 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0042 | 0.0003 | -0.0032 | 0 | 0 | 0.1400 | 0.2240 |
| llmrouterbench | seen | 2 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0070 | 0.0053 | -0.0054 | 1 | 2 | 0.0080 | 0.0280 |
| llmrouterbench | seen | 2 |  | 0 | task_type_theme | handcrafted | 3 | -0.0036 | 0.0041 | -0.0028 | 1 | 0 | 0.0580 | 0.4240 |
| llmrouterbench | seen | 3 |  | 0 | combined | handcrafted | 3 | 0.0017 | 0.0004 | 0.0013 | 3 | 0 | 0.0760 | 0.2340 |
| llmrouterbench | seen | 3 |  | 0 | contrastive | handcrafted | 3 | -0.0201 | 0.0015 | -0.0153 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 3 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0037 | 0.0018 | -0.0028 | 0 | 0 | 0.2700 | 0.2780 |
| llmrouterbench | seen | 3 |  | 0 | frozen | handcrafted | 3 | -0.0041 | 0.0026 | -0.0031 | 0 | 0 | 0.1080 | 0.1100 |
| llmrouterbench | seen | 3 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0040 | 0.0012 | -0.0030 | 0 | 0 | 0.2360 | 0.4640 |
| llmrouterbench | seen | 3 |  | 0 | regression | handcrafted | 3 | -0.0128 | 0.0033 | -0.0097 | 0 | 3 | 0.0000 | 0.0220 |
| llmrouterbench | seen | 3 |  | 0 | regression_hc | handcrafted | 3 | -0.0068 | 0.0013 | -0.0052 | 0 | 0 | 0.1160 | 0.1180 |
| llmrouterbench | seen | 3 |  | 0 | stats | handcrafted | 3 | -0.0093 | 0.0010 | -0.0071 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | seen | 3 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0082 | 0.0022 | -0.0062 | 0 | 2 | 0.0040 | 0.0060 |
| llmrouterbench | seen | 3 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0052 | 0.0024 | -0.0040 | 0 | 2 | 0.0120 | 0.0160 |
| llmrouterbench | seen | 3 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0092 | 0.0050 | -0.0070 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 3 |  | 0 | task_type_theme | handcrafted | 3 | -0.0017 | 0.0030 | -0.0013 | 1 | 0 | 0.3560 | 0.4960 |
| llmrouterbench | seen | 4 |  | 0 | combined | handcrafted | 3 | 0.0000 | 0.0011 | 0.0000 | 1 | 0 | 0.3320 | 0.5500 |
| llmrouterbench | seen | 4 |  | 0 | contrastive | handcrafted | 3 | -0.0065 | 0.0031 | -0.0050 | 0 | 0 | 0.0720 | 0.1020 |
| llmrouterbench | seen | 4 |  | 0 | contrastive_hc | handcrafted | 3 | 0.0021 | 0.0034 | 0.0016 | 2 | 0 | 0.1760 | 0.6600 |
| llmrouterbench | seen | 4 |  | 0 | frozen | handcrafted | 3 | -0.0059 | 0.0025 | -0.0045 | 0 | 1 | 0.0140 | 0.2060 |
| llmrouterbench | seen | 4 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0021 | 0.0037 | 0.0016 | 2 | 0 | 0.1840 | 0.3780 |
| llmrouterbench | seen | 4 |  | 0 | regression | handcrafted | 3 | 0.0033 | 0.0051 | 0.0025 | 2 | 1 | 0.0380 | 0.5660 |
| llmrouterbench | seen | 4 |  | 0 | regression_hc | handcrafted | 3 | 0.0076 | 0.0050 | 0.0058 | 3 | 2 | 0.0020 | 0.0280 |
| llmrouterbench | seen | 4 |  | 0 | stats | handcrafted | 3 | -0.0001 | 0.0024 | -0.0001 | 1 | 0 | 0.2120 | 0.4200 |
| llmrouterbench | seen | 4 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0089 | 0.0007 | -0.0067 | 0 | 3 | 0.0020 | 0.0060 |
| llmrouterbench | seen | 4 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0069 | 0.0004 | -0.0052 | 0 | 3 | 0.0080 | 0.0160 |
| llmrouterbench | seen | 4 |  | 0 | task_type_L2 | handcrafted | 3 | 0.0011 | 0.0016 | 0.0008 | 2 | 0 | 0.3680 | 0.7840 |
| llmrouterbench | seen | 4 |  | 0 | task_type_theme | handcrafted | 3 | 0.0047 | 0.0019 | 0.0035 | 3 | 0 | 0.1300 | 0.1520 |
| llmrouterbench | seen | 5 |  | 0 | combined | handcrafted | 3 | -0.0008 | 0.0013 | -0.0006 | 1 | 0 | 0.2900 | 0.4780 |
| llmrouterbench | seen | 5 |  | 0 | contrastive | handcrafted | 3 | -0.0112 | 0.0040 | -0.0083 | 0 | 1 | 0.0040 | 0.0600 |
| llmrouterbench | seen | 5 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0027 | 0.0044 | -0.0020 | 1 | 0 | 0.1360 | 0.7380 |
| llmrouterbench | seen | 5 |  | 0 | frozen | handcrafted | 3 | -0.0079 | 0.0030 | -0.0059 | 0 | 1 | 0.0020 | 0.1040 |
| llmrouterbench | seen | 5 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0020 | 0.0034 | 0.0014 | 2 | 0 | 0.2940 | 0.3220 |
| llmrouterbench | seen | 5 |  | 0 | regression | handcrafted | 3 | -0.0001 | 0.0069 | -0.0001 | 1 | 1 | 0.0260 | 0.2220 |
| llmrouterbench | seen | 5 |  | 0 | regression_hc | handcrafted | 3 | 0.0056 | 0.0041 | 0.0042 | 3 | 1 | 0.0120 | 0.2460 |
| llmrouterbench | seen | 5 |  | 0 | stats | handcrafted | 3 | -0.0019 | 0.0016 | -0.0014 | 1 | 0 | 0.2160 | 0.3240 |
| llmrouterbench | seen | 5 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0060 | 0.0014 | -0.0045 | 0 | 1 | 0.0220 | 0.0880 |
| llmrouterbench | seen | 5 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0040 | 0.0011 | -0.0030 | 0 | 0 | 0.0860 | 0.2880 |
| llmrouterbench | seen | 5 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0012 | 0.0016 | -0.0009 | 1 | 0 | 0.3700 | 0.8280 |
| llmrouterbench | seen | 5 |  | 0 | task_type_theme | handcrafted | 3 | 0.0024 | 0.0023 | 0.0018 | 2 | 0 | 0.2900 | 0.5440 |
| llmrouterbench | seen | 6 |  | 0 | combined | handcrafted | 3 | -0.0014 | 0.0013 | -0.0010 | 1 | 0 | 0.2180 | 0.2880 |
| llmrouterbench | seen | 6 |  | 0 | contrastive | handcrafted | 3 | -0.0128 | 0.0029 | -0.0094 | 0 | 2 | 0.0000 | 0.0260 |
| llmrouterbench | seen | 6 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0043 | 0.0044 | -0.0032 | 1 | 0 | 0.1060 | 0.5060 |
| llmrouterbench | seen | 6 |  | 0 | frozen | handcrafted | 3 | -0.0084 | 0.0030 | -0.0062 | 0 | 1 | 0.0000 | 0.0740 |
| llmrouterbench | seen | 6 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0014 | 0.0033 | 0.0010 | 2 | 0 | 0.3820 | 0.4000 |
| llmrouterbench | seen | 6 |  | 0 | regression | handcrafted | 3 | -0.0025 | 0.0082 | -0.0019 | 1 | 1 | 0.0440 | 0.0960 |
| llmrouterbench | seen | 6 |  | 0 | regression_hc | handcrafted | 3 | 0.0041 | 0.0062 | 0.0030 | 2 | 1 | 0.0060 | 0.4200 |
| llmrouterbench | seen | 6 |  | 0 | stats | handcrafted | 3 | -0.0024 | 0.0017 | -0.0018 | 0 | 0 | 0.1700 | 0.2600 |
| llmrouterbench | seen | 6 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0066 | 0.0014 | -0.0048 | 0 | 1 | 0.0100 | 0.0720 |
| llmrouterbench | seen | 6 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0045 | 0.0011 | -0.0033 | 0 | 0 | 0.0840 | 0.2120 |
| llmrouterbench | seen | 6 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0017 | 0.0016 | -0.0013 | 0 | 0 | 0.3160 | 0.7060 |
| llmrouterbench | seen | 6 |  | 0 | task_type_theme | handcrafted | 3 | 0.0019 | 0.0023 | 0.0014 | 2 | 0 | 0.3640 | 0.6400 |
| llmrouterbench | seen | 7 |  | 0 | combined | handcrafted | 3 | -0.0014 | 0.0013 | -0.0010 | 1 | 0 | 0.1960 | 0.3420 |
| llmrouterbench | seen | 7 |  | 0 | contrastive | handcrafted | 3 | -0.0139 | 0.0033 | -0.0100 | 0 | 2 | 0.0020 | 0.0200 |
| llmrouterbench | seen | 7 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0051 | 0.0051 | -0.0037 | 0 | 1 | 0.0180 | 0.5280 |
| llmrouterbench | seen | 7 |  | 0 | frozen | handcrafted | 3 | -0.0084 | 0.0031 | -0.0061 | 0 | 1 | 0.0000 | 0.0860 |
| llmrouterbench | seen | 7 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0014 | 0.0033 | 0.0010 | 2 | 0 | 0.3820 | 0.4000 |
| llmrouterbench | seen | 7 |  | 0 | regression | handcrafted | 3 | -0.0011 | 0.0064 | -0.0008 | 1 | 0 | 0.0860 | 0.1620 |
| llmrouterbench | seen | 7 |  | 0 | regression_hc | handcrafted | 3 | 0.0034 | 0.0041 | 0.0025 | 3 | 1 | 0.0340 | 0.9200 |
| llmrouterbench | seen | 7 |  | 0 | stats | handcrafted | 3 | -0.0024 | 0.0017 | -0.0018 | 0 | 0 | 0.1700 | 0.2460 |
| llmrouterbench | seen | 7 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0066 | 0.0014 | -0.0048 | 0 | 1 | 0.0100 | 0.0640 |
| llmrouterbench | seen | 7 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0045 | 0.0010 | -0.0033 | 0 | 0 | 0.0840 | 0.2100 |
| llmrouterbench | seen | 7 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0017 | 0.0016 | -0.0013 | 0 | 0 | 0.3160 | 0.6940 |
| llmrouterbench | seen | 7 |  | 0 | task_type_theme | handcrafted | 3 | 0.0019 | 0.0022 | 0.0013 | 2 | 0 | 0.3680 | 0.6400 |
| llmrouterbench | seen | 8 |  | 0 | combined | handcrafted | 3 | -0.0009 | 0.0018 | -0.0007 | 2 | 1 | 0.0480 | 0.6340 |
| llmrouterbench | seen | 8 |  | 0 | contrastive | handcrafted | 3 | -0.0230 | 0.0015 | -0.0166 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 8 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0100 | 0.0020 | -0.0072 | 0 | 2 | 0.0080 | 0.0480 |
| llmrouterbench | seen | 8 |  | 0 | frozen | handcrafted | 3 | -0.0041 | 0.0038 | -0.0029 | 0 | 1 | 0.0020 | 0.5560 |
| llmrouterbench | seen | 8 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0020 | 0.0040 | 0.0014 | 2 | 0 | 0.0680 | 0.3240 |
| llmrouterbench | seen | 8 |  | 0 | regression | handcrafted | 3 | -0.0010 | 0.0060 | -0.0008 | 2 | 0 | 0.0540 | 0.1880 |
| llmrouterbench | seen | 8 |  | 0 | regression_hc | handcrafted | 3 | 0.0011 | 0.0035 | 0.0008 | 2 | 0 | 0.1220 | 0.4860 |
| llmrouterbench | seen | 8 |  | 0 | stats | handcrafted | 3 | -0.0013 | 0.0008 | -0.0009 | 0 | 0 | 0.4420 | 0.4660 |
| llmrouterbench | seen | 8 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0092 | 0.0011 | -0.0067 | 0 | 3 | 0.0040 | 0.0040 |
| llmrouterbench | seen | 8 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0080 | 0.0010 | -0.0058 | 0 | 3 | 0.0020 | 0.0060 |
| llmrouterbench | seen | 8 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0081 | 0.0017 | -0.0059 | 0 | 2 | 0.0040 | 0.0060 |
| llmrouterbench | seen | 8 |  | 0 | task_type_theme | handcrafted | 3 | -0.0008 | 0.0035 | -0.0006 | 1 | 0 | 0.1080 | 0.4400 |
| llmrouterbench | seen | 9 |  | 0 | combined | handcrafted | 3 | -0.0011 | 0.0013 | -0.0008 | 1 | 0 | 0.1300 | 0.6900 |
| llmrouterbench | seen | 9 |  | 0 | contrastive | handcrafted | 3 | -0.0211 | 0.0028 | -0.0149 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 9 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0130 | 0.0055 | -0.0091 | 0 | 2 | 0.0000 | 0.0100 |
| llmrouterbench | seen | 9 |  | 0 | frozen | handcrafted | 3 | -0.0045 | 0.0031 | -0.0032 | 0 | 1 | 0.0080 | 0.3160 |
| llmrouterbench | seen | 9 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0013 | 0.0035 | 0.0009 | 2 | 0 | 0.0940 | 0.4300 |
| llmrouterbench | seen | 9 |  | 0 | regression | handcrafted | 3 | -0.0059 | 0.0073 | -0.0042 | 1 | 1 | 0.0000 | 0.0520 |
| llmrouterbench | seen | 9 |  | 0 | regression_hc | handcrafted | 3 | 0.0028 | 0.0035 | 0.0020 | 2 | 0 | 0.1280 | 0.1920 |
| llmrouterbench | seen | 9 |  | 0 | stats | handcrafted | 3 | -0.0014 | 0.0011 | -0.0010 | 0 | 0 | 0.2500 | 0.7460 |
| llmrouterbench | seen | 9 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0090 | 0.0020 | -0.0063 | 0 | 2 | 0.0020 | 0.0060 |
| llmrouterbench | seen | 9 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0074 | 0.0020 | -0.0052 | 0 | 2 | 0.0000 | 0.0120 |
| llmrouterbench | seen | 9 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0083 | 0.0018 | -0.0058 | 0 | 2 | 0.0020 | 0.0180 |
| llmrouterbench | seen | 9 |  | 0 | task_type_theme | handcrafted | 3 | -0.0006 | 0.0033 | -0.0004 | 1 | 0 | 0.2380 | 0.3400 |
| llmrouterbench | seen | 10 |  | 0 | combined | handcrafted | 3 | -0.0015 | 0.0017 | -0.0010 | 0 | 0 | 0.0880 | 0.9140 |
| llmrouterbench | seen | 10 |  | 0 | contrastive | handcrafted | 3 | -0.0253 | 0.0016 | -0.0177 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 10 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0131 | 0.0023 | -0.0092 | 0 | 1 | 0.0080 | 0.0740 |
| llmrouterbench | seen | 10 |  | 0 | frozen | handcrafted | 3 | -0.0066 | 0.0031 | -0.0047 | 0 | 1 | 0.0140 | 0.2240 |
| llmrouterbench | seen | 10 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0013 | 0.0041 | 0.0009 | 2 | 0 | 0.1840 | 0.4740 |
| llmrouterbench | seen | 10 |  | 0 | regression | handcrafted | 3 | -0.0066 | 0.0067 | -0.0046 | 1 | 2 | 0.0260 | 0.0420 |
| llmrouterbench | seen | 10 |  | 0 | regression_hc | handcrafted | 3 | 0.0004 | 0.0044 | 0.0003 | 1 | 0 | 0.2140 | 0.5980 |
| llmrouterbench | seen | 10 |  | 0 | stats | handcrafted | 3 | -0.0032 | 0.0007 | -0.0022 | 0 | 0 | 0.2560 | 0.4200 |
| llmrouterbench | seen | 10 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0079 | 0.0027 | -0.0055 | 0 | 2 | 0.0100 | 0.0140 |
| llmrouterbench | seen | 10 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0052 | 0.0022 | -0.0036 | 0 | 1 | 0.0140 | 0.1240 |
| llmrouterbench | seen | 10 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0104 | 0.0012 | -0.0073 | 0 | 3 | 0.0120 | 0.0140 |
| llmrouterbench | seen | 10 |  | 0 | task_type_theme | handcrafted | 3 | 0.0004 | 0.0052 | 0.0002 | 2 | 0 | 0.1280 | 0.1780 |
| llmrouterbench | seen | 11 |  | 0 | combined | handcrafted | 3 | -0.0015 | 0.0017 | -0.0010 | 0 | 0 | 0.0880 | 0.9140 |
| llmrouterbench | seen | 11 |  | 0 | contrastive | handcrafted | 3 | -0.0281 | 0.0007 | -0.0195 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | seen | 11 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0147 | 0.0040 | -0.0102 | 0 | 1 | 0.0000 | 0.0660 |
| llmrouterbench | seen | 11 |  | 0 | frozen | handcrafted | 3 | -0.0066 | 0.0031 | -0.0046 | 0 | 1 | 0.0140 | 0.2240 |
| llmrouterbench | seen | 11 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0013 | 0.0041 | 0.0009 | 2 | 0 | 0.1840 | 0.4740 |
| llmrouterbench | seen | 11 |  | 0 | regression | handcrafted | 3 | -0.0056 | 0.0081 | -0.0039 | 1 | 1 | 0.0160 | 0.1820 |
| llmrouterbench | seen | 11 |  | 0 | regression_hc | handcrafted | 3 | -0.0006 | 0.0075 | -0.0004 | 1 | 0 | 0.0560 | 0.0940 |
| llmrouterbench | seen | 11 |  | 0 | stats | handcrafted | 3 | -0.0032 | 0.0007 | -0.0022 | 0 | 0 | 0.2560 | 0.4200 |
| llmrouterbench | seen | 11 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0079 | 0.0027 | -0.0055 | 0 | 2 | 0.0100 | 0.0140 |
| llmrouterbench | seen | 11 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0052 | 0.0022 | -0.0036 | 0 | 1 | 0.0140 | 0.1240 |
| llmrouterbench | seen | 11 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0104 | 0.0012 | -0.0072 | 0 | 3 | 0.0120 | 0.0140 |
| llmrouterbench | seen | 11 |  | 0 | task_type_theme | handcrafted | 3 | 0.0004 | 0.0052 | 0.0002 | 2 | 0 | 0.1280 | 0.1780 |
| routerbench | seen | -1 |  | 0 | combined | handcrafted | 3 | 0.0036 | 0.0027 | 0.0026 | 3 | 1 | 0.0000 | 0.1080 |
| routerbench | seen | -1 |  | 0 | contrastive | handcrafted | 3 | 0.0013 | 0.0008 | 0.0009 | 3 | 0 | 0.3320 | 0.4440 |
| routerbench | seen | -1 |  | 0 | contrastive_hc | handcrafted | 3 | 0.0050 | 0.0005 | 0.0036 | 3 | 3 | 0.0040 | 0.0120 |
| routerbench | seen | -1 |  | 0 | frozen | handcrafted | 3 | -0.0031 | 0.0004 | -0.0022 | 0 | 0 | 0.1280 | 0.1880 |
| routerbench | seen | -1 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0024 | 0.0020 | -0.0017 | 1 | 1 | 0.0360 | 0.2240 |
| routerbench | seen | -1 |  | 0 | regression | handcrafted | 3 | 0.0037 | 0.0015 | 0.0027 | 3 | 1 | 0.0060 | 0.0580 |
| routerbench | seen | -1 |  | 0 | regression_hc | handcrafted | 3 | 0.0057 | 0.0005 | 0.0041 | 3 | 3 | 0.0000 | 0.0020 |
| routerbench | seen | -1 |  | 0 | stats | handcrafted | 3 | -0.0033 | 0.0003 | -0.0024 | 0 | 0 | 0.0820 | 0.1020 |
| routerbench | seen | -1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0478 | 0.0033 | -0.0343 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0398 | 0.0114 | -0.0284 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0373 | 0.0122 | -0.0267 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | -1 |  | 0 | task_type_theme | handcrafted | 3 | -0.0355 | 0.0048 | -0.0254 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 0 |  | 0 | combined | handcrafted | 3 | -0.0011 | 0.0005 | -0.0009 | 0 | 0 | 0.3340 | 0.3780 |
| routerbench | seen | 0 |  | 0 | contrastive | handcrafted | 3 | -0.0092 | 0.0008 | -0.0077 | 0 | 3 | 0.0000 | 0.0020 |
| routerbench | seen | 0 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0070 | 0.0024 | -0.0059 | 0 | 2 | 0.0000 | 0.0020 |
| routerbench | seen | 0 |  | 0 | frozen | handcrafted | 3 | -0.0022 | 0.0010 | -0.0019 | 0 | 0 | 0.1420 | 0.3440 |
| routerbench | seen | 0 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0002 | 0.0013 | 0.0001 | 1 | 0 | 0.2900 | 0.5300 |
| routerbench | seen | 0 |  | 0 | regression | handcrafted | 3 | -0.0036 | 0.0019 | -0.0030 | 0 | 2 | 0.0400 | 0.0460 |
| routerbench | seen | 0 |  | 0 | regression_hc | handcrafted | 3 | -0.0018 | 0.0013 | -0.0015 | 0 | 0 | 0.1140 | 0.5360 |
| routerbench | seen | 0 |  | 0 | stats | handcrafted | 3 | -0.0010 | 0.0003 | -0.0009 | 0 | 0 | 0.3140 | 0.5360 |
| routerbench | seen | 0 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0097 | 0.0017 | -0.0081 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 0 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0085 | 0.0003 | -0.0071 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 0 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0076 | 0.0014 | -0.0064 | 0 | 3 | 0.0000 | 0.0100 |
| routerbench | seen | 0 |  | 0 | task_type_theme | handcrafted | 3 | -0.0095 | 0.0010 | -0.0080 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 1 |  | 0 | combined | handcrafted | 3 | -0.0031 | 0.0011 | -0.0026 | 0 | 0 | 0.1320 | 0.1620 |
| routerbench | seen | 1 |  | 0 | contrastive | handcrafted | 3 | -0.0057 | 0.0012 | -0.0048 | 0 | 1 | 0.0220 | 0.0520 |
| routerbench | seen | 1 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0047 | 0.0007 | -0.0040 | 0 | 1 | 0.0500 | 0.1200 |
| routerbench | seen | 1 |  | 0 | frozen | handcrafted | 3 | -0.0062 | 0.0004 | -0.0052 | 0 | 1 | 0.0240 | 0.0540 |
| routerbench | seen | 1 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0021 | 0.0012 | -0.0018 | 0 | 0 | 0.1760 | 0.5320 |
| routerbench | seen | 1 |  | 0 | regression | handcrafted | 3 | -0.0066 | 0.0022 | -0.0055 | 0 | 2 | 0.0100 | 0.0300 |
| routerbench | seen | 1 |  | 0 | regression_hc | handcrafted | 3 | -0.0030 | 0.0029 | -0.0025 | 0 | 1 | 0.0240 | 0.5440 |
| routerbench | seen | 1 |  | 0 | stats | handcrafted | 3 | -0.0021 | 0.0003 | -0.0018 | 0 | 0 | 0.1100 | 0.1780 |
| routerbench | seen | 1 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0083 | 0.0018 | -0.0069 | 0 | 3 | 0.0000 | 0.0140 |
| routerbench | seen | 1 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0067 | 0.0009 | -0.0056 | 0 | 3 | 0.0120 | 0.0140 |
| routerbench | seen | 1 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0079 | 0.0016 | -0.0066 | 0 | 3 | 0.0000 | 0.0040 |
| routerbench | seen | 1 |  | 0 | task_type_theme | handcrafted | 3 | -0.0081 | 0.0017 | -0.0067 | 0 | 2 | 0.0020 | 0.0140 |
| routerbench | seen | 2 |  | 0 | combined | handcrafted | 3 | 0.0005 | 0.0002 | 0.0004 | 3 | 0 | 0.3420 | 0.5660 |
| routerbench | seen | 2 |  | 0 | contrastive | handcrafted | 3 | -0.0036 | 0.0005 | -0.0028 | 0 | 2 | 0.0180 | 0.0220 |
| routerbench | seen | 2 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0013 | 0.0014 | -0.0011 | 1 | 0 | 0.0560 | 0.3220 |
| routerbench | seen | 2 |  | 0 | frozen | handcrafted | 3 | -0.0027 | 0.0005 | -0.0021 | 0 | 1 | 0.0320 | 0.1120 |
| routerbench | seen | 2 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0009 | 0.0016 | -0.0007 | 1 | 1 | 0.0340 | 0.2240 |
| routerbench | seen | 2 |  | 0 | regression | handcrafted | 3 | -0.0016 | 0.0011 | -0.0013 | 0 | 1 | 0.0240 | 0.2780 |
| routerbench | seen | 2 |  | 0 | regression_hc | handcrafted | 3 | -0.0003 | 0.0007 | -0.0002 | 1 | 0 | 0.4300 | 0.7140 |
| routerbench | seen | 2 |  | 0 | stats | handcrafted | 3 | -0.0003 | 0.0005 | -0.0003 | 1 | 0 | 0.4960 | 0.5460 |
| routerbench | seen | 2 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0070 | 0.0016 | -0.0055 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 2 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0035 | 0.0011 | -0.0028 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 2 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0025 | 0.0019 | -0.0020 | 0 | 1 | 0.0000 | 0.2320 |
| routerbench | seen | 2 |  | 0 | task_type_theme | handcrafted | 3 | -0.0036 | 0.0008 | -0.0029 | 0 | 2 | 0.0020 | 0.0040 |
| routerbench | seen | 3 |  | 0 | combined | handcrafted | 3 | -0.0019 | 0.0019 | -0.0014 | 1 | 1 | 0.0200 | 0.4360 |
| routerbench | seen | 3 |  | 0 | contrastive | handcrafted | 3 | -0.0066 | 0.0024 | -0.0049 | 0 | 2 | 0.0020 | 0.0180 |
| routerbench | seen | 3 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0057 | 0.0015 | -0.0042 | 0 | 1 | 0.0060 | 0.0560 |
| routerbench | seen | 3 |  | 0 | frozen | handcrafted | 3 | -0.0055 | 0.0013 | -0.0041 | 0 | 1 | 0.0100 | 0.0600 |
| routerbench | seen | 3 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0014 | 0.0006 | -0.0010 | 0 | 0 | 0.3220 | 0.3940 |
| routerbench | seen | 3 |  | 0 | regression | handcrafted | 3 | -0.0055 | 0.0019 | -0.0041 | 0 | 1 | 0.0100 | 0.1040 |
| routerbench | seen | 3 |  | 0 | regression_hc | handcrafted | 3 | -0.0028 | 0.0017 | -0.0021 | 0 | 0 | 0.0580 | 0.5120 |
| routerbench | seen | 3 |  | 0 | stats | handcrafted | 3 | -0.0018 | 0.0005 | -0.0013 | 0 | 0 | 0.1380 | 0.1740 |
| routerbench | seen | 3 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0151 | 0.0017 | -0.0112 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 3 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0117 | 0.0011 | -0.0086 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 3 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0107 | 0.0003 | -0.0079 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 3 |  | 0 | task_type_theme | handcrafted | 3 | -0.0120 | 0.0010 | -0.0089 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 4 |  | 0 | combined | handcrafted | 3 | -0.0016 | 0.0018 | -0.0011 | 1 | 1 | 0.0240 | 0.4880 |
| routerbench | seen | 4 |  | 0 | contrastive | handcrafted | 3 | -0.0077 | 0.0019 | -0.0054 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 4 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0048 | 0.0017 | -0.0034 | 0 | 2 | 0.0020 | 0.0480 |
| routerbench | seen | 4 |  | 0 | frozen | handcrafted | 3 | -0.0060 | 0.0011 | -0.0042 | 0 | 2 | 0.0040 | 0.0240 |
| routerbench | seen | 4 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0018 | 0.0005 | -0.0012 | 0 | 0 | 0.2040 | 0.3540 |
| routerbench | seen | 4 |  | 0 | regression | handcrafted | 3 | -0.0030 | 0.0020 | -0.0021 | 0 | 0 | 0.0560 | 0.1820 |
| routerbench | seen | 4 |  | 0 | regression_hc | handcrafted | 3 | -0.0019 | 0.0024 | -0.0013 | 1 | 0 | 0.0680 | 0.5440 |
| routerbench | seen | 4 |  | 0 | stats | handcrafted | 3 | -0.0024 | 0.0008 | -0.0017 | 0 | 1 | 0.0380 | 0.1140 |
| routerbench | seen | 4 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0167 | 0.0024 | -0.0117 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 4 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0125 | 0.0008 | -0.0087 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 4 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0117 | 0.0005 | -0.0082 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 4 |  | 0 | task_type_theme | handcrafted | 3 | -0.0136 | 0.0011 | -0.0095 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 5 |  | 0 | combined | handcrafted | 3 | -0.0013 | 0.0011 | -0.0009 | 0 | 0 | 0.1080 | 0.7080 |
| routerbench | seen | 5 |  | 0 | contrastive | handcrafted | 3 | -0.0047 | 0.0031 | -0.0032 | 0 | 1 | 0.0120 | 0.0760 |
| routerbench | seen | 5 |  | 0 | contrastive_hc | handcrafted | 3 | -0.0030 | 0.0017 | -0.0021 | 0 | 0 | 0.0600 | 0.3640 |
| routerbench | seen | 5 |  | 0 | frozen | handcrafted | 3 | -0.0067 | 0.0037 | -0.0046 | 0 | 1 | 0.0000 | 0.0860 |
| routerbench | seen | 5 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0008 | 0.0028 | -0.0005 | 1 | 0 | 0.2060 | 0.2480 |
| routerbench | seen | 5 |  | 0 | regression | handcrafted | 3 | -0.0007 | 0.0030 | -0.0005 | 1 | 0 | 0.2500 | 0.2860 |
| routerbench | seen | 5 |  | 0 | regression_hc | handcrafted | 3 | 0.0006 | 0.0016 | 0.0004 | 2 | 0 | 0.5020 | 0.5920 |
| routerbench | seen | 5 |  | 0 | stats | handcrafted | 3 | -0.0025 | 0.0018 | -0.0017 | 0 | 0 | 0.1000 | 0.1000 |
| routerbench | seen | 5 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0274 | 0.0062 | -0.0188 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 5 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0222 | 0.0028 | -0.0152 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 5 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0218 | 0.0034 | -0.0150 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 5 |  | 0 | task_type_theme | handcrafted | 3 | -0.0221 | 0.0035 | -0.0152 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 6 |  | 0 | combined | handcrafted | 3 | -0.0003 | 0.0012 | -0.0002 | 2 | 0 | 0.1000 | 0.5460 |
| routerbench | seen | 6 |  | 0 | contrastive | handcrafted | 3 | -0.0002 | 0.0010 | -0.0001 | 1 | 0 | 0.5380 | 0.6180 |
| routerbench | seen | 6 |  | 0 | contrastive_hc | handcrafted | 3 | 0.0013 | 0.0010 | 0.0009 | 3 | 0 | 0.1920 | 0.7180 |
| routerbench | seen | 6 |  | 0 | frozen | handcrafted | 3 | -0.0040 | 0.0015 | -0.0029 | 0 | 2 | 0.0060 | 0.0400 |
| routerbench | seen | 6 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0010 | 0.0009 | -0.0007 | 0 | 0 | 0.1140 | 0.7500 |
| routerbench | seen | 6 |  | 0 | regression | handcrafted | 3 | 0.0020 | 0.0013 | 0.0014 | 3 | 0 | 0.1040 | 0.2420 |
| routerbench | seen | 6 |  | 0 | regression_hc | handcrafted | 3 | 0.0042 | 0.0017 | 0.0030 | 3 | 2 | 0.0020 | 0.0400 |
| routerbench | seen | 6 |  | 0 | stats | handcrafted | 3 | -0.0006 | 0.0011 | -0.0004 | 1 | 0 | 0.1900 | 0.4360 |
| routerbench | seen | 6 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0196 | 0.0033 | -0.0139 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 6 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0137 | 0.0010 | -0.0097 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 6 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0116 | 0.0012 | -0.0082 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 6 |  | 0 | task_type_theme | handcrafted | 3 | -0.0177 | 0.0013 | -0.0126 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 7 |  | 0 | combined | handcrafted | 3 | 0.0003 | 0.0004 | 0.0002 | 2 | 0 | 0.4240 | 0.8980 |
| routerbench | seen | 7 |  | 0 | contrastive | handcrafted | 3 | -0.0002 | 0.0006 | -0.0002 | 1 | 0 | 0.6460 | 0.7900 |
| routerbench | seen | 7 |  | 0 | contrastive_hc | handcrafted | 3 | 0.0018 | 0.0022 | 0.0013 | 2 | 0 | 0.0540 | 0.2160 |
| routerbench | seen | 7 |  | 0 | frozen | handcrafted | 3 | -0.0062 | 0.0036 | -0.0044 | 0 | 2 | 0.0000 | 0.0080 |
| routerbench | seen | 7 |  | 0 | handcrafted_nik | handcrafted | 3 | 0.0000 | 0.0008 | 0.0000 | 1 | 0 | 0.6220 | 0.6360 |
| routerbench | seen | 7 |  | 0 | regression | handcrafted | 3 | 0.0019 | 0.0023 | 0.0014 | 2 | 1 | 0.0180 | 0.5760 |
| routerbench | seen | 7 |  | 0 | regression_hc | handcrafted | 3 | 0.0039 | 0.0011 | 0.0028 | 3 | 1 | 0.0060 | 0.0800 |
| routerbench | seen | 7 |  | 0 | stats | handcrafted | 3 | -0.0010 | 0.0001 | -0.0007 | 0 | 0 | 0.5580 | 0.6400 |
| routerbench | seen | 7 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0304 | 0.0082 | -0.0218 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 7 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0234 | 0.0082 | -0.0168 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 7 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0240 | 0.0102 | -0.0172 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 7 |  | 0 | task_type_theme | handcrafted | 3 | -0.0214 | 0.0008 | -0.0154 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 8 |  | 0 | combined | handcrafted | 3 | 0.0036 | 0.0027 | 0.0026 | 3 | 1 | 0.0000 | 0.1080 |
| routerbench | seen | 8 |  | 0 | contrastive | handcrafted | 3 | 0.0013 | 0.0008 | 0.0009 | 3 | 0 | 0.3320 | 0.4440 |
| routerbench | seen | 8 |  | 0 | contrastive_hc | handcrafted | 3 | 0.0050 | 0.0005 | 0.0036 | 3 | 3 | 0.0040 | 0.0120 |
| routerbench | seen | 8 |  | 0 | frozen | handcrafted | 3 | -0.0031 | 0.0004 | -0.0022 | 0 | 0 | 0.1280 | 0.1880 |
| routerbench | seen | 8 |  | 0 | handcrafted_nik | handcrafted | 3 | -0.0024 | 0.0020 | -0.0017 | 1 | 1 | 0.0360 | 0.2240 |
| routerbench | seen | 8 |  | 0 | regression | handcrafted | 3 | 0.0037 | 0.0015 | 0.0027 | 3 | 1 | 0.0060 | 0.0580 |
| routerbench | seen | 8 |  | 0 | regression_hc | handcrafted | 3 | 0.0057 | 0.0005 | 0.0041 | 3 | 3 | 0.0000 | 0.0020 |
| routerbench | seen | 8 |  | 0 | stats | handcrafted | 3 | -0.0033 | 0.0003 | -0.0024 | 0 | 0 | 0.0820 | 0.1020 |
| routerbench | seen | 8 |  | 0 | task_type_L1 | handcrafted | 3 | -0.0478 | 0.0033 | -0.0343 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 8 |  | 0 | task_type_L12 | handcrafted | 3 | -0.0398 | 0.0114 | -0.0284 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 8 |  | 0 | task_type_L2 | handcrafted | 3 | -0.0373 | 0.0122 | -0.0267 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | seen | 8 |  | 0 | task_type_theme | handcrafted | 3 | -0.0355 | 0.0048 | -0.0254 | 0 | 3 | 0.0000 | 0.0000 |

## Unseen setting

| benchmark | setting | instance | new_model | n_probes | a | b | n | d_gain_mean | d_gain_sd | d_A_mean | wins | ci_excludes_0 | min_p | median_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | combined | handcrafted | 3 | -0.0009 | 0.0031 | -0.0007 | 1 | 0 | 0.0320 | 0.2240 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | contrastive | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | contrastive_hc | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | frozen | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.1960 | 0.2220 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | handcrafted_nik | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.1220 | 0.3100 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | regression | handcrafted | 3 | -0.0011 | 0.0028 | -0.0010 | 1 | 0 | 0.0180 | 0.0420 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | regression_hc | handcrafted | 3 | -0.0008 | 0.0011 | -0.0007 | 0 | 0 | 0.0140 | 0.5940 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | stats | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.0020 | 0.0760 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | task_type_L1 | handcrafted | 3 | 0.0003 | 0.0044 | 0.0002 | 1 | 0 | 0.0000 | 0.0380 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | task_type_L12 | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.0080 | 0.0120 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | task_type_L2 | handcrafted | 3 | -0.0017 | 0.0024 | -0.0015 | 0 | 0 | 0.0000 | 0.0380 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 5 | task_type_theme | handcrafted | 3 | 0.0034 | 0.0017 | 0.0030 | 3 | 0 | 0.2720 | 0.5700 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | combined | handcrafted | 3 | -0.0032 | 0.0041 | -0.0028 | 1 | 0 | 0.0760 | 0.8500 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | contrastive | handcrafted | 3 | -0.0076 | 0.0054 | -0.0067 | 0 | 1 | 0.0060 | 0.2520 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | contrastive_hc | handcrafted | 3 | -0.0079 | 0.0049 | -0.0069 | 0 | 1 | 0.0180 | 0.1280 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | frozen | handcrafted | 3 | -0.0059 | 0.0067 | -0.0051 | 0 | 1 | 0.0000 | 0.5920 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | handcrafted_nik | handcrafted | 3 | -0.0001 | 0.0028 | -0.0001 | 1 | 0 | 0.0040 | 0.5960 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | regression | handcrafted | 3 | -0.0084 | 0.0060 | -0.0074 | 0 | 1 | 0.0400 | 0.0700 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | regression_hc | handcrafted | 3 | -0.0069 | 0.0045 | -0.0060 | 0 | 0 | 0.0780 | 0.5040 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | stats | handcrafted | 3 | -0.0044 | 0.0027 | -0.0039 | 0 | 0 | 0.0580 | 0.1900 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | task_type_L1 | handcrafted | 3 | -0.0032 | 0.0053 | -0.0028 | 1 | 0 | 0.0640 | 0.0740 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | task_type_L12 | handcrafted | 3 | -0.0079 | 0.0058 | -0.0069 | 1 | 2 | 0.0240 | 0.0320 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | task_type_L2 | handcrafted | 3 | -0.0090 | 0.0047 | -0.0079 | 0 | 2 | 0.0020 | 0.0040 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 50 | task_type_theme | handcrafted | 3 | 0.0127 | 0.0037 | 0.0111 | 3 | 1 | 0.0000 | 0.0720 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | combined | handcrafted | 3 | 0.0019 | 0.0037 | 0.0016 | 2 | 0 | 0.2100 | 0.5300 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | contrastive | handcrafted | 3 | -0.0082 | 0.0069 | -0.0071 | 0 | 1 | 0.0080 | 0.0940 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | contrastive_hc | handcrafted | 3 | -0.0021 | 0.0018 | -0.0019 | 1 | 0 | 0.4800 | 0.5760 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | frozen | handcrafted | 3 | -0.0042 | 0.0036 | -0.0036 | 1 | 0 | 0.1440 | 0.3000 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | handcrafted_nik | handcrafted | 3 | -0.0000 | 0.0034 | -0.0000 | 1 | 0 | 0.4420 | 0.4700 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | regression | handcrafted | 3 | -0.0060 | 0.0045 | -0.0052 | 0 | 0 | 0.1380 | 0.2180 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | regression_hc | handcrafted | 3 | -0.0029 | 0.0031 | -0.0026 | 0 | 0 | 0.3240 | 0.7320 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | stats | handcrafted | 3 | -0.0051 | 0.0049 | -0.0045 | 0 | 0 | 0.0880 | 0.3060 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | task_type_L1 | handcrafted | 3 | -0.0008 | 0.0058 | -0.0007 | 1 | 0 | 0.1240 | 0.2260 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | task_type_L12 | handcrafted | 3 | -0.0024 | 0.0062 | -0.0021 | 1 | 1 | 0.0260 | 0.1480 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | task_type_L2 | handcrafted | 3 | -0.0041 | 0.0062 | -0.0035 | 1 | 1 | 0.0140 | 0.2680 |
| llmrouterbench | unseen | 0 | claude-sonnet-4 | 500 | task_type_theme | handcrafted | 3 | 0.0072 | 0.0053 | 0.0063 | 2 | 0 | 0.0000 | 0.1040 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | combined | handcrafted | 3 | 0.0021 | 0.0020 | 0.0018 | 2 | 1 | 0.0220 | 0.1220 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | contrastive | handcrafted | 3 | 0.0150 | 0.0035 | 0.0123 | 3 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | contrastive_hc | handcrafted | 3 | 0.0161 | 0.0038 | 0.0132 | 3 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | frozen | handcrafted | 3 | -0.0008 | 0.0014 | -0.0006 | 1 | 0 | 0.6240 | 0.6360 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | handcrafted_nik | handcrafted | 3 | 0.0272 | 0.0066 | 0.0222 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | regression | handcrafted | 3 | 0.0246 | 0.0047 | 0.0201 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | regression_hc | handcrafted | 3 | 0.0237 | 0.0040 | 0.0193 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | stats | handcrafted | 3 | -0.0023 | 0.0041 | -0.0019 | 1 | 0 | 0.0940 | 0.4060 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | task_type_L1 | handcrafted | 3 | 0.0217 | 0.0067 | 0.0177 | 3 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | task_type_L12 | handcrafted | 3 | 0.0199 | 0.0044 | 0.0163 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | task_type_L2 | handcrafted | 3 | 0.0233 | 0.0034 | 0.0190 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 5 | task_type_theme | handcrafted | 3 | 0.0201 | 0.0046 | 0.0164 | 3 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | combined | handcrafted | 3 | 0.0032 | 0.0019 | 0.0026 | 3 | 1 | 0.0020 | 0.2320 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | contrastive | handcrafted | 3 | 0.0135 | 0.0040 | 0.0110 | 3 | 3 | 0.0000 | 0.0180 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | contrastive_hc | handcrafted | 3 | 0.0156 | 0.0048 | 0.0128 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | frozen | handcrafted | 3 | 0.0009 | 0.0006 | 0.0007 | 3 | 0 | 0.5380 | 0.7200 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | handcrafted_nik | handcrafted | 3 | 0.0227 | 0.0028 | 0.0185 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | regression | handcrafted | 3 | 0.0231 | 0.0051 | 0.0188 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | regression_hc | handcrafted | 3 | 0.0218 | 0.0013 | 0.0178 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | stats | handcrafted | 3 | 0.0024 | 0.0022 | 0.0019 | 2 | 0 | 0.1340 | 0.4560 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | task_type_L1 | handcrafted | 3 | 0.0195 | 0.0058 | 0.0160 | 3 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | task_type_L12 | handcrafted | 3 | 0.0174 | 0.0037 | 0.0142 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | task_type_L2 | handcrafted | 3 | 0.0215 | 0.0024 | 0.0176 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 50 | task_type_theme | handcrafted | 3 | 0.0175 | 0.0019 | 0.0143 | 3 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | combined | handcrafted | 3 | 0.0034 | 0.0013 | 0.0028 | 3 | 1 | 0.0020 | 0.1460 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | contrastive | handcrafted | 3 | 0.0132 | 0.0046 | 0.0107 | 3 | 2 | 0.0000 | 0.0200 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | contrastive_hc | handcrafted | 3 | 0.0158 | 0.0052 | 0.0129 | 3 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | frozen | handcrafted | 3 | 0.0011 | 0.0007 | 0.0009 | 3 | 0 | 0.5540 | 0.6900 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | handcrafted_nik | handcrafted | 3 | 0.0230 | 0.0031 | 0.0188 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | regression | handcrafted | 3 | 0.0229 | 0.0056 | 0.0187 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | regression_hc | handcrafted | 3 | 0.0221 | 0.0019 | 0.0180 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | stats | handcrafted | 3 | 0.0023 | 0.0027 | 0.0019 | 2 | 0 | 0.0980 | 0.3900 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | task_type_L1 | handcrafted | 3 | 0.0197 | 0.0060 | 0.0160 | 3 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | task_type_L12 | handcrafted | 3 | 0.0182 | 0.0042 | 0.0149 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | task_type_L2 | handcrafted | 3 | 0.0218 | 0.0028 | 0.0178 | 3 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 1 | deepseek-r1-0528 | 500 | task_type_theme | handcrafted | 3 | 0.0175 | 0.0024 | 0.0143 | 3 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | combined | handcrafted | 3 | 0.0024 | 0.0008 | 0.0018 | 3 | 0 | 0.1500 | 0.1720 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | contrastive | handcrafted | 3 | -0.0106 | 0.0059 | -0.0082 | 0 | 2 | 0.0040 | 0.0340 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | contrastive_hc | handcrafted | 3 | -0.0085 | 0.0073 | -0.0066 | 1 | 2 | 0.0040 | 0.0320 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | frozen | handcrafted | 3 | 0.0023 | 0.0054 | 0.0018 | 2 | 0 | 0.0680 | 0.5240 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | handcrafted_nik | handcrafted | 3 | -0.0049 | 0.0063 | -0.0038 | 1 | 0 | 0.0620 | 0.1740 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | regression | handcrafted | 3 | -0.0106 | 0.0084 | -0.0082 | 1 | 2 | 0.0020 | 0.0400 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | regression_hc | handcrafted | 3 | -0.0049 | 0.0067 | -0.0038 | 1 | 0 | 0.0920 | 0.2380 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | stats | handcrafted | 3 | 0.0058 | 0.0023 | 0.0045 | 3 | 0 | 0.0860 | 0.2100 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | task_type_L1 | handcrafted | 3 | -0.0131 | 0.0086 | -0.0101 | 0 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | task_type_L12 | handcrafted | 3 | -0.0098 | 0.0075 | -0.0075 | 1 | 2 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | task_type_L2 | handcrafted | 3 | -0.0148 | 0.0057 | -0.0114 | 0 | 2 | 0.0060 | 0.0140 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 5 | task_type_theme | handcrafted | 3 | -0.0066 | 0.0057 | -0.0051 | 1 | 1 | 0.0220 | 0.0620 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | combined | handcrafted | 3 | 0.0031 | 0.0001 | 0.0024 | 3 | 0 | 0.1400 | 0.1960 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | contrastive | handcrafted | 3 | -0.0095 | 0.0015 | -0.0073 | 0 | 1 | 0.0160 | 0.0720 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | contrastive_hc | handcrafted | 3 | -0.0061 | 0.0044 | -0.0047 | 0 | 1 | 0.0180 | 0.4060 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | frozen | handcrafted | 3 | 0.0014 | 0.0033 | 0.0010 | 2 | 0 | 0.3540 | 0.4780 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | handcrafted_nik | handcrafted | 3 | -0.0047 | 0.0017 | -0.0036 | 0 | 0 | 0.1840 | 0.3400 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | regression | handcrafted | 3 | -0.0089 | 0.0013 | -0.0068 | 0 | 0 | 0.0640 | 0.1280 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | regression_hc | handcrafted | 3 | -0.0044 | 0.0008 | -0.0034 | 0 | 0 | 0.3320 | 0.4140 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | stats | handcrafted | 3 | 0.0050 | 0.0063 | 0.0039 | 2 | 1 | 0.0100 | 0.4340 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | task_type_L1 | handcrafted | 3 | -0.0110 | 0.0025 | -0.0085 | 0 | 1 | 0.0100 | 0.0840 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | task_type_L12 | handcrafted | 3 | -0.0090 | 0.0031 | -0.0070 | 0 | 1 | 0.0120 | 0.0760 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | task_type_L2 | handcrafted | 3 | -0.0129 | 0.0027 | -0.0100 | 0 | 1 | 0.0080 | 0.0580 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 50 | task_type_theme | handcrafted | 3 | -0.0055 | 0.0012 | -0.0043 | 0 | 0 | 0.1240 | 0.1300 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | combined | handcrafted | 3 | 0.0026 | 0.0004 | 0.0020 | 3 | 0 | 0.1540 | 0.2480 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | contrastive | handcrafted | 3 | -0.0121 | 0.0027 | -0.0093 | 0 | 2 | 0.0020 | 0.0040 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | contrastive_hc | handcrafted | 3 | -0.0090 | 0.0027 | -0.0069 | 0 | 1 | 0.0140 | 0.1000 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | frozen | handcrafted | 3 | 0.0035 | 0.0022 | 0.0027 | 3 | 0 | 0.1560 | 0.4340 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | handcrafted_nik | handcrafted | 3 | -0.0064 | 0.0013 | -0.0049 | 0 | 0 | 0.1660 | 0.2160 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | regression | handcrafted | 3 | -0.0119 | 0.0033 | -0.0092 | 0 | 1 | 0.0040 | 0.1020 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | regression_hc | handcrafted | 3 | -0.0071 | 0.0020 | -0.0055 | 0 | 0 | 0.1280 | 0.2840 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | stats | handcrafted | 3 | 0.0086 | 0.0052 | 0.0066 | 3 | 1 | 0.0040 | 0.2640 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | task_type_L1 | handcrafted | 3 | -0.0145 | 0.0018 | -0.0112 | 0 | 3 | 0.0060 | 0.0100 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | task_type_L12 | handcrafted | 3 | -0.0124 | 0.0017 | -0.0096 | 0 | 3 | 0.0040 | 0.0060 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | task_type_L2 | handcrafted | 3 | -0.0164 | 0.0016 | -0.0127 | 0 | 3 | 0.0060 | 0.0100 |
| llmrouterbench | unseen | 2 | gemini-2.5-flash | 500 | task_type_theme | handcrafted | 3 | -0.0062 | 0.0013 | -0.0048 | 0 | 0 | 0.0900 | 0.1840 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | combined | handcrafted | 3 | 0.0022 | 0.0009 | 0.0017 | 3 | 0 | 0.0520 | 0.4320 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | contrastive | handcrafted | 3 | -0.0145 | 0.0123 | -0.0111 | 1 | 2 | 0.0000 | 0.0120 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | contrastive_hc | handcrafted | 3 | -0.0166 | 0.0089 | -0.0127 | 0 | 2 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | frozen | handcrafted | 3 | -0.0004 | 0.0015 | -0.0003 | 1 | 0 | 0.6340 | 0.7300 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | handcrafted_nik | handcrafted | 3 | -0.0201 | 0.0074 | -0.0153 | 0 | 3 | 0.0000 | 0.0060 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | regression | handcrafted | 3 | -0.0218 | 0.0093 | -0.0166 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | regression_hc | handcrafted | 3 | -0.0198 | 0.0086 | -0.0151 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | stats | handcrafted | 3 | -0.0002 | 0.0034 | -0.0001 | 2 | 0 | 0.0840 | 0.5180 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | task_type_L1 | handcrafted | 3 | -0.0167 | 0.0088 | -0.0127 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | task_type_L12 | handcrafted | 3 | -0.0096 | 0.0069 | -0.0073 | 0 | 1 | 0.0000 | 0.0840 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | task_type_L2 | handcrafted | 3 | -0.0237 | 0.0096 | -0.0181 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 5 | task_type_theme | handcrafted | 3 | -0.0220 | 0.0089 | -0.0168 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | combined | handcrafted | 3 | 0.0017 | 0.0012 | 0.0013 | 3 | 0 | 0.1180 | 0.1820 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | contrastive | handcrafted | 3 | -0.0279 | 0.0069 | -0.0213 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | contrastive_hc | handcrafted | 3 | -0.0296 | 0.0036 | -0.0226 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | frozen | handcrafted | 3 | 0.0003 | 0.0003 | 0.0002 | 3 | 0 | 0.8760 | 0.9420 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | handcrafted_nik | handcrafted | 3 | -0.0339 | 0.0051 | -0.0258 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | regression | handcrafted | 3 | -0.0323 | 0.0049 | -0.0246 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | regression_hc | handcrafted | 3 | -0.0290 | 0.0042 | -0.0221 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | stats | handcrafted | 3 | -0.0066 | 0.0015 | -0.0050 | 0 | 1 | 0.0100 | 0.0560 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | task_type_L1 | handcrafted | 3 | -0.0145 | 0.0042 | -0.0111 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | task_type_L12 | handcrafted | 3 | -0.0059 | 0.0011 | -0.0045 | 0 | 1 | 0.0340 | 0.1080 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | task_type_L2 | handcrafted | 3 | -0.0200 | 0.0031 | -0.0152 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 50 | task_type_theme | handcrafted | 3 | -0.0277 | 0.0099 | -0.0212 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | combined | handcrafted | 3 | 0.0017 | 0.0015 | 0.0013 | 2 | 0 | 0.0520 | 0.2540 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | contrastive | handcrafted | 3 | -0.0275 | 0.0076 | -0.0209 | 0 | 3 | 0.0000 | 0.0060 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | contrastive_hc | handcrafted | 3 | -0.0276 | 0.0037 | -0.0210 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | frozen | handcrafted | 3 | -0.0004 | 0.0009 | -0.0003 | 1 | 0 | 0.7920 | 0.8360 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | handcrafted_nik | handcrafted | 3 | -0.0189 | 0.0015 | -0.0144 | 0 | 3 | 0.0020 | 0.0040 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | regression | handcrafted | 3 | -0.0287 | 0.0039 | -0.0219 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | regression_hc | handcrafted | 3 | -0.0243 | 0.0031 | -0.0185 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | stats | handcrafted | 3 | -0.0048 | 0.0003 | -0.0036 | 0 | 0 | 0.0740 | 0.0840 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | task_type_L1 | handcrafted | 3 | -0.0069 | 0.0047 | -0.0052 | 0 | 1 | 0.0000 | 0.1480 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | task_type_L12 | handcrafted | 3 | -0.0046 | 0.0022 | -0.0035 | 0 | 1 | 0.0360 | 0.0840 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | task_type_L2 | handcrafted | 3 | -0.0119 | 0.0036 | -0.0090 | 0 | 2 | 0.0000 | 0.0120 |
| llmrouterbench | unseen | 3 | gemini-2.5-pro | 500 | task_type_theme | handcrafted | 3 | -0.0197 | 0.0036 | -0.0150 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | combined | handcrafted | 3 | -0.0006 | 0.0012 | -0.0004 | 1 | 0 | 0.4360 | 0.4500 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | contrastive | handcrafted | 3 | -0.0161 | 0.0109 | -0.0122 | 0 | 2 | 0.0000 | 0.0280 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | contrastive_hc | handcrafted | 3 | -0.0083 | 0.0096 | -0.0063 | 1 | 1 | 0.0000 | 0.3640 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | frozen | handcrafted | 3 | -0.0022 | 0.0089 | -0.0016 | 1 | 1 | 0.0060 | 0.0780 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | handcrafted_nik | handcrafted | 3 | -0.0065 | 0.0086 | -0.0049 | 1 | 1 | 0.0000 | 0.3440 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | regression | handcrafted | 3 | -0.0135 | 0.0087 | -0.0102 | 0 | 2 | 0.0000 | 0.0240 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | regression_hc | handcrafted | 3 | -0.0110 | 0.0064 | -0.0084 | 0 | 1 | 0.0020 | 0.2860 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | stats | handcrafted | 3 | -0.0071 | 0.0064 | -0.0054 | 1 | 2 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | task_type_L1 | handcrafted | 3 | -0.0023 | 0.0069 | -0.0017 | 1 | 1 | 0.0080 | 0.2420 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | task_type_L12 | handcrafted | 3 | 0.0006 | 0.0058 | 0.0004 | 2 | 0 | 0.0700 | 0.2420 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | task_type_L2 | handcrafted | 3 | -0.0065 | 0.0091 | -0.0049 | 1 | 1 | 0.0000 | 0.3080 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 5 | task_type_theme | handcrafted | 3 | -0.0089 | 0.0034 | -0.0067 | 0 | 1 | 0.0020 | 0.2300 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | combined | handcrafted | 3 | 0.0023 | 0.0020 | 0.0017 | 2 | 1 | 0.0320 | 0.0700 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | contrastive | handcrafted | 3 | -0.0231 | 0.0072 | -0.0175 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | contrastive_hc | handcrafted | 3 | -0.0182 | 0.0088 | -0.0138 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | frozen | handcrafted | 3 | -0.0084 | 0.0018 | -0.0064 | 0 | 2 | 0.0200 | 0.0420 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | handcrafted_nik | handcrafted | 3 | -0.0147 | 0.0036 | -0.0112 | 0 | 3 | 0.0000 | 0.0080 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | regression | handcrafted | 3 | -0.0188 | 0.0039 | -0.0143 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | regression_hc | handcrafted | 3 | -0.0153 | 0.0070 | -0.0116 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | stats | handcrafted | 3 | -0.0069 | 0.0035 | -0.0053 | 0 | 1 | 0.0080 | 0.2480 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | task_type_L1 | handcrafted | 3 | -0.0059 | 0.0050 | -0.0045 | 0 | 1 | 0.0020 | 0.1500 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | task_type_L12 | handcrafted | 3 | -0.0044 | 0.0020 | -0.0034 | 0 | 0 | 0.0820 | 0.3160 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | task_type_L2 | handcrafted | 3 | -0.0206 | 0.0078 | -0.0157 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 50 | task_type_theme | handcrafted | 3 | -0.0094 | 0.0012 | -0.0072 | 0 | 1 | 0.0140 | 0.0840 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | combined | handcrafted | 3 | 0.0006 | 0.0020 | 0.0004 | 1 | 0 | 0.0680 | 0.6080 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | contrastive | handcrafted | 3 | -0.0239 | 0.0047 | -0.0182 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | contrastive_hc | handcrafted | 3 | -0.0201 | 0.0050 | -0.0153 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | frozen | handcrafted | 3 | -0.0036 | 0.0028 | -0.0027 | 0 | 0 | 0.1620 | 0.4220 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | handcrafted_nik | handcrafted | 3 | -0.0149 | 0.0057 | -0.0113 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | regression | handcrafted | 3 | -0.0217 | 0.0047 | -0.0165 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | regression_hc | handcrafted | 3 | -0.0175 | 0.0041 | -0.0133 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | stats | handcrafted | 3 | -0.0008 | 0.0039 | -0.0006 | 2 | 0 | 0.1580 | 0.4700 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | task_type_L1 | handcrafted | 3 | -0.0085 | 0.0046 | -0.0064 | 0 | 2 | 0.0020 | 0.0100 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | task_type_L12 | handcrafted | 3 | -0.0094 | 0.0012 | -0.0071 | 0 | 2 | 0.0200 | 0.0220 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | task_type_L2 | handcrafted | 3 | -0.0188 | 0.0061 | -0.0143 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 4 | qwen3-235b-a22b-2507 | 500 | task_type_theme | handcrafted | 3 | -0.0087 | 0.0034 | -0.0066 | 0 | 1 | 0.0020 | 0.0760 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | combined | handcrafted | 3 | -0.0002 | 0.0013 | -0.0001 | 1 | 0 | 0.3720 | 0.4620 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | contrastive | handcrafted | 3 | -0.0436 | 0.0017 | -0.0325 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | contrastive_hc | handcrafted | 3 | -0.0422 | 0.0045 | -0.0314 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | frozen | handcrafted | 3 | -0.0062 | 0.0024 | -0.0046 | 0 | 1 | 0.0140 | 0.1860 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | handcrafted_nik | handcrafted | 3 | -0.0214 | 0.0039 | -0.0159 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | regression | handcrafted | 3 | -0.0316 | 0.0064 | -0.0235 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | regression_hc | handcrafted | 3 | -0.0286 | 0.0030 | -0.0213 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | stats | handcrafted | 3 | -0.0001 | 0.0025 | -0.0001 | 1 | 0 | 0.1980 | 0.4220 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | task_type_L1 | handcrafted | 3 | -0.0311 | 0.0016 | -0.0231 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | task_type_L12 | handcrafted | 3 | -0.0253 | 0.0025 | -0.0188 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | task_type_L2 | handcrafted | 3 | -0.0360 | 0.0028 | -0.0268 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 5 | task_type_theme | handcrafted | 3 | -0.0189 | 0.0043 | -0.0140 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | combined | handcrafted | 3 | 0.0027 | 0.0026 | 0.0020 | 2 | 1 | 0.0080 | 0.1620 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | contrastive | handcrafted | 3 | -0.0187 | 0.0110 | -0.0139 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | contrastive_hc | handcrafted | 3 | -0.0168 | 0.0120 | -0.0125 | 0 | 2 | 0.0000 | 0.0140 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | frozen | handcrafted | 3 | 0.0050 | 0.0055 | 0.0037 | 3 | 1 | 0.0020 | 0.6960 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | handcrafted_nik | handcrafted | 3 | -0.0098 | 0.0066 | -0.0073 | 0 | 1 | 0.0000 | 0.1780 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | regression | handcrafted | 3 | -0.0099 | 0.0059 | -0.0073 | 0 | 1 | 0.0080 | 0.0700 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | regression_hc | handcrafted | 3 | -0.0057 | 0.0087 | -0.0043 | 2 | 1 | 0.0020 | 0.9300 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | stats | handcrafted | 3 | 0.0026 | 0.0045 | 0.0019 | 2 | 0 | 0.1380 | 0.3160 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | task_type_L1 | handcrafted | 3 | -0.0105 | 0.0064 | -0.0078 | 0 | 1 | 0.0000 | 0.1340 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | task_type_L12 | handcrafted | 3 | -0.0087 | 0.0076 | -0.0065 | 1 | 1 | 0.0000 | 0.1060 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | task_type_L2 | handcrafted | 3 | -0.0200 | 0.0108 | -0.0149 | 0 | 2 | 0.0000 | 0.0100 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 50 | task_type_theme | handcrafted | 3 | 0.0022 | 0.0064 | 0.0016 | 2 | 0 | 0.1200 | 0.1380 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | combined | handcrafted | 3 | 0.0015 | 0.0021 | 0.0011 | 2 | 0 | 0.1120 | 0.5380 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | contrastive | handcrafted | 3 | -0.0298 | 0.0015 | -0.0222 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | contrastive_hc | handcrafted | 3 | -0.0273 | 0.0016 | -0.0204 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | frozen | handcrafted | 3 | 0.0032 | 0.0045 | 0.0024 | 2 | 0 | 0.1160 | 0.2620 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | handcrafted_nik | handcrafted | 3 | -0.0154 | 0.0035 | -0.0115 | 0 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | regression | handcrafted | 3 | -0.0192 | 0.0084 | -0.0143 | 0 | 3 | 0.0000 | 0.0100 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | regression_hc | handcrafted | 3 | -0.0164 | 0.0053 | -0.0122 | 0 | 3 | 0.0000 | 0.0160 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | stats | handcrafted | 3 | 0.0095 | 0.0022 | 0.0071 | 3 | 2 | 0.0040 | 0.0480 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | task_type_L1 | handcrafted | 3 | -0.0153 | 0.0017 | -0.0114 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | task_type_L12 | handcrafted | 3 | -0.0154 | 0.0020 | -0.0115 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | task_type_L2 | handcrafted | 3 | -0.0313 | 0.0029 | -0.0233 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 5 | qwen3-235b-a22b-thinking-2507 | 500 | task_type_theme | handcrafted | 3 | 0.0003 | 0.0066 | 0.0002 | 1 | 0 | 0.1240 | 0.1280 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | combined | handcrafted | 3 | -0.0012 | 0.0006 | -0.0009 | 0 | 0 | 0.4080 | 0.4840 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | contrastive | handcrafted | 3 | -0.0571 | 0.0044 | -0.0419 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | contrastive_hc | handcrafted | 3 | -0.0579 | 0.0017 | -0.0424 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | frozen | handcrafted | 3 | -0.0083 | 0.0031 | -0.0061 | 0 | 1 | 0.0000 | 0.1140 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | handcrafted_nik | handcrafted | 3 | -0.0185 | 0.0026 | -0.0136 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | regression | handcrafted | 3 | -0.0497 | 0.0070 | -0.0364 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | regression_hc | handcrafted | 3 | -0.0503 | 0.0059 | -0.0369 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | stats | handcrafted | 3 | -0.0013 | 0.0015 | -0.0010 | 1 | 0 | 0.3220 | 0.4660 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | task_type_L1 | handcrafted | 3 | -0.0319 | 0.0058 | -0.0234 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | task_type_L12 | handcrafted | 3 | -0.0276 | 0.0048 | -0.0203 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | task_type_L2 | handcrafted | 3 | -0.0514 | 0.0063 | -0.0377 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 5 | task_type_theme | handcrafted | 3 | -0.0141 | 0.0019 | -0.0104 | 0 | 3 | 0.0080 | 0.0120 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | combined | handcrafted | 3 | -0.0008 | 0.0007 | -0.0006 | 0 | 0 | 0.3300 | 0.9100 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | contrastive | handcrafted | 3 | -0.0545 | 0.0034 | -0.0399 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | contrastive_hc | handcrafted | 3 | -0.0560 | 0.0048 | -0.0410 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | frozen | handcrafted | 3 | -0.0056 | 0.0011 | -0.0041 | 0 | 0 | 0.1100 | 0.2100 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | handcrafted_nik | handcrafted | 3 | -0.0181 | 0.0012 | -0.0133 | 0 | 3 | 0.0020 | 0.0020 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | regression | handcrafted | 3 | -0.0516 | 0.0041 | -0.0378 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | regression_hc | handcrafted | 3 | -0.0505 | 0.0052 | -0.0370 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | stats | handcrafted | 3 | 0.0018 | 0.0021 | 0.0013 | 2 | 0 | 0.3540 | 0.4360 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | task_type_L1 | handcrafted | 3 | -0.0311 | 0.0066 | -0.0228 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | task_type_L12 | handcrafted | 3 | -0.0273 | 0.0063 | -0.0201 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | task_type_L2 | handcrafted | 3 | -0.0499 | 0.0020 | -0.0366 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 50 | task_type_theme | handcrafted | 3 | -0.0104 | 0.0011 | -0.0076 | 0 | 2 | 0.0200 | 0.0420 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | combined | handcrafted | 3 | -0.0014 | 0.0008 | -0.0010 | 0 | 0 | 0.3360 | 0.3500 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | contrastive | handcrafted | 3 | -0.0576 | 0.0041 | -0.0423 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | contrastive_hc | handcrafted | 3 | -0.0575 | 0.0021 | -0.0422 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | frozen | handcrafted | 3 | -0.0082 | 0.0027 | -0.0060 | 0 | 1 | 0.0020 | 0.1060 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | handcrafted_nik | handcrafted | 3 | -0.0183 | 0.0024 | -0.0134 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | regression | handcrafted | 3 | -0.0494 | 0.0072 | -0.0363 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | regression_hc | handcrafted | 3 | -0.0480 | 0.0079 | -0.0352 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | stats | handcrafted | 3 | -0.0018 | 0.0018 | -0.0013 | 1 | 0 | 0.2300 | 0.3120 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | task_type_L1 | handcrafted | 3 | -0.0273 | 0.0095 | -0.0200 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | task_type_L12 | handcrafted | 3 | -0.0244 | 0.0075 | -0.0179 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | task_type_L2 | handcrafted | 3 | -0.0450 | 0.0068 | -0.0330 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 6 | intern-s1 | 500 | task_type_theme | handcrafted | 3 | -0.0146 | 0.0022 | -0.0107 | 0 | 3 | 0.0060 | 0.0060 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | combined | handcrafted | 3 | -0.0002 | 0.0030 | -0.0001 | 2 | 1 | 0.0380 | 0.2420 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | contrastive | handcrafted | 3 | -0.0215 | 0.0249 | -0.0156 | 1 | 2 | 0.0000 | 0.0220 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | contrastive_hc | handcrafted | 3 | -0.0205 | 0.0246 | -0.0148 | 0 | 1 | 0.0000 | 0.2620 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | frozen | handcrafted | 3 | -0.0063 | 0.0039 | -0.0045 | 0 | 1 | 0.0020 | 0.3520 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | handcrafted_nik | handcrafted | 3 | -0.0131 | 0.0163 | -0.0095 | 1 | 1 | 0.0000 | 0.2620 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | regression | handcrafted | 3 | -0.0203 | 0.0223 | -0.0147 | 0 | 1 | 0.0000 | 0.1080 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | regression_hc | handcrafted | 3 | -0.0154 | 0.0180 | -0.0111 | 0 | 1 | 0.0000 | 0.3760 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | stats | handcrafted | 3 | -0.0018 | 0.0010 | -0.0013 | 0 | 0 | 0.2720 | 0.5880 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | task_type_L1 | handcrafted | 3 | -0.0158 | 0.0138 | -0.0115 | 0 | 3 | 0.0000 | 0.0280 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | task_type_L12 | handcrafted | 3 | -0.0133 | 0.0110 | -0.0096 | 0 | 2 | 0.0000 | 0.0380 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | task_type_L2 | handcrafted | 3 | -0.0188 | 0.0227 | -0.0136 | 0 | 1 | 0.0000 | 0.3460 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 5 | task_type_theme | handcrafted | 3 | -0.0124 | 0.0138 | -0.0090 | 1 | 1 | 0.0000 | 0.1620 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | combined | handcrafted | 3 | 0.0047 | 0.0009 | 0.0034 | 3 | 0 | 0.0580 | 0.1480 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | contrastive | handcrafted | 3 | -0.0142 | 0.0089 | -0.0103 | 0 | 2 | 0.0000 | 0.0200 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | contrastive_hc | handcrafted | 3 | -0.0122 | 0.0055 | -0.0088 | 0 | 2 | 0.0080 | 0.0160 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | frozen | handcrafted | 3 | 0.0014 | 0.0041 | 0.0010 | 1 | 0 | 0.1540 | 0.6600 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | handcrafted_nik | handcrafted | 3 | -0.0113 | 0.0024 | -0.0082 | 0 | 1 | 0.0180 | 0.1220 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | regression | handcrafted | 3 | -0.0139 | 0.0062 | -0.0100 | 0 | 2 | 0.0020 | 0.0040 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | regression_hc | handcrafted | 3 | -0.0090 | 0.0037 | -0.0065 | 0 | 1 | 0.0300 | 0.1620 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | stats | handcrafted | 3 | -0.0024 | 0.0028 | -0.0017 | 1 | 0 | 0.2920 | 0.3160 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | task_type_L1 | handcrafted | 3 | -0.0118 | 0.0014 | -0.0085 | 0 | 3 | 0.0060 | 0.0200 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | task_type_L12 | handcrafted | 3 | -0.0143 | 0.0037 | -0.0103 | 0 | 3 | 0.0060 | 0.0080 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | task_type_L2 | handcrafted | 3 | -0.0126 | 0.0046 | -0.0091 | 0 | 2 | 0.0000 | 0.0060 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 50 | task_type_theme | handcrafted | 3 | 0.0126 | 0.0072 | 0.0091 | 3 | 1 | 0.0020 | 0.1160 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | combined | handcrafted | 3 | 0.0007 | 0.0027 | 0.0005 | 2 | 0 | 0.1460 | 0.2440 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | contrastive | handcrafted | 3 | -0.0437 | 0.0114 | -0.0315 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | contrastive_hc | handcrafted | 3 | -0.0411 | 0.0092 | -0.0297 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | frozen | handcrafted | 3 | 0.0008 | 0.0059 | 0.0006 | 2 | 0 | 0.1020 | 0.2300 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | handcrafted_nik | handcrafted | 3 | -0.0219 | 0.0084 | -0.0158 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | regression | handcrafted | 3 | -0.0404 | 0.0088 | -0.0292 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | regression_hc | handcrafted | 3 | -0.0348 | 0.0052 | -0.0251 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | stats | handcrafted | 3 | 0.0065 | 0.0027 | 0.0047 | 3 | 1 | 0.0360 | 0.1540 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | task_type_L1 | handcrafted | 3 | -0.0295 | 0.0100 | -0.0213 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | task_type_L12 | handcrafted | 3 | -0.0266 | 0.0064 | -0.0192 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | task_type_L2 | handcrafted | 3 | -0.0423 | 0.0077 | -0.0306 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 7 | gpt-5-chat | 500 | task_type_theme | handcrafted | 3 | -0.0121 | 0.0091 | -0.0088 | 0 | 1 | 0.0000 | 0.1740 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | combined | handcrafted | 3 | -0.0006 | 0.0022 | -0.0005 | 1 | 0 | 0.1460 | 0.2200 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | contrastive | handcrafted | 3 | -0.0108 | 0.0057 | -0.0078 | 0 | 1 | 0.0000 | 0.1060 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | contrastive_hc | handcrafted | 3 | -0.0097 | 0.0039 | -0.0070 | 0 | 2 | 0.0000 | 0.0180 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | frozen | handcrafted | 3 | -0.0044 | 0.0064 | -0.0032 | 1 | 1 | 0.0000 | 0.4480 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | handcrafted_nik | handcrafted | 3 | 0.0061 | 0.0020 | 0.0044 | 3 | 0 | 0.1400 | 0.1460 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | regression | handcrafted | 3 | 0.0002 | 0.0048 | 0.0002 | 2 | 0 | 0.1960 | 0.4420 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | regression_hc | handcrafted | 3 | 0.0013 | 0.0088 | 0.0010 | 2 | 0 | 0.0540 | 0.0780 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | stats | handcrafted | 3 | -0.0020 | 0.0022 | -0.0014 | 1 | 0 | 0.1680 | 0.4340 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | task_type_L1 | handcrafted | 3 | -0.0005 | 0.0052 | -0.0003 | 1 | 0 | 0.1980 | 0.2000 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | task_type_L12 | handcrafted | 3 | -0.0005 | 0.0042 | -0.0003 | 1 | 0 | 0.1720 | 0.2280 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | task_type_L2 | handcrafted | 3 | 0.0066 | 0.0035 | 0.0048 | 3 | 1 | 0.0400 | 0.3760 |
| llmrouterbench | unseen | 8 | gpt-5 | 5 | task_type_theme | handcrafted | 3 | 0.0027 | 0.0043 | 0.0020 | 2 | 0 | 0.1120 | 0.6200 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | combined | handcrafted | 3 | -0.0018 | 0.0002 | -0.0013 | 0 | 0 | 0.2940 | 0.4800 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | contrastive | handcrafted | 3 | -0.0177 | 0.0060 | -0.0128 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | contrastive_hc | handcrafted | 3 | -0.0172 | 0.0026 | -0.0124 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | frozen | handcrafted | 3 | -0.0066 | 0.0028 | -0.0047 | 0 | 1 | 0.0380 | 0.2680 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | handcrafted_nik | handcrafted | 3 | 0.0009 | 0.0044 | 0.0006 | 2 | 0 | 0.3320 | 0.4740 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | regression | handcrafted | 3 | -0.0070 | 0.0055 | -0.0051 | 1 | 1 | 0.0320 | 0.0880 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | regression_hc | handcrafted | 3 | -0.0056 | 0.0060 | -0.0040 | 1 | 1 | 0.0200 | 0.2060 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | stats | handcrafted | 3 | -0.0041 | 0.0012 | -0.0030 | 0 | 0 | 0.1940 | 0.3220 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | task_type_L1 | handcrafted | 3 | -0.0043 | 0.0060 | -0.0031 | 1 | 1 | 0.0220 | 0.3600 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | task_type_L12 | handcrafted | 3 | -0.0010 | 0.0059 | -0.0007 | 2 | 0 | 0.0520 | 0.3180 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | task_type_L2 | handcrafted | 3 | 0.0015 | 0.0030 | 0.0011 | 2 | 0 | 0.3820 | 0.6700 |
| llmrouterbench | unseen | 8 | gpt-5 | 50 | task_type_theme | handcrafted | 3 | -0.0066 | 0.0035 | -0.0048 | 0 | 1 | 0.0420 | 0.3300 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | combined | handcrafted | 3 | -0.0014 | 0.0005 | -0.0010 | 0 | 0 | 0.2680 | 0.5980 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | contrastive | handcrafted | 3 | -0.0174 | 0.0078 | -0.0126 | 0 | 2 | 0.0000 | 0.0200 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | contrastive_hc | handcrafted | 3 | -0.0175 | 0.0048 | -0.0126 | 0 | 3 | 0.0000 | 0.0100 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | frozen | handcrafted | 3 | -0.0073 | 0.0040 | -0.0053 | 0 | 1 | 0.0040 | 0.1360 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | handcrafted_nik | handcrafted | 3 | 0.0021 | 0.0020 | 0.0015 | 3 | 0 | 0.3620 | 0.7440 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | regression | handcrafted | 3 | -0.0053 | 0.0038 | -0.0038 | 0 | 0 | 0.1060 | 0.3080 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | regression_hc | handcrafted | 3 | -0.0034 | 0.0058 | -0.0025 | 1 | 1 | 0.0240 | 0.7220 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | stats | handcrafted | 3 | -0.0068 | 0.0020 | -0.0049 | 0 | 1 | 0.0260 | 0.1340 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | task_type_L1 | handcrafted | 3 | -0.0018 | 0.0022 | -0.0013 | 1 | 0 | 0.2900 | 0.8560 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | task_type_L12 | handcrafted | 3 | 0.0025 | 0.0033 | 0.0018 | 2 | 0 | 0.1680 | 0.4720 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | task_type_L2 | handcrafted | 3 | 0.0025 | 0.0019 | 0.0018 | 2 | 0 | 0.5740 | 0.5980 |
| llmrouterbench | unseen | 8 | gpt-5 | 500 | task_type_theme | handcrafted | 3 | -0.0050 | 0.0014 | -0.0036 | 0 | 0 | 0.2060 | 0.3260 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | combined | handcrafted | 3 | -0.0009 | 0.0019 | -0.0006 | 2 | 1 | 0.0420 | 0.5480 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | contrastive | handcrafted | 3 | -0.0537 | 0.0446 | -0.0379 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | contrastive_hc | handcrafted | 3 | -0.0681 | 0.0463 | -0.0481 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | frozen | handcrafted | 3 | -0.0036 | 0.0032 | -0.0025 | 0 | 1 | 0.0200 | 0.5520 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | handcrafted_nik | handcrafted | 3 | -0.0156 | 0.0189 | -0.0110 | 0 | 1 | 0.0000 | 0.3720 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | regression | handcrafted | 3 | -0.0255 | 0.0292 | -0.0180 | 1 | 2 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | regression_hc | handcrafted | 3 | -0.0242 | 0.0300 | -0.0172 | 1 | 1 | 0.0000 | 0.0620 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | stats | handcrafted | 3 | -0.0008 | 0.0006 | -0.0006 | 0 | 0 | 0.4660 | 0.7580 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | task_type_L1 | handcrafted | 3 | -0.0142 | 0.0060 | -0.0100 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | task_type_L12 | handcrafted | 3 | -0.0129 | 0.0073 | -0.0091 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | task_type_L2 | handcrafted | 3 | -0.0243 | 0.0218 | -0.0172 | 0 | 3 | 0.0000 | 0.0040 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 5 | task_type_theme | handcrafted | 3 | -0.0160 | 0.0174 | -0.0113 | 0 | 1 | 0.0000 | 0.1040 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | combined | handcrafted | 3 | 0.0034 | 0.0022 | 0.0024 | 3 | 0 | 0.0600 | 0.1360 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | contrastive | handcrafted | 3 | -0.1243 | 0.0078 | -0.0874 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | contrastive_hc | handcrafted | 3 | -0.1455 | 0.0141 | -0.1023 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | frozen | handcrafted | 3 | 0.0124 | 0.0087 | 0.0088 | 3 | 2 | 0.0000 | 0.0140 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | handcrafted_nik | handcrafted | 3 | -0.0271 | 0.0053 | -0.0191 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | regression | handcrafted | 3 | -0.0575 | 0.0053 | -0.0405 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | regression_hc | handcrafted | 3 | -0.0493 | 0.0062 | -0.0346 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | stats | handcrafted | 3 | 0.0091 | 0.0063 | 0.0064 | 3 | 2 | 0.0060 | 0.0060 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | task_type_L1 | handcrafted | 3 | -0.0215 | 0.0142 | -0.0151 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | task_type_L12 | handcrafted | 3 | -0.0315 | 0.0038 | -0.0221 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | task_type_L2 | handcrafted | 3 | -0.0589 | 0.0135 | -0.0414 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 50 | task_type_theme | handcrafted | 3 | -0.0111 | 0.0141 | -0.0078 | 1 | 2 | 0.0000 | 0.0060 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | combined | handcrafted | 3 | 0.0036 | 0.0040 | 0.0025 | 2 | 2 | 0.0200 | 0.0320 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | contrastive | handcrafted | 3 | -0.1304 | 0.0032 | -0.0918 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | contrastive_hc | handcrafted | 3 | -0.1501 | 0.0036 | -0.1056 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | frozen | handcrafted | 3 | 0.0048 | 0.0077 | 0.0034 | 2 | 1 | 0.0080 | 0.1000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | handcrafted_nik | handcrafted | 3 | -0.0264 | 0.0101 | -0.0186 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | regression | handcrafted | 3 | -0.0641 | 0.0108 | -0.0451 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | regression_hc | handcrafted | 3 | -0.0566 | 0.0117 | -0.0399 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | stats | handcrafted | 3 | 0.0088 | 0.0043 | 0.0062 | 3 | 2 | 0.0000 | 0.0120 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | task_type_L1 | handcrafted | 3 | -0.0314 | 0.0045 | -0.0221 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | task_type_L12 | handcrafted | 3 | -0.0288 | 0.0026 | -0.0203 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | task_type_L2 | handcrafted | 3 | -0.0653 | 0.0056 | -0.0460 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 9 | kimi-k2-0905 | 500 | task_type_theme | handcrafted | 3 | -0.0237 | 0.0098 | -0.0167 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | combined | handcrafted | 3 | -0.0016 | 0.0014 | -0.0011 | 1 | 0 | 0.1280 | 0.1760 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | contrastive | handcrafted | 3 | -0.1832 | 0.0130 | -0.1279 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | contrastive_hc | handcrafted | 3 | -0.1855 | 0.0040 | -0.1296 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | frozen | handcrafted | 3 | -0.0039 | 0.0033 | -0.0027 | 0 | 1 | 0.0140 | 0.4620 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | handcrafted_nik | handcrafted | 3 | -0.0263 | 0.0051 | -0.0184 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | regression | handcrafted | 3 | -0.0648 | 0.0120 | -0.0453 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | regression_hc | handcrafted | 3 | -0.0546 | 0.0054 | -0.0381 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | stats | handcrafted | 3 | -0.0011 | 0.0017 | -0.0008 | 1 | 0 | 0.2660 | 0.6800 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | task_type_L1 | handcrafted | 3 | -0.0195 | 0.0040 | -0.0136 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | task_type_L12 | handcrafted | 3 | -0.0182 | 0.0018 | -0.0127 | 0 | 3 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | task_type_L2 | handcrafted | 3 | -0.0718 | 0.0058 | -0.0502 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 5 | task_type_theme | handcrafted | 3 | -0.0246 | 0.0050 | -0.0172 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | combined | handcrafted | 3 | 0.0018 | 0.0040 | 0.0012 | 1 | 1 | 0.0100 | 0.6820 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | contrastive | handcrafted | 3 | -0.1881 | 0.0134 | -0.1313 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | contrastive_hc | handcrafted | 3 | -0.1851 | 0.0027 | -0.1293 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | frozen | handcrafted | 3 | 0.0064 | 0.0065 | 0.0045 | 2 | 2 | 0.0260 | 0.0340 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | handcrafted_nik | handcrafted | 3 | -0.0158 | 0.0041 | -0.0110 | 0 | 2 | 0.0000 | 0.0180 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | regression | handcrafted | 3 | -0.0666 | 0.0099 | -0.0465 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | regression_hc | handcrafted | 3 | -0.0533 | 0.0012 | -0.0372 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | stats | handcrafted | 3 | 0.0084 | 0.0086 | 0.0059 | 2 | 2 | 0.0000 | 0.0100 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | task_type_L1 | handcrafted | 3 | -0.0167 | 0.0012 | -0.0117 | 0 | 3 | 0.0020 | 0.0080 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | task_type_L12 | handcrafted | 3 | -0.0187 | 0.0068 | -0.0131 | 0 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | task_type_L2 | handcrafted | 3 | -0.0965 | 0.0196 | -0.0675 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 50 | task_type_theme | handcrafted | 3 | -0.0113 | 0.0066 | -0.0079 | 0 | 1 | 0.0000 | 0.1380 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | combined | handcrafted | 3 | 0.0011 | 0.0014 | 0.0007 | 2 | 0 | 0.2720 | 0.6000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | contrastive | handcrafted | 3 | -0.1911 | 0.0106 | -0.1334 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | contrastive_hc | handcrafted | 3 | -0.1920 | 0.0002 | -0.1341 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | frozen | handcrafted | 3 | 0.0022 | 0.0046 | 0.0015 | 2 | 0 | 0.1340 | 0.3420 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | handcrafted_nik | handcrafted | 3 | -0.0212 | 0.0060 | -0.0148 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | regression | handcrafted | 3 | -0.0719 | 0.0073 | -0.0502 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | regression_hc | handcrafted | 3 | -0.0590 | 0.0037 | -0.0412 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | stats | handcrafted | 3 | 0.0044 | 0.0001 | 0.0031 | 3 | 0 | 0.1800 | 0.2380 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | task_type_L1 | handcrafted | 3 | -0.0195 | 0.0036 | -0.0136 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | task_type_L12 | handcrafted | 3 | -0.0232 | 0.0045 | -0.0162 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | task_type_L2 | handcrafted | 3 | -0.0883 | 0.0067 | -0.0617 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 10 | deepseek-v3.1-terminus | 500 | task_type_theme | handcrafted | 3 | -0.0183 | 0.0057 | -0.0128 | 0 | 2 | 0.0000 | 0.0020 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | combined | handcrafted | 3 | -0.0014 | 0.0018 | -0.0010 | 0 | 0 | 0.0880 | 0.9740 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | contrastive | handcrafted | 3 | -0.0744 | 0.0035 | -0.0517 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | contrastive_hc | handcrafted | 3 | -0.0709 | 0.0020 | -0.0493 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | frozen | handcrafted | 3 | -0.0067 | 0.0031 | -0.0046 | 0 | 1 | 0.0140 | 0.2240 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | handcrafted_nik | handcrafted | 3 | -0.0193 | 0.0070 | -0.0134 | 0 | 3 | 0.0000 | 0.0140 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | regression | handcrafted | 3 | -0.0480 | 0.0101 | -0.0334 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | regression_hc | handcrafted | 3 | -0.0454 | 0.0094 | -0.0316 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | stats | handcrafted | 3 | -0.0032 | 0.0006 | -0.0022 | 0 | 0 | 0.2560 | 0.4200 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | task_type_L1 | handcrafted | 3 | -0.0184 | 0.0005 | -0.0128 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | task_type_L12 | handcrafted | 3 | -0.0152 | 0.0026 | -0.0106 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | task_type_L2 | handcrafted | 3 | -0.0447 | 0.0068 | -0.0311 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 5 | task_type_theme | handcrafted | 3 | -0.0177 | 0.0079 | -0.0124 | 0 | 2 | 0.0000 | 0.0220 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | combined | handcrafted | 3 | 0.0025 | 0.0036 | 0.0018 | 2 | 1 | 0.0260 | 0.9720 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | contrastive | handcrafted | 3 | -0.0560 | 0.0156 | -0.0389 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | contrastive_hc | handcrafted | 3 | -0.0519 | 0.0124 | -0.0361 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | frozen | handcrafted | 3 | 0.0041 | 0.0062 | 0.0029 | 2 | 0 | 0.1460 | 0.2400 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | handcrafted_nik | handcrafted | 3 | -0.0125 | 0.0071 | -0.0087 | 0 | 2 | 0.0000 | 0.0140 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | regression | handcrafted | 3 | -0.0411 | 0.0051 | -0.0286 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | regression_hc | handcrafted | 3 | -0.0403 | 0.0092 | -0.0280 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | stats | handcrafted | 3 | 0.0068 | 0.0073 | 0.0047 | 2 | 1 | 0.0000 | 0.2080 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | task_type_L1 | handcrafted | 3 | -0.0162 | 0.0062 | -0.0113 | 0 | 2 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | task_type_L12 | handcrafted | 3 | -0.0226 | 0.0088 | -0.0157 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | task_type_L2 | handcrafted | 3 | -0.0450 | 0.0105 | -0.0313 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 50 | task_type_theme | handcrafted | 3 | 0.0011 | 0.0149 | 0.0008 | 1 | 2 | 0.0040 | 0.0220 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | combined | handcrafted | 3 | -0.0010 | 0.0021 | -0.0007 | 2 | 0 | 0.0900 | 0.7680 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | contrastive | handcrafted | 3 | -0.0736 | 0.0027 | -0.0512 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | contrastive_hc | handcrafted | 3 | -0.0697 | 0.0032 | -0.0485 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | frozen | handcrafted | 3 | -0.0055 | 0.0042 | -0.0039 | 0 | 1 | 0.0140 | 0.2180 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | handcrafted_nik | handcrafted | 3 | -0.0187 | 0.0076 | -0.0131 | 0 | 3 | 0.0000 | 0.0380 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | regression | handcrafted | 3 | -0.0572 | 0.0044 | -0.0398 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | regression_hc | handcrafted | 3 | -0.0540 | 0.0059 | -0.0376 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | stats | handcrafted | 3 | -0.0021 | 0.0016 | -0.0015 | 0 | 0 | 0.2740 | 0.5120 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | task_type_L1 | handcrafted | 3 | -0.0290 | 0.0028 | -0.0201 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | task_type_L12 | handcrafted | 3 | -0.0245 | 0.0032 | -0.0171 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | task_type_L2 | handcrafted | 3 | -0.0615 | 0.0012 | -0.0428 | 0 | 3 | 0.0000 | 0.0000 |
| llmrouterbench | unseen | 11 | glm-4.6 | 500 | task_type_theme | handcrafted | 3 | -0.0166 | 0.0085 | -0.0116 | 0 | 1 | 0.0000 | 0.0760 |
| routerbench | unseen | 0 | claude-v2 | 5 | combined | handcrafted | 3 | -0.0014 | 0.0015 | -0.0012 | 1 | 1 | 0.0020 | 0.0560 |
| routerbench | unseen | 0 | claude-v2 | 5 | contrastive | handcrafted | 3 | -0.0023 | 0.0033 | -0.0019 | 1 | 1 | 0.0020 | 0.8960 |
| routerbench | unseen | 0 | claude-v2 | 5 | contrastive_hc | handcrafted | 3 | -0.0020 | 0.0035 | -0.0017 | 1 | 1 | 0.0020 | 0.5680 |
| routerbench | unseen | 0 | claude-v2 | 5 | frozen | handcrafted | 3 | -0.0012 | 0.0012 | -0.0010 | 1 | 0 | 0.1940 | 0.2640 |
| routerbench | unseen | 0 | claude-v2 | 5 | handcrafted_nik | handcrafted | 3 | -0.0016 | 0.0022 | -0.0013 | 1 | 1 | 0.0040 | 0.5780 |
| routerbench | unseen | 0 | claude-v2 | 5 | regression | handcrafted | 3 | -0.0019 | 0.0048 | -0.0016 | 2 | 1 | 0.0000 | 0.3880 |
| routerbench | unseen | 0 | claude-v2 | 5 | regression_hc | handcrafted | 3 | -0.0024 | 0.0039 | -0.0020 | 2 | 1 | 0.0000 | 0.8440 |
| routerbench | unseen | 0 | claude-v2 | 5 | stats | handcrafted | 3 | 0.0005 | 0.0010 | 0.0005 | 2 | 0 | 0.2180 | 0.7500 |
| routerbench | unseen | 0 | claude-v2 | 5 | task_type_L1 | handcrafted | 3 | -0.0044 | 0.0009 | -0.0037 | 0 | 1 | 0.0000 | 0.0960 |
| routerbench | unseen | 0 | claude-v2 | 5 | task_type_L12 | handcrafted | 3 | -0.0050 | 0.0024 | -0.0042 | 0 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 0 | claude-v2 | 5 | task_type_L2 | handcrafted | 3 | -0.0051 | 0.0039 | -0.0043 | 0 | 2 | 0.0000 | 0.0040 |
| routerbench | unseen | 0 | claude-v2 | 5 | task_type_theme | handcrafted | 3 | -0.0044 | 0.0018 | -0.0037 | 0 | 1 | 0.0020 | 0.0580 |
| routerbench | unseen | 0 | claude-v2 | 50 | combined | handcrafted | 3 | -0.0010 | 0.0008 | -0.0009 | 1 | 0 | 0.1980 | 0.2040 |
| routerbench | unseen | 0 | claude-v2 | 50 | contrastive | handcrafted | 3 | -0.0044 | 0.0007 | -0.0037 | 0 | 1 | 0.0220 | 0.1240 |
| routerbench | unseen | 0 | claude-v2 | 50 | contrastive_hc | handcrafted | 3 | -0.0048 | 0.0012 | -0.0040 | 0 | 1 | 0.0040 | 0.0640 |
| routerbench | unseen | 0 | claude-v2 | 50 | frozen | handcrafted | 3 | -0.0012 | 0.0019 | -0.0010 | 1 | 0 | 0.0820 | 0.5720 |
| routerbench | unseen | 0 | claude-v2 | 50 | handcrafted_nik | handcrafted | 3 | -0.0008 | 0.0032 | -0.0007 | 2 | 1 | 0.0040 | 0.2860 |
| routerbench | unseen | 0 | claude-v2 | 50 | regression | handcrafted | 3 | -0.0027 | 0.0016 | -0.0023 | 0 | 0 | 0.1460 | 0.1940 |
| routerbench | unseen | 0 | claude-v2 | 50 | regression_hc | handcrafted | 3 | -0.0032 | 0.0022 | -0.0027 | 0 | 1 | 0.0260 | 0.1120 |
| routerbench | unseen | 0 | claude-v2 | 50 | stats | handcrafted | 3 | 0.0013 | 0.0017 | 0.0010 | 2 | 0 | 0.1440 | 0.2740 |
| routerbench | unseen | 0 | claude-v2 | 50 | task_type_L1 | handcrafted | 3 | -0.0027 | 0.0033 | -0.0023 | 1 | 1 | 0.0000 | 0.3160 |
| routerbench | unseen | 0 | claude-v2 | 50 | task_type_L12 | handcrafted | 3 | -0.0045 | 0.0030 | -0.0038 | 0 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 0 | claude-v2 | 50 | task_type_L2 | handcrafted | 3 | -0.0034 | 0.0026 | -0.0029 | 0 | 1 | 0.0200 | 0.1040 |
| routerbench | unseen | 0 | claude-v2 | 50 | task_type_theme | handcrafted | 3 | -0.0054 | 0.0016 | -0.0045 | 0 | 1 | 0.0000 | 0.0940 |
| routerbench | unseen | 0 | claude-v2 | 500 | combined | handcrafted | 3 | -0.0012 | 0.0005 | -0.0010 | 0 | 0 | 0.1760 | 0.2540 |
| routerbench | unseen | 0 | claude-v2 | 500 | contrastive | handcrafted | 3 | -0.0034 | 0.0011 | -0.0028 | 0 | 0 | 0.1260 | 0.1660 |
| routerbench | unseen | 0 | claude-v2 | 500 | contrastive_hc | handcrafted | 3 | -0.0038 | 0.0006 | -0.0032 | 0 | 0 | 0.0560 | 0.1520 |
| routerbench | unseen | 0 | claude-v2 | 500 | frozen | handcrafted | 3 | -0.0016 | 0.0017 | -0.0014 | 1 | 0 | 0.0760 | 0.4940 |
| routerbench | unseen | 0 | claude-v2 | 500 | handcrafted_nik | handcrafted | 3 | 0.0016 | 0.0007 | 0.0014 | 3 | 0 | 0.1740 | 0.4500 |
| routerbench | unseen | 0 | claude-v2 | 500 | regression | handcrafted | 3 | -0.0020 | 0.0016 | -0.0017 | 0 | 0 | 0.1080 | 0.5320 |
| routerbench | unseen | 0 | claude-v2 | 500 | regression_hc | handcrafted | 3 | -0.0021 | 0.0018 | -0.0018 | 0 | 0 | 0.0640 | 0.3880 |
| routerbench | unseen | 0 | claude-v2 | 500 | stats | handcrafted | 3 | 0.0025 | 0.0007 | 0.0021 | 3 | 0 | 0.0620 | 0.2500 |
| routerbench | unseen | 0 | claude-v2 | 500 | task_type_L1 | handcrafted | 3 | -0.0015 | 0.0022 | -0.0013 | 1 | 0 | 0.2040 | 0.3460 |
| routerbench | unseen | 0 | claude-v2 | 500 | task_type_L12 | handcrafted | 3 | -0.0046 | 0.0028 | -0.0038 | 0 | 2 | 0.0000 | 0.0060 |
| routerbench | unseen | 0 | claude-v2 | 500 | task_type_L2 | handcrafted | 3 | -0.0015 | 0.0041 | -0.0013 | 1 | 1 | 0.0440 | 0.0920 |
| routerbench | unseen | 0 | claude-v2 | 500 | task_type_theme | handcrafted | 3 | -0.0055 | 0.0051 | -0.0046 | 0 | 1 | 0.0000 | 0.1160 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | combined | handcrafted | 3 | -0.0011 | 0.0047 | -0.0009 | 1 | 1 | 0.0080 | 0.1000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | contrastive | handcrafted | 3 | 0.1143 | 0.0480 | 0.0952 | 3 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | contrastive_hc | handcrafted | 3 | 0.0971 | 0.0444 | 0.0808 | 3 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | frozen | handcrafted | 3 | -0.0326 | 0.0457 | -0.0271 | 1 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | handcrafted_nik | handcrafted | 3 | -0.0108 | 0.0348 | -0.0089 | 1 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | regression | handcrafted | 3 | 0.0346 | 0.0270 | 0.0288 | 3 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | regression_hc | handcrafted | 3 | 0.0289 | 0.0307 | 0.0240 | 2 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | stats | handcrafted | 3 | 0.0137 | 0.0191 | 0.0114 | 2 | 3 | 0.0000 | 0.0160 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | task_type_L1 | handcrafted | 3 | 0.0794 | 0.0031 | 0.0661 | 3 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | task_type_L12 | handcrafted | 3 | 0.0284 | 0.0151 | 0.0236 | 3 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | task_type_L2 | handcrafted | 3 | 0.0670 | 0.0441 | 0.0557 | 3 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 5 | task_type_theme | handcrafted | 3 | -0.1692 | 0.0754 | -0.1409 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | combined | handcrafted | 3 | 0.0008 | 0.0003 | 0.0007 | 3 | 0 | 0.1600 | 0.3280 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | contrastive | handcrafted | 3 | -0.0091 | 0.0055 | -0.0075 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | contrastive_hc | handcrafted | 3 | -0.0174 | 0.0065 | -0.0145 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | frozen | handcrafted | 3 | -0.0008 | 0.0003 | -0.0007 | 0 | 0 | 0.4100 | 0.6660 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | handcrafted_nik | handcrafted | 3 | -0.0026 | 0.0017 | -0.0022 | 0 | 1 | 0.0000 | 0.1900 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | regression | handcrafted | 3 | -0.0334 | 0.0177 | -0.0278 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | regression_hc | handcrafted | 3 | -0.0353 | 0.0185 | -0.0294 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | stats | handcrafted | 3 | 0.0005 | 0.0006 | 0.0004 | 2 | 0 | 0.3180 | 0.8580 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | task_type_L1 | handcrafted | 3 | -0.0021 | 0.0009 | -0.0017 | 0 | 1 | 0.0300 | 0.2640 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | task_type_L12 | handcrafted | 3 | 0.0000 | 0.0013 | 0.0000 | 2 | 0 | 0.0800 | 0.1520 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | task_type_L2 | handcrafted | 3 | 0.0005 | 0.0016 | 0.0004 | 2 | 0 | 0.1340 | 0.1400 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 50 | task_type_theme | handcrafted | 3 | -0.0119 | 0.0018 | -0.0099 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | combined | handcrafted | 3 | 0.0008 | 0.0003 | 0.0007 | 3 | 0 | 0.1740 | 0.3260 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | contrastive | handcrafted | 3 | -0.0077 | 0.0020 | -0.0064 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | contrastive_hc | handcrafted | 3 | -0.0136 | 0.0021 | -0.0113 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | frozen | handcrafted | 3 | -0.0011 | 0.0006 | -0.0009 | 0 | 0 | 0.2520 | 0.5400 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | handcrafted_nik | handcrafted | 3 | -0.0014 | 0.0016 | -0.0011 | 1 | 1 | 0.0200 | 0.2260 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | regression | handcrafted | 3 | -0.0274 | 0.0080 | -0.0228 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | regression_hc | handcrafted | 3 | -0.0315 | 0.0069 | -0.0263 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | stats | handcrafted | 3 | 0.0006 | 0.0006 | 0.0005 | 3 | 0 | 0.2580 | 0.8340 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | task_type_L1 | handcrafted | 3 | -0.0003 | 0.0007 | -0.0003 | 1 | 0 | 0.2840 | 0.7800 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | task_type_L12 | handcrafted | 3 | -0.0003 | 0.0015 | -0.0003 | 2 | 1 | 0.0200 | 0.1740 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | task_type_L2 | handcrafted | 3 | 0.0002 | 0.0018 | 0.0002 | 2 | 1 | 0.0360 | 0.1200 |
| routerbench | unseen | 1 | meta/llama-2-70b-chat | 500 | task_type_theme | handcrafted | 3 | -0.0096 | 0.0014 | -0.0080 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | combined | handcrafted | 3 | -0.0000 | 0.0004 | -0.0000 | 2 | 0 | 0.4340 | 0.6360 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | contrastive | handcrafted | 3 | 0.0299 | 0.0457 | 0.0237 | 1 | 1 | 0.0000 | 0.1040 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | contrastive_hc | handcrafted | 3 | 0.0233 | 0.0364 | 0.0184 | 2 | 2 | 0.0000 | 0.0060 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | frozen | handcrafted | 3 | -0.0122 | 0.0144 | -0.0097 | 0 | 1 | 0.0000 | 0.1320 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | handcrafted_nik | handcrafted | 3 | -0.0051 | 0.0012 | -0.0041 | 0 | 3 | 0.0000 | 0.0120 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | regression | handcrafted | 3 | 0.0033 | 0.0213 | 0.0026 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | regression_hc | handcrafted | 3 | 0.0030 | 0.0185 | 0.0023 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | stats | handcrafted | 3 | -0.0026 | 0.0025 | -0.0021 | 1 | 1 | 0.0000 | 0.0700 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | task_type_L1 | handcrafted | 3 | 0.0082 | 0.0138 | 0.0065 | 2 | 2 | 0.0000 | 0.0140 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | task_type_L12 | handcrafted | 3 | 0.0034 | 0.0068 | 0.0027 | 1 | 1 | 0.0000 | 0.1740 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | task_type_L2 | handcrafted | 3 | 0.0115 | 0.0200 | 0.0091 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 5 | task_type_theme | handcrafted | 3 | -0.0100 | 0.0118 | -0.0079 | 0 | 1 | 0.0000 | 0.1120 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | combined | handcrafted | 3 | -0.0004 | 0.0001 | -0.0003 | 0 | 0 | 0.4980 | 0.5420 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | contrastive | handcrafted | 3 | -0.0026 | 0.0011 | -0.0021 | 0 | 0 | 0.1040 | 0.2560 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | contrastive_hc | handcrafted | 3 | -0.0048 | 0.0013 | -0.0038 | 0 | 1 | 0.0060 | 0.0740 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | frozen | handcrafted | 3 | -0.0013 | 0.0004 | -0.0010 | 0 | 0 | 0.2660 | 0.4060 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | handcrafted_nik | handcrafted | 3 | -0.0040 | 0.0014 | -0.0032 | 0 | 2 | 0.0000 | 0.0120 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | regression | handcrafted | 3 | -0.0155 | 0.0045 | -0.0123 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | regression_hc | handcrafted | 3 | -0.0153 | 0.0032 | -0.0121 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | stats | handcrafted | 3 | -0.0023 | 0.0004 | -0.0019 | 0 | 1 | 0.0320 | 0.1240 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | task_type_L1 | handcrafted | 3 | -0.0024 | 0.0008 | -0.0019 | 0 | 0 | 0.0640 | 0.1700 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | task_type_L12 | handcrafted | 3 | -0.0013 | 0.0007 | -0.0010 | 0 | 1 | 0.0380 | 0.3900 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | task_type_L2 | handcrafted | 3 | -0.0021 | 0.0004 | -0.0016 | 0 | 1 | 0.0480 | 0.1800 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 50 | task_type_theme | handcrafted | 3 | -0.0016 | 0.0009 | -0.0013 | 0 | 0 | 0.2420 | 0.2980 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | combined | handcrafted | 3 | -0.0005 | 0.0001 | -0.0004 | 0 | 0 | 0.3660 | 0.5480 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | contrastive | handcrafted | 3 | -0.0034 | 0.0012 | -0.0027 | 0 | 1 | 0.0380 | 0.1020 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | contrastive_hc | handcrafted | 3 | -0.0058 | 0.0008 | -0.0046 | 0 | 3 | 0.0060 | 0.0200 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | frozen | handcrafted | 3 | -0.0017 | 0.0006 | -0.0014 | 0 | 0 | 0.1520 | 0.1720 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | handcrafted_nik | handcrafted | 3 | -0.0054 | 0.0005 | -0.0042 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | regression | handcrafted | 3 | -0.0186 | 0.0018 | -0.0147 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | regression_hc | handcrafted | 3 | -0.0166 | 0.0014 | -0.0132 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | stats | handcrafted | 3 | -0.0036 | 0.0015 | -0.0029 | 0 | 2 | 0.0000 | 0.0480 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | task_type_L1 | handcrafted | 3 | -0.0029 | 0.0021 | -0.0023 | 0 | 1 | 0.0000 | 0.2300 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | task_type_L12 | handcrafted | 3 | -0.0020 | 0.0007 | -0.0016 | 0 | 1 | 0.0160 | 0.0660 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | task_type_L2 | handcrafted | 3 | -0.0031 | 0.0015 | -0.0025 | 0 | 1 | 0.0000 | 0.0580 |
| routerbench | unseen | 2 | WizardLM/WizardLM-13B-V1.2 | 500 | task_type_theme | handcrafted | 3 | -0.0030 | 0.0018 | -0.0024 | 0 | 1 | 0.0040 | 0.2760 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | combined | handcrafted | 3 | -0.0048 | 0.0037 | -0.0036 | 1 | 2 | 0.0000 | 0.0200 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | contrastive | handcrafted | 3 | -0.0346 | 0.0327 | -0.0257 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | contrastive_hc | handcrafted | 3 | -0.0261 | 0.0256 | -0.0194 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | frozen | handcrafted | 3 | 0.0027 | 0.0116 | 0.0020 | 1 | 2 | 0.0000 | 0.0240 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | handcrafted_nik | handcrafted | 3 | 0.0062 | 0.0171 | 0.0046 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | regression | handcrafted | 3 | -0.0305 | 0.0263 | -0.0226 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | regression_hc | handcrafted | 3 | -0.0300 | 0.0255 | -0.0223 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | stats | handcrafted | 3 | 0.0068 | 0.0199 | 0.0050 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | task_type_L1 | handcrafted | 3 | 0.0240 | 0.0493 | 0.0177 | 1 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | task_type_L12 | handcrafted | 3 | 0.0066 | 0.0187 | 0.0049 | 1 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | task_type_L2 | handcrafted | 3 | 0.0108 | 0.0237 | 0.0079 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 5 | task_type_theme | handcrafted | 3 | 0.0124 | 0.0301 | 0.0091 | 1 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | combined | handcrafted | 3 | -0.0019 | 0.0019 | -0.0014 | 1 | 1 | 0.0200 | 0.4360 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | contrastive | handcrafted | 3 | -0.0091 | 0.0030 | -0.0067 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | contrastive_hc | handcrafted | 3 | -0.0069 | 0.0010 | -0.0051 | 0 | 3 | 0.0060 | 0.0080 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | frozen | handcrafted | 3 | -0.0055 | 0.0013 | -0.0041 | 0 | 1 | 0.0100 | 0.0600 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | handcrafted_nik | handcrafted | 3 | -0.0014 | 0.0006 | -0.0010 | 0 | 0 | 0.3240 | 0.3940 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | regression | handcrafted | 3 | -0.0063 | 0.0019 | -0.0047 | 0 | 2 | 0.0020 | 0.0280 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | regression_hc | handcrafted | 3 | -0.0072 | 0.0022 | -0.0054 | 0 | 3 | 0.0000 | 0.0100 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | stats | handcrafted | 3 | -0.0018 | 0.0005 | -0.0013 | 0 | 0 | 0.1380 | 0.1740 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | task_type_L1 | handcrafted | 3 | -0.0151 | 0.0017 | -0.0112 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | task_type_L12 | handcrafted | 3 | -0.0117 | 0.0011 | -0.0086 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | task_type_L2 | handcrafted | 3 | -0.0107 | 0.0003 | -0.0079 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 50 | task_type_theme | handcrafted | 3 | -0.0120 | 0.0010 | -0.0089 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | combined | handcrafted | 3 | -0.0019 | 0.0019 | -0.0014 | 1 | 1 | 0.0200 | 0.4360 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | contrastive | handcrafted | 3 | -0.0091 | 0.0029 | -0.0068 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | contrastive_hc | handcrafted | 3 | -0.0071 | 0.0002 | -0.0053 | 0 | 3 | 0.0040 | 0.0080 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | frozen | handcrafted | 3 | -0.0055 | 0.0013 | -0.0041 | 0 | 1 | 0.0100 | 0.0600 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | handcrafted_nik | handcrafted | 3 | -0.0014 | 0.0006 | -0.0010 | 0 | 0 | 0.3260 | 0.3940 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | regression | handcrafted | 3 | -0.0064 | 0.0014 | -0.0047 | 0 | 2 | 0.0000 | 0.0100 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | regression_hc | handcrafted | 3 | -0.0073 | 0.0001 | -0.0054 | 0 | 3 | 0.0020 | 0.0060 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | stats | handcrafted | 3 | -0.0018 | 0.0005 | -0.0013 | 0 | 0 | 0.1380 | 0.1740 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | task_type_L1 | handcrafted | 3 | -0.0151 | 0.0017 | -0.0112 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | task_type_L12 | handcrafted | 3 | -0.0117 | 0.0011 | -0.0086 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | task_type_L2 | handcrafted | 3 | -0.0107 | 0.0003 | -0.0079 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 3 | meta/code-llama-instruct-34b-chat | 500 | task_type_theme | handcrafted | 3 | -0.0120 | 0.0010 | -0.0089 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | combined | handcrafted | 3 | -0.0034 | 0.0029 | -0.0024 | 1 | 2 | 0.0020 | 0.0220 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | contrastive | handcrafted | 3 | -0.0312 | 0.0193 | -0.0217 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | contrastive_hc | handcrafted | 3 | -0.0293 | 0.0172 | -0.0204 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | frozen | handcrafted | 3 | -0.0083 | 0.0048 | -0.0058 | 0 | 2 | 0.0000 | 0.0400 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | handcrafted_nik | handcrafted | 3 | -0.0061 | 0.0063 | -0.0042 | 0 | 1 | 0.0000 | 0.3440 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | regression | handcrafted | 3 | -0.0215 | 0.0120 | -0.0150 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | regression_hc | handcrafted | 3 | -0.0164 | 0.0101 | -0.0114 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | stats | handcrafted | 3 | -0.0030 | 0.0058 | -0.0020 | 1 | 1 | 0.0000 | 0.3440 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | task_type_L1 | handcrafted | 3 | -0.0031 | 0.0095 | -0.0022 | 1 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | task_type_L12 | handcrafted | 3 | -0.0076 | 0.0015 | -0.0053 | 0 | 3 | 0.0000 | 0.0100 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | task_type_L2 | handcrafted | 3 | -0.0040 | 0.0047 | -0.0028 | 0 | 1 | 0.0000 | 0.7600 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 5 | task_type_theme | handcrafted | 3 | -0.0200 | 0.0082 | -0.0139 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | combined | handcrafted | 3 | -0.0016 | 0.0019 | -0.0011 | 1 | 1 | 0.0240 | 0.4080 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | contrastive | handcrafted | 3 | -0.0184 | 0.0060 | -0.0128 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | contrastive_hc | handcrafted | 3 | -0.0220 | 0.0061 | -0.0154 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | frozen | handcrafted | 3 | -0.0068 | 0.0018 | -0.0047 | 0 | 2 | 0.0000 | 0.0040 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | handcrafted_nik | handcrafted | 3 | -0.0029 | 0.0006 | -0.0020 | 0 | 1 | 0.0500 | 0.1000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | regression | handcrafted | 3 | -0.0139 | 0.0021 | -0.0097 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | regression_hc | handcrafted | 3 | -0.0111 | 0.0018 | -0.0077 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | stats | handcrafted | 3 | -0.0018 | 0.0010 | -0.0012 | 0 | 0 | 0.0520 | 0.1680 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | task_type_L1 | handcrafted | 3 | -0.0141 | 0.0024 | -0.0099 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | task_type_L12 | handcrafted | 3 | -0.0123 | 0.0015 | -0.0086 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | task_type_L2 | handcrafted | 3 | -0.0113 | 0.0004 | -0.0079 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 50 | task_type_theme | handcrafted | 3 | -0.0169 | 0.0010 | -0.0118 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | combined | handcrafted | 3 | -0.0018 | 0.0018 | -0.0013 | 1 | 1 | 0.0240 | 0.3160 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | contrastive | handcrafted | 3 | -0.0213 | 0.0042 | -0.0149 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | contrastive_hc | handcrafted | 3 | -0.0269 | 0.0025 | -0.0188 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | frozen | handcrafted | 3 | -0.0077 | 0.0011 | -0.0054 | 0 | 3 | 0.0000 | 0.0040 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | handcrafted_nik | handcrafted | 3 | -0.0038 | 0.0006 | -0.0027 | 0 | 2 | 0.0300 | 0.0460 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | regression | handcrafted | 3 | -0.0165 | 0.0017 | -0.0115 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | regression_hc | handcrafted | 3 | -0.0143 | 0.0030 | -0.0100 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | stats | handcrafted | 3 | -0.0026 | 0.0005 | -0.0018 | 0 | 1 | 0.0300 | 0.0840 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | task_type_L1 | handcrafted | 3 | -0.0139 | 0.0026 | -0.0097 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | task_type_L12 | handcrafted | 3 | -0.0122 | 0.0015 | -0.0085 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | task_type_L2 | handcrafted | 3 | -0.0110 | 0.0003 | -0.0077 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 4 | mistralai/mistral-7b-chat | 500 | task_type_theme | handcrafted | 3 | -0.0167 | 0.0010 | -0.0116 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | combined | handcrafted | 3 | 0.0005 | 0.0009 | 0.0003 | 2 | 0 | 0.0920 | 0.4160 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | contrastive | handcrafted | 3 | -0.0028 | 0.0004 | -0.0019 | 0 | 0 | 0.1080 | 0.1520 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | contrastive_hc | handcrafted | 3 | -0.0019 | 0.0020 | -0.0013 | 1 | 0 | 0.0600 | 0.1460 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | frozen | handcrafted | 3 | -0.0015 | 0.0003 | -0.0011 | 0 | 0 | 0.1700 | 0.1740 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | handcrafted_nik | handcrafted | 3 | 0.0000 | 0.0006 | 0.0000 | 2 | 0 | 0.5800 | 0.6600 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | regression | handcrafted | 3 | 0.0000 | 0.0019 | 0.0000 | 2 | 0 | 0.2280 | 0.3900 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | regression_hc | handcrafted | 3 | -0.0008 | 0.0017 | -0.0005 | 1 | 0 | 0.2940 | 0.4340 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | stats | handcrafted | 3 | -0.0025 | 0.0008 | -0.0017 | 0 | 1 | 0.0000 | 0.0540 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | task_type_L1 | handcrafted | 3 | -0.0009 | 0.0027 | -0.0006 | 1 | 0 | 0.1960 | 0.2320 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | task_type_L12 | handcrafted | 3 | -0.0006 | 0.0019 | -0.0004 | 1 | 1 | 0.0500 | 0.2700 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | task_type_L2 | handcrafted | 3 | -0.0031 | 0.0035 | -0.0021 | 1 | 1 | 0.0020 | 0.3700 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 5 | task_type_theme | handcrafted | 3 | -0.0014 | 0.0018 | -0.0010 | 1 | 0 | 0.0760 | 0.6660 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | combined | handcrafted | 3 | -0.0014 | 0.0021 | -0.0010 | 1 | 0 | 0.0940 | 0.1600 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | contrastive | handcrafted | 3 | -0.0052 | 0.0030 | -0.0035 | 0 | 2 | 0.0040 | 0.0420 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | contrastive_hc | handcrafted | 3 | -0.0044 | 0.0039 | -0.0030 | 1 | 1 | 0.0080 | 0.0760 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | frozen | handcrafted | 3 | -0.0014 | 0.0019 | -0.0010 | 1 | 0 | 0.3300 | 0.4580 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | handcrafted_nik | handcrafted | 3 | 0.0013 | 0.0037 | 0.0009 | 2 | 1 | 0.0280 | 0.1260 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | regression | handcrafted | 3 | -0.0016 | 0.0025 | -0.0011 | 1 | 0 | 0.3260 | 0.4000 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | regression_hc | handcrafted | 3 | -0.0012 | 0.0010 | -0.0008 | 0 | 0 | 0.4800 | 0.8160 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | stats | handcrafted | 3 | -0.0040 | 0.0028 | -0.0028 | 0 | 1 | 0.0040 | 0.1060 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | task_type_L1 | handcrafted | 3 | -0.0089 | 0.0020 | -0.0061 | 0 | 3 | 0.0000 | 0.0140 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | task_type_L12 | handcrafted | 3 | -0.0073 | 0.0019 | -0.0050 | 0 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | task_type_L2 | handcrafted | 3 | -0.0098 | 0.0019 | -0.0067 | 0 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 50 | task_type_theme | handcrafted | 3 | -0.0020 | 0.0009 | -0.0013 | 0 | 0 | 0.2640 | 0.7320 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | combined | handcrafted | 3 | -0.0028 | 0.0013 | -0.0019 | 0 | 1 | 0.0140 | 0.1060 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | contrastive | handcrafted | 3 | -0.0038 | 0.0033 | -0.0026 | 0 | 1 | 0.0080 | 0.4760 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | contrastive_hc | handcrafted | 3 | -0.0037 | 0.0028 | -0.0025 | 1 | 1 | 0.0440 | 0.0740 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | frozen | handcrafted | 3 | -0.0026 | 0.0015 | -0.0018 | 0 | 0 | 0.1320 | 0.3780 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | handcrafted_nik | handcrafted | 3 | 0.0010 | 0.0036 | 0.0007 | 2 | 0 | 0.1160 | 0.1960 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | regression | handcrafted | 3 | -0.0007 | 0.0026 | -0.0005 | 2 | 0 | 0.2240 | 0.6940 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | regression_hc | handcrafted | 3 | -0.0004 | 0.0019 | -0.0003 | 1 | 0 | 0.4920 | 0.5720 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | stats | handcrafted | 3 | -0.0052 | 0.0018 | -0.0036 | 0 | 1 | 0.0020 | 0.1100 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | task_type_L1 | handcrafted | 3 | -0.0074 | 0.0038 | -0.0051 | 0 | 1 | 0.0200 | 0.0760 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | task_type_L12 | handcrafted | 3 | -0.0054 | 0.0017 | -0.0037 | 0 | 1 | 0.0140 | 0.0720 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | task_type_L2 | handcrafted | 3 | -0.0063 | 0.0022 | -0.0043 | 0 | 2 | 0.0100 | 0.0340 |
| routerbench | unseen | 5 | gpt-3.5-turbo-1106 | 500 | task_type_theme | handcrafted | 3 | 0.0047 | 0.0044 | 0.0032 | 3 | 1 | 0.0360 | 0.6900 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | combined | handcrafted | 3 | 0.0001 | 0.0012 | 0.0000 | 2 | 0 | 0.3040 | 0.3440 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | contrastive | handcrafted | 3 | -0.0029 | 0.0024 | -0.0021 | 0 | 1 | 0.0180 | 0.2180 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | contrastive_hc | handcrafted | 3 | -0.0031 | 0.0029 | -0.0022 | 1 | 2 | 0.0240 | 0.0480 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | frozen | handcrafted | 3 | -0.0017 | 0.0019 | -0.0012 | 1 | 0 | 0.1140 | 0.3960 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | handcrafted_nik | handcrafted | 3 | -0.0004 | 0.0012 | -0.0003 | 2 | 0 | 0.2540 | 0.6640 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | regression | handcrafted | 3 | -0.0021 | 0.0038 | -0.0015 | 1 | 1 | 0.0020 | 0.2420 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | regression_hc | handcrafted | 3 | -0.0014 | 0.0035 | -0.0010 | 1 | 1 | 0.0140 | 0.2620 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | stats | handcrafted | 3 | -0.0023 | 0.0017 | -0.0016 | 0 | 1 | 0.0220 | 0.0660 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | task_type_L1 | handcrafted | 3 | -0.0366 | 0.0041 | -0.0260 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | task_type_L12 | handcrafted | 3 | -0.0106 | 0.0010 | -0.0075 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | task_type_L2 | handcrafted | 3 | -0.0132 | 0.0022 | -0.0094 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 5 | task_type_theme | handcrafted | 3 | -0.0117 | 0.0020 | -0.0083 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | combined | handcrafted | 3 | 0.0001 | 0.0016 | 0.0001 | 2 | 0 | 0.1420 | 0.3040 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | contrastive | handcrafted | 3 | -0.0024 | 0.0024 | -0.0017 | 0 | 1 | 0.0200 | 0.6140 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | contrastive_hc | handcrafted | 3 | -0.0026 | 0.0026 | -0.0018 | 1 | 1 | 0.0240 | 0.1720 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | frozen | handcrafted | 3 | -0.0011 | 0.0021 | -0.0008 | 2 | 0 | 0.0960 | 0.7500 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | handcrafted_nik | handcrafted | 3 | -0.0018 | 0.0015 | -0.0012 | 1 | 0 | 0.0860 | 0.2520 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | regression | handcrafted | 3 | -0.0021 | 0.0036 | -0.0015 | 1 | 1 | 0.0080 | 0.2420 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | regression_hc | handcrafted | 3 | -0.0014 | 0.0032 | -0.0010 | 1 | 1 | 0.0320 | 0.2620 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | stats | handcrafted | 3 | -0.0024 | 0.0017 | -0.0017 | 0 | 1 | 0.0180 | 0.0920 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | task_type_L1 | handcrafted | 3 | -0.0368 | 0.0041 | -0.0261 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | task_type_L12 | handcrafted | 3 | -0.0114 | 0.0012 | -0.0081 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | task_type_L2 | handcrafted | 3 | -0.0157 | 0.0018 | -0.0112 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 50 | task_type_theme | handcrafted | 3 | -0.0137 | 0.0034 | -0.0097 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | combined | handcrafted | 3 | -0.0000 | 0.0017 | -0.0000 | 2 | 0 | 0.1260 | 0.2060 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | contrastive | handcrafted | 3 | -0.0029 | 0.0023 | -0.0020 | 0 | 1 | 0.0200 | 0.1940 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | contrastive_hc | handcrafted | 3 | -0.0032 | 0.0030 | -0.0023 | 1 | 2 | 0.0260 | 0.0280 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | frozen | handcrafted | 3 | -0.0016 | 0.0019 | -0.0012 | 1 | 0 | 0.1000 | 0.4760 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | handcrafted_nik | handcrafted | 3 | -0.0004 | 0.0013 | -0.0002 | 2 | 0 | 0.2300 | 0.5740 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | regression | handcrafted | 3 | -0.0020 | 0.0035 | -0.0014 | 1 | 1 | 0.0080 | 0.2620 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | regression_hc | handcrafted | 3 | -0.0012 | 0.0033 | -0.0008 | 1 | 1 | 0.0320 | 0.2400 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | stats | handcrafted | 3 | -0.0022 | 0.0018 | -0.0016 | 1 | 1 | 0.0140 | 0.0780 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | task_type_L1 | handcrafted | 3 | -0.0317 | 0.0068 | -0.0225 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | task_type_L12 | handcrafted | 3 | -0.0106 | 0.0006 | -0.0075 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | task_type_L2 | handcrafted | 3 | -0.0149 | 0.0008 | -0.0106 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 6 | gpt-4-1106-preview | 500 | task_type_theme | handcrafted | 3 | -0.0119 | 0.0018 | -0.0085 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | combined | handcrafted | 3 | 0.0010 | 0.0007 | 0.0007 | 3 | 1 | 0.0280 | 0.4160 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | contrastive | handcrafted | 3 | -0.0009 | 0.0089 | -0.0006 | 1 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | contrastive_hc | handcrafted | 3 | -0.0033 | 0.0114 | -0.0024 | 1 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | frozen | handcrafted | 3 | -0.0010 | 0.0025 | -0.0007 | 2 | 0 | 0.1220 | 0.6140 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | handcrafted_nik | handcrafted | 3 | -0.0023 | 0.0024 | -0.0017 | 0 | 1 | 0.0060 | 0.4420 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | regression | handcrafted | 3 | -0.0054 | 0.0043 | -0.0039 | 1 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | regression_hc | handcrafted | 3 | -0.0040 | 0.0056 | -0.0028 | 1 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | stats | handcrafted | 3 | -0.0007 | 0.0009 | -0.0005 | 1 | 0 | 0.1720 | 0.6860 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | task_type_L1 | handcrafted | 3 | -0.0183 | 0.0059 | -0.0132 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | task_type_L12 | handcrafted | 3 | -0.0111 | 0.0048 | -0.0080 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | task_type_L2 | handcrafted | 3 | -0.0090 | 0.0045 | -0.0065 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 5 | task_type_theme | handcrafted | 3 | -0.0166 | 0.0050 | -0.0119 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | combined | handcrafted | 3 | 0.0038 | 0.0022 | 0.0028 | 3 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | contrastive | handcrafted | 3 | -0.0052 | 0.0022 | -0.0037 | 0 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | contrastive_hc | handcrafted | 3 | -0.0080 | 0.0004 | -0.0057 | 0 | 3 | 0.0000 | 0.0020 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | frozen | handcrafted | 3 | 0.0032 | 0.0033 | 0.0023 | 2 | 1 | 0.0000 | 0.0680 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | handcrafted_nik | handcrafted | 3 | 0.0007 | 0.0014 | 0.0005 | 2 | 0 | 0.2100 | 0.5000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | regression | handcrafted | 3 | -0.0110 | 0.0010 | -0.0079 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | regression_hc | handcrafted | 3 | -0.0101 | 0.0018 | -0.0072 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | stats | handcrafted | 3 | -0.0014 | 0.0007 | -0.0010 | 0 | 0 | 0.3100 | 0.4240 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | task_type_L1 | handcrafted | 3 | -0.0193 | 0.0059 | -0.0138 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | task_type_L12 | handcrafted | 3 | -0.0049 | 0.0026 | -0.0035 | 0 | 2 | 0.0000 | 0.0420 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | task_type_L2 | handcrafted | 3 | -0.0060 | 0.0038 | -0.0043 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 50 | task_type_theme | handcrafted | 3 | -0.0045 | 0.0072 | -0.0032 | 1 | 1 | 0.0000 | 0.5680 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | combined | handcrafted | 3 | 0.0013 | 0.0007 | 0.0009 | 3 | 0 | 0.0680 | 0.2220 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | contrastive | handcrafted | 3 | -0.0095 | 0.0023 | -0.0068 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | contrastive_hc | handcrafted | 3 | -0.0096 | 0.0032 | -0.0069 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | frozen | handcrafted | 3 | 0.0017 | 0.0042 | 0.0012 | 2 | 1 | 0.0000 | 0.2160 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | handcrafted_nik | handcrafted | 3 | 0.0014 | 0.0012 | 0.0010 | 3 | 0 | 0.0900 | 0.5420 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | regression | handcrafted | 3 | -0.0127 | 0.0013 | -0.0091 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | regression_hc | handcrafted | 3 | -0.0115 | 0.0034 | -0.0082 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | stats | handcrafted | 3 | -0.0011 | 0.0020 | -0.0008 | 1 | 0 | 0.1400 | 0.1720 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | task_type_L1 | handcrafted | 3 | -0.0231 | 0.0024 | -0.0166 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | task_type_L12 | handcrafted | 3 | -0.0085 | 0.0029 | -0.0061 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | task_type_L2 | handcrafted | 3 | -0.0099 | 0.0030 | -0.0071 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 7 | zero-one-ai/Yi-34B-Chat | 500 | task_type_theme | handcrafted | 3 | -0.0067 | 0.0052 | -0.0048 | 0 | 2 | 0.0000 | 0.0080 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | combined | handcrafted | 3 | -0.0039 | 0.0079 | -0.0028 | 2 | 2 | 0.0000 | 0.0220 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | contrastive | handcrafted | 3 | 0.0070 | 0.0102 | 0.0050 | 2 | 1 | 0.0000 | 0.8020 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | contrastive_hc | handcrafted | 3 | 0.0051 | 0.0059 | 0.0036 | 3 | 1 | 0.0000 | 0.4880 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | frozen | handcrafted | 3 | -0.0220 | 0.0168 | -0.0158 | 0 | 2 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | handcrafted_nik | handcrafted | 3 | -0.0040 | 0.0058 | -0.0028 | 1 | 1 | 0.0000 | 0.6000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | regression | handcrafted | 3 | 0.0018 | 0.0040 | 0.0013 | 2 | 1 | 0.0260 | 0.1320 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | regression_hc | handcrafted | 3 | 0.0018 | 0.0043 | 0.0013 | 2 | 1 | 0.0480 | 0.0620 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | stats | handcrafted | 3 | -0.0044 | 0.0031 | -0.0032 | 0 | 1 | 0.0000 | 0.1280 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | task_type_L1 | handcrafted | 3 | -0.0359 | 0.0196 | -0.0257 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | task_type_L12 | handcrafted | 3 | -0.0515 | 0.0085 | -0.0369 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | task_type_L2 | handcrafted | 3 | -0.0515 | 0.0077 | -0.0369 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 5 | task_type_theme | handcrafted | 3 | -0.0406 | 0.0250 | -0.0290 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | combined | handcrafted | 3 | 0.0022 | 0.0004 | 0.0016 | 3 | 2 | 0.0120 | 0.0220 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | contrastive | handcrafted | 3 | -0.0007 | 0.0003 | -0.0005 | 0 | 0 | 0.6460 | 0.8060 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | contrastive_hc | handcrafted | 3 | -0.0025 | 0.0010 | -0.0018 | 0 | 0 | 0.1220 | 0.2620 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | frozen | handcrafted | 3 | -0.0014 | 0.0011 | -0.0010 | 1 | 0 | 0.2660 | 0.3620 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | handcrafted_nik | handcrafted | 3 | 0.0008 | 0.0015 | 0.0006 | 1 | 0 | 0.1200 | 0.8060 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | regression | handcrafted | 3 | -0.0007 | 0.0027 | -0.0005 | 2 | 0 | 0.0940 | 0.5340 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | regression_hc | handcrafted | 3 | 0.0006 | 0.0021 | 0.0004 | 2 | 0 | 0.1580 | 0.4920 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | stats | handcrafted | 3 | -0.0011 | 0.0007 | -0.0008 | 0 | 0 | 0.3440 | 0.4420 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | task_type_L1 | handcrafted | 3 | -0.0398 | 0.0035 | -0.0285 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | task_type_L12 | handcrafted | 3 | -0.0400 | 0.0042 | -0.0287 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | task_type_L2 | handcrafted | 3 | -0.0375 | 0.0048 | -0.0269 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 50 | task_type_theme | handcrafted | 3 | -0.0307 | 0.0050 | -0.0220 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | combined | handcrafted | 3 | 0.0019 | 0.0004 | 0.0013 | 3 | 1 | 0.0300 | 0.0540 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | contrastive | handcrafted | 3 | -0.0048 | 0.0027 | -0.0034 | 0 | 2 | 0.0080 | 0.0400 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | contrastive_hc | handcrafted | 3 | -0.0086 | 0.0041 | -0.0062 | 0 | 2 | 0.0000 | 0.0020 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | frozen | handcrafted | 3 | -0.0002 | 0.0011 | -0.0002 | 1 | 0 | 0.4960 | 0.6120 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | handcrafted_nik | handcrafted | 3 | 0.0007 | 0.0028 | 0.0005 | 1 | 1 | 0.0200 | 0.3980 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | regression | handcrafted | 3 | -0.0041 | 0.0004 | -0.0030 | 0 | 0 | 0.0580 | 0.1140 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | regression_hc | handcrafted | 3 | -0.0040 | 0.0027 | -0.0028 | 0 | 1 | 0.0020 | 0.1300 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | stats | handcrafted | 3 | -0.0021 | 0.0015 | -0.0015 | 0 | 1 | 0.0480 | 0.2840 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | task_type_L1 | handcrafted | 3 | -0.0357 | 0.0010 | -0.0256 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | task_type_L12 | handcrafted | 3 | -0.0380 | 0.0025 | -0.0272 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | task_type_L2 | handcrafted | 3 | -0.0352 | 0.0039 | -0.0252 | 0 | 3 | 0.0000 | 0.0000 |
| routerbench | unseen | 8 | mistralai/mixtral-8x7b-chat | 500 | task_type_theme | handcrafted | 3 | -0.0419 | 0.0051 | -0.0300 | 0 | 3 | 0.0000 | 0.0000 |
