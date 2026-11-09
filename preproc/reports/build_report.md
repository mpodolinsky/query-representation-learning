# Build report

Built 2026-11-09 02:27 at commit baf8547-dirty by `preproc/build.py`.

## LLMRouterBench

- **12,068 queries × 13 models = 156,884 (query, model) rows**; score matrix complete: True; scores in [0.0, 1.0] (no rescaling needed); 1.4% of scores are not 0/1 (themes: arenahard 22%).
- text differs across models: 2
- hle without category: 0
- arenahard without category: 0
- duplicate prompts dropped: 0
- costs imputed (no token counts): 1,879
- excluded datasets: swe-bench (verified): no qwen3-235b-a22b-thinking-2507 results; tau2 (test): no gpt-5-chat results
- empty outputs (mostly reasoning models hitting their token limit; scored as published): 2,636; 'failed to generate' (API failures, scored 0 as published): 8
- cost = tokens × Table 1 price. The recorded `cost` is 0 on 532 records that have token counts; recorded vs recomputed total: gemini-2.5-flash -2.2%, qwen3-235b-a22b-2507 +3.3%, qwen3-235b-a22b-thinking-2507 -22.2%, gpt-5-chat -3.3%, gpt-5 -9.4% (others within 0.5%)

### Themes and splits

| theme | queries | share | subtasks | seed0 train/val/test | seed1 train/val/test | seed2 train/val/test |
|---|---|---|---|---|---|---|
| aime | 60 | 0.5% | 1 | 42/6/12 | 42/6/12 | 42/6/12 |
| arc-agi | 400 | 3.3% | 1 | 280/40/80 | 280/40/80 | 280/40/80 |
| arenahard | 750 | 6.2% | 3 | 525/75/150 | 525/75/150 | 525/75/150 |
| gpqa | 198 | 1.6% | 1 | 139/20/39 | 139/20/39 | 139/20/39 |
| hle | 2158 | 17.9% | 8 | 1511/216/431 | 1511/216/431 | 1511/216/431 |
| livecodebench | 1055 | 8.7% | 1 | 739/106/210 | 739/106/210 | 739/106/210 |
| livemathbench | 121 | 1.0% | 1 | 85/12/24 | 85/12/24 | 85/12/24 |
| mmlupro | 3000 | 24.9% | 14 | 2100/300/600 | 2100/300/600 | 2100/300/600 |
| simpleqa | 4326 | 35.8% | 1 | 3028/433/865 | 3028/433/865 | 3028/433/865 |

### Models

| model | display_name | release | epoch | price_in_per_1m | price_out_per_1m | mean_cost | mean_score | n_cost_imputed |
|---|---|---|---|---|---|---|---|---|
| deepseek-v3-0324 | DeepSeek-V3-0324 | 2025-03-24 | 0 | 0.25 | 0.88 | 0.000682 | 0.418 | 0 |
| claude-sonnet-4 | Claude-Sonnet-4 | 2025-05-22 | 1 | 3 | 15 | 0.00848 | 0.381 | 1 |
| deepseek-r1-0528 | DeepSeek-R1-0528 | 2025-05-28 | 2 | 0.5 | 2.15 | 0.0137 | 0.478 | 0 |
| gemini-2.5-flash | Gemini-2.5-Flash | 2025-06-17 | 3 | 0.3 | 2.5 | 0.00875 | 0.434 | 32 |
| gemini-2.5-pro | Gemini-2.5-Pro | 2025-06-17 | 3 | 1.25 | 10 | 0.0627 | 0.599 | 201 |
| qwen3-235b-a22b-2507 | Qwen3-235B-A22B-2507 | 2025-07-21 | 4 | 0.09 | 0.6 | 0.000814 | 0.546 | 194 |
| qwen3-235b-a22b-thinking-2507 | Qwen3-235B-A22B-Thinking-2507 | 2025-07-25 | 5 | 0.3 | 2.9 | 0.0109 | 0.527 | 1408 |
| intern-s1 | Intern-S1 | 2025-07-26 | 6 | 0.18 | 0.54 | 0.00289 | 0.379 | 0 |
| gpt-5-chat | GPT-5-chat | 2025-08-07 | 7 | 1.25 | 10 | 0.00454 | 0.479 | 0 |
| gpt-5 | GPT-5-medium | 2025-08-07 | 7 | 1.25 | 10 | 0.0351 | 0.598 | 11 |
| kimi-k2-0905 | Kimi-K2-0905 | 2025-09-05 | 8 | 0.5 | 2 | 0.00131 | 0.443 | 2 |
| deepseek-v3.1-terminus | DeepSeek-V3.1-Terminus | 2025-09-22 | 9 | 0.27 | 1 | 0.000907 | 0.440 | 1 |
| glm-4.6 | GLM-4.6 | 2025-09-30 | 10 | 0.6 | 2.2 | 0.0168 | 0.444 | 29 |

### Mean score per theme

| theme | DeepSeek-V3-0324 | Claude-Sonnet-4 | DeepSeek-R1-0528 | Gemini-2.5-Flash | Gemini-2.5-Pro | Qwen3-235B-A22B-2507 | Qwen3-235B-A22B-Thinking-2507 | Intern-S1 | GPT-5-chat | GPT-5-medium | Kimi-K2-0905 | DeepSeek-V3.1-Terminus | GLM-4.6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aime | 0.43 | 0.37 | 0.85 | 0.63 | 0.85 | 0.77 | 0.87 | 0.48 | 0.72 | 0.88 | 0.65 | 0.55 | 0.82 |
| arc-agi | 0.13 | 0.23 | 0.23 | 0.11 | 0.43 | 0.25 | 0.16 | 0.04 | 0.09 | 0.52 | 0.09 | 0.15 | 0.17 |
| arenahard | 0.60 | 0.55 | 0.64 | 0.56 | 0.77 | 0.73 | 0.74 | 0.67 | 0.69 | 0.70 | 0.71 | 0.66 | 0.66 |
| gpqa | 0.60 | 0.69 | 0.80 | 0.66 | 0.85 | 0.59 | 0.80 | 0.66 | 0.74 | 0.85 | 0.73 | 0.76 | 0.75 |
| hle | 0.04 | 0.05 | 0.16 | 0.08 | 0.22 | 0.09 | 0.08 | 0.09 | 0.06 | 0.26 | 0.06 | 0.09 | 0.16 |
| livecodebench | 0.67 | 0.58 | 0.80 | 0.60 | 0.79 | 0.64 | 0.78 | 0.49 | 0.62 | 0.86 | 0.67 | 0.67 | 0.63 |
| livemathbench | 0.62 | 0.61 | 0.78 | 0.74 | 0.50 | 0.76 | 0.53 | 0.69 | 0.58 | 0.79 | 0.72 | 0.74 | 0.64 |
| mmlupro | 0.78 | 0.83 | 0.84 | 0.81 | 0.86 | 0.83 | 0.79 | 0.82 | 0.81 | 0.87 | 0.80 | 0.84 | 0.80 |
| simpleqa | 0.28 | 0.15 | 0.27 | 0.30 | 0.54 | 0.54 | 0.48 | 0.15 | 0.40 | 0.48 | 0.29 | 0.24 | 0.26 |

### Release epochs: mean cost per query (USD; blank = not released yet)

| epoch | date | DeepSeek-V3-0324 | Claude-Sonnet-4 | DeepSeek-R1-0528 | Gemini-2.5-Flash | Gemini-2.5-Pro | Qwen3-235B-A22B-2507 | Qwen3-235B-A22B-Thinking-2507 | Intern-S1 | GPT-5-chat | GPT-5-medium | Kimi-K2-0905 | DeepSeek-V3.1-Terminus | GLM-4.6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2025-03-24 | 6.82e-04 |  |  |  |  |  |  |  |  |  |  |  |  |
| 1 | 2025-05-22 | 6.82e-04 | 8.48e-03 |  |  |  |  |  |  |  |  |  |  |  |
| 2 | 2025-05-28 | 6.82e-04 | 8.48e-03 | 1.37e-02 |  |  |  |  |  |  |  |  |  |  |
| 3 | 2025-06-17 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 |  |  |  |  |  |  |  |  |
| 4 | 2025-07-21 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 |  |  |  |  |  |  |  |
| 5 | 2025-07-25 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 |  |  |  |  |  |  |
| 6 | 2025-07-26 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 | 2.89e-03 |  |  |  |  |  |
| 7 | 2025-08-07 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 | 2.89e-03 | 4.54e-03 | 3.51e-02 |  |  |  |
| 8 | 2025-09-05 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 | 2.89e-03 | 4.54e-03 | 3.51e-02 | 1.31e-03 |  |  |
| 9 | 2025-09-22 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 | 2.89e-03 | 4.54e-03 | 3.51e-02 | 1.31e-03 | 9.07e-04 |  |
| 10 | 2025-09-30 | 6.82e-04 | 8.48e-03 | 1.37e-02 | 8.75e-03 | 6.27e-02 | 8.14e-04 | 1.09e-02 | 2.89e-03 | 4.54e-03 | 3.51e-02 | 1.31e-03 | 9.07e-04 | 1.68e-02 |

### Unseen-model instances

| instance | epoch | date | new_model | pool |
|---|---|---|---|---|
| 0 | 1 | 2025-05-22 | claude-sonnet-4 | 2 models: deepseek-v3-0324, claude-sonnet-4 |
| 1 | 2 | 2025-05-28 | deepseek-r1-0528 | 3 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528 |
| 2 | 3 | 2025-06-17 | gemini-2.5-flash | 4 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash |
| 3 | 3 | 2025-06-17 | gemini-2.5-pro | 4 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-pro |
| 4 | 4 | 2025-07-21 | qwen3-235b-a22b-2507 | 6 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507 |
| 5 | 5 | 2025-07-25 | qwen3-235b-a22b-thinking-2507 | 7 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507 |
| 6 | 6 | 2025-07-26 | intern-s1 | 8 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1 |
| 7 | 7 | 2025-08-07 | gpt-5-chat | 9 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1, gpt-5-chat |
| 8 | 7 | 2025-08-07 | gpt-5 | 9 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1, gpt-5 |
| 9 | 8 | 2025-09-05 | kimi-k2-0905 | 11 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1, gpt-5-chat, gpt-5, kimi-k2-0905 |
| 10 | 9 | 2025-09-22 | deepseek-v3.1-terminus | 12 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1, gpt-5-chat, gpt-5, kimi-k2-0905, deepseek-v3.1-terminus |
| 11 | 10 | 2025-09-30 | glm-4.6 | 13 models: deepseek-v3-0324, claude-sonnet-4, deepseek-r1-0528, gemini-2.5-flash, gemini-2.5-pro, qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, intern-s1, gpt-5-chat, gpt-5, kimi-k2-0905, deepseek-v3.1-terminus, glm-4.6 |

### Probe coverage (split seed 0, mean over probe seeds 0–4, 9 themes)

Probes depend only on the training split and the probe seed, so every unseen instance gets the same ones. *Max theme miscount* is the largest |probes of a theme − n × its share of train|: stratified sampling keeps the theme mix proportional (miscount about 1 or less); it does not guarantee that a small theme is covered.

| n | random: themes covered | random: max theme miscount | stratified: themes covered | stratified: max theme miscount |
|---|---|---|---|---|
| 1 | 1.0 | 0.9 | 1.0 | 0.6 |
| 2 | 2.0 | 0.8 | 2.0 | 0.5 |
| 5 | 3.8 | 1.1 | 4.0 | 0.6 |
| 10 | 4.8 | 1.8 | 5.0 | 0.5 |
| 20 | 6.2 | 2.5 | 6.0 | 0.4 |
| 50 | 7.8 | 4.7 | 8.0 | 0.5 |
| 100 | 8.8 | 5.2 | 8.0 | 0.5 |
| 200 | 8.8 | 8.4 | 9.0 | 0.5 |
| 500 | 9.0 | 9.2 | 9.0 | 0.6 |
| 1000 | 9.0 | 12.9 | 9.0 | 0.6 |
| all (8449) | 9.0 | 0.0 | 9.0 | 0.0 |

## RouterBench

- **36,478 queries × 11 models = 401,258 (query, model) rows**; score matrix complete: True; scores in [0.0, 1.0] (no rescaling needed); 21.2% of scores are not 0/1 (themes: chinese 1%, consensus_summary 72%, grade-school-math 99%, mtbench 68%).
- test-match queries dropped: 3
- duplicate prompts dropped: 16
- cost = recorded `total_cost`; prices in the model table are from `deps/routerbench/routers/common.py` (information only)

### Themes and splits

| theme | queries | share | subtasks | seed0 train/val/test | seed1 train/val/test | seed2 train/val/test |
|---|---|---|---|---|---|---|
| abstract2title | 253 | 0.7% | 1 | 177/25/51 | 177/25/51 | 177/25/51 |
| accounting_audit | 30 | 0.1% | 1 | 21/3/6 | 21/3/6 | 21/3/6 |
| arc-challenge | 1470 | 4.0% | 1 | 1029/147/294 | 1029/147/294 | 1029/147/294 |
| bias_detection | 284 | 0.8% | 1 | 199/28/57 | 199/28/57 | 199/28/57 |
| chinese | 782 | 2.1% | 16 | 547/78/157 | 547/78/157 | 547/78/157 |
| consensus_summary | 358 | 1.0% | 1 | 251/36/71 | 251/36/71 | 251/36/71 |
| grade-school-math | 7450 | 20.4% | 1 | 5215/745/1490 | 5215/745/1490 | 5215/745/1490 |
| hellaswag | 10042 | 27.5% | 1 | 7029/1004/2009 | 7029/1004/2009 | 7029/1004/2009 |
| mbpp | 425 | 1.2% | 1 | 298/43/84 | 298/43/84 | 298/43/84 |
| mmlu | 14037 | 38.5% | 57 | 9826/1404/2807 | 9826/1404/2807 | 9826/1404/2807 |
| mtbench | 80 | 0.2% | 3 | 56/8/16 | 56/8/16 | 56/8/16 |
| winogrande | 1267 | 3.5% | 1 | 887/127/253 | 887/127/253 | 887/127/253 |

### Models

| model | display_name | release | epoch | price_in_per_1m | price_out_per_1m | mean_cost | mean_score | n_cost_imputed |
|---|---|---|---|---|---|---|---|---|
| claude-instant-v1 | claude-instant-v1 | 2023-03 | 0 | 0.08 | 0.24 | 0.000233 | 0.598 | 0 |
| claude-v1 | claude-v1 | 2023-03 | 0 | 0.8 | 2.4 | 0.00214 | 0.630 | 0 |
| claude-v2 | claude-v2 | 2023-07 | 1 | 0.8 | 2.4 | 0.00242 | 0.636 | 0 |
| meta/llama-2-70b-chat | llama-2-70b-chat | 2023-07 | 1 | 0.09 | 0.09 | 0.000203 | 0.329 | 0 |
| WizardLM/WizardLM-13B-V1.2 | WizardLM-13B-V1.2 | 2023-07 | 1 | 0.03 | 0.03 | 7.29e-05 | 0.431 | 0 |
| meta/code-llama-instruct-34b-chat | code-llama-instruct-34b-chat | 2023-08 | 2 | 0.0776 | 0.0776 | 0.000172 | 0.202 | 0 |
| mistralai/mistral-7b-chat | mistral-7b-chat | 2023-09 | 3 | 0.02 | 0.02 | 4.57e-05 | 0.306 | 0 |
| gpt-3.5-turbo-1106 | gpt-3.5-turbo-1106 | 2023-11 | 4 | 0.1 | 0.2 | 0.000243 | 0.619 | 0 |
| gpt-4-1106-preview | gpt-4-1106-preview | 2023-11 | 4 | 1 | 3 | 0.00329 | 0.781 | 0 |
| zero-one-ai/Yi-34B-Chat | Yi-34B-Chat | 2023-11 | 4 | 0.08 | 0.08 | 0.000186 | 0.647 | 0 |
| mistralai/mixtral-8x7b-chat | mixtral-8x7b-chat | 2023-12 | 5 | 0.06 | 0.06 | 0.000135 | 0.547 | 0 |

### Mean score per theme

| theme | claude-instant-v1 | claude-v1 | claude-v2 | llama-2-70b-chat | WizardLM-13B-V1.2 | code-llama-instruct-34b-chat | mistral-7b-chat | gpt-3.5-turbo-1106 | gpt-4-1106-preview | Yi-34B-Chat | mixtral-8x7b-chat |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abstract2title | 1.00 | 1.00 | 1.00 | 0.99 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| accounting_audit | 0.53 | 0.67 | 0.53 | 0.00 | 0.30 | 0.00 | 0.20 | 0.60 | 0.80 | 0.20 | 0.63 |
| arc-challenge | 0.80 | 0.87 | 0.87 | 0.73 | 0.61 | 0.37 | 0.39 | 0.83 | 0.96 | 0.86 | 0.83 |
| bias_detection | 0.26 | 0.33 | 0.30 | 0.23 | 0.21 | 0.07 | 0.06 | 0.33 | 0.37 | 0.07 | 0.27 |
| chinese | 0.06 | 0.26 | 0.17 | 0.01 | 0.08 | 0.01 | 0.05 | 0.31 | 0.48 | 0.07 | 0.24 |
| consensus_summary | 0.68 | 0.61 | 0.67 | 0.67 | 0.59 | 0.66 | 0.64 | 0.62 | 0.57 | 0.64 | 0.69 |
| grade-school-math | 0.63 | 0.65 | 0.66 | 0.52 | 0.51 | 0.46 | 0.41 | 0.60 | 0.66 | 0.55 | 0.52 |
| hellaswag | 0.59 | 0.57 | 0.62 | 0.53 | 0.33 | 0.21 | 0.25 | 0.59 | 0.84 | 0.74 | 0.42 |
| mbpp | 0.60 | 0.60 | 0.64 | 0.33 | 0.37 | 0.52 | 0.34 | 0.65 | 0.69 | 0.39 | 0.54 |
| mmlu | 0.60 | 0.66 | 0.63 | 0.03 | 0.45 | 0.00 | 0.25 | 0.65 | 0.81 | 0.66 | 0.64 |
| mtbench | 0.63 | 0.65 | 0.68 | 0.59 | 0.55 | 0.53 | 0.52 | 0.69 | 0.81 | 0.64 | 0.65 |
| winogrande | 0.62 | 0.66 | 0.66 | 0.48 | 0.51 | 0.38 | 0.52 | 0.58 | 0.82 | 0.63 | 0.55 |

### Release epochs: mean cost per query (USD; blank = not released yet)

| epoch | date | claude-instant-v1 | claude-v1 | claude-v2 | llama-2-70b-chat | WizardLM-13B-V1.2 | code-llama-instruct-34b-chat | mistral-7b-chat | gpt-3.5-turbo-1106 | gpt-4-1106-preview | Yi-34B-Chat | mixtral-8x7b-chat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2023-03 | 2.33e-04 | 2.14e-03 |  |  |  |  |  |  |  |  |  |
| 1 | 2023-07 | 2.33e-04 | 2.14e-03 | 2.42e-03 | 2.03e-04 | 7.29e-05 |  |  |  |  |  |  |
| 2 | 2023-08 | 2.33e-04 | 2.14e-03 | 2.42e-03 | 2.03e-04 | 7.29e-05 | 1.72e-04 |  |  |  |  |  |
| 3 | 2023-09 | 2.33e-04 | 2.14e-03 | 2.42e-03 | 2.03e-04 | 7.29e-05 | 1.72e-04 | 4.57e-05 |  |  |  |  |
| 4 | 2023-11 | 2.33e-04 | 2.14e-03 | 2.42e-03 | 2.03e-04 | 7.29e-05 | 1.72e-04 | 4.57e-05 | 2.43e-04 | 3.29e-03 | 1.86e-04 |  |
| 5 | 2023-12 | 2.33e-04 | 2.14e-03 | 2.42e-03 | 2.03e-04 | 7.29e-05 | 1.72e-04 | 4.57e-05 | 2.43e-04 | 3.29e-03 | 1.86e-04 | 1.35e-04 |

### Unseen-model instances

| instance | epoch | date | new_model | pool |
|---|---|---|---|---|
| 0 | 1 | 2023-07 | claude-v2 | 3 models: claude-instant-v1, claude-v1, claude-v2 |
| 1 | 1 | 2023-07 | meta/llama-2-70b-chat | 3 models: claude-instant-v1, claude-v1, meta/llama-2-70b-chat |
| 2 | 1 | 2023-07 | WizardLM/WizardLM-13B-V1.2 | 3 models: claude-instant-v1, claude-v1, WizardLM/WizardLM-13B-V1.2 |
| 3 | 2 | 2023-08 | meta/code-llama-instruct-34b-chat | 6 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat |
| 4 | 3 | 2023-09 | mistralai/mistral-7b-chat | 7 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat, mistralai/mistral-7b-chat |
| 5 | 4 | 2023-11 | gpt-3.5-turbo-1106 | 8 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat, mistralai/mistral-7b-chat, gpt-3.5-turbo-1106 |
| 6 | 4 | 2023-11 | gpt-4-1106-preview | 8 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat, mistralai/mistral-7b-chat, gpt-4-1106-preview |
| 7 | 4 | 2023-11 | zero-one-ai/Yi-34B-Chat | 8 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat, mistralai/mistral-7b-chat, zero-one-ai/Yi-34B-Chat |
| 8 | 5 | 2023-12 | mistralai/mixtral-8x7b-chat | 11 models: claude-instant-v1, claude-v1, claude-v2, meta/llama-2-70b-chat, WizardLM/WizardLM-13B-V1.2, meta/code-llama-instruct-34b-chat, mistralai/mistral-7b-chat, gpt-3.5-turbo-1106, gpt-4-1106-preview, zero-one-ai/Yi-34B-Chat, mistralai/mixtral-8x7b-chat |

### Probe coverage (split seed 0, mean over probe seeds 0–4, 12 themes)

Probes depend only on the training split and the probe seed, so every unseen instance gets the same ones. *Max theme miscount* is the largest |probes of a theme − n × its share of train|: stratified sampling keeps the theme mix proportional (miscount about 1 or less); it does not guarantee that a small theme is covered.

| n | random: themes covered | random: max theme miscount | stratified: themes covered | stratified: max theme miscount |
|---|---|---|---|---|
| 1 | 1.0 | 0.7 | 1.0 | 0.6 |
| 2 | 1.8 | 0.7 | 2.0 | 0.4 |
| 5 | 3.0 | 1.3 | 3.0 | 0.6 |
| 10 | 3.8 | 1.8 | 3.0 | 1.2 |
| 20 | 5.2 | 2.3 | 5.0 | 0.5 |
| 50 | 7.6 | 3.6 | 7.0 | 0.8 |
| 100 | 8.2 | 6.1 | 10.0 | 0.5 |
| 200 | 10.4 | 7.4 | 10.0 | 1.0 |
| 500 | 11.0 | 11.8 | 11.0 | 0.6 |
| 1000 | 11.6 | 19.7 | 12.0 | 0.4 |
| all (25535) | 12.0 | 0.0 | 12.0 | 0.0 |

## Table digests

Content hashes of the processed tables; a rebuild must reproduce them.

- `llmrouterbench/queries`: 61a0f92082c1ad1b
- `llmrouterbench/scores`: 43b75f75ab4d8417
- `routerbench/queries`: b27c4def76413f2a
- `routerbench/scores`: 1b1e421f9a28aeca
