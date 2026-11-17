# Offline task-type labeling (Alexandros)

Gives every query of both benchmarks a hierarchical task label, **domain -> subdomain -> specific task**, with a
local LLM (Qwen3-32B through vLLM, guided JSON decoding, a closed taxonomy). Arman's `theme` is the source dataset
and `subtask` is finer only for MMLU-Pro, HLE, ArenaHard and RouterBench; several themes span many domains (HLE,
MMLU-Pro, ArenaHard, SimpleQA, MT-Bench). The labels feed RQ1a (how much of a learned embedding does task type
alone recover), evaluated at each level in [`../alexandros-handcrafted/`](../alexandros-handcrafted/README.md).

| File | What |
|---|---|
| `taxonomy.py` | the closed taxonomy (`DOMAINS`, 11 domains x 90 subdomains), `VERSION`, JSON schema, prompt text blocks, dataset glossary |
| `label_tasks.py` | the vLLM labeling script: prompts, dedup, shards, resume, metadata, time budget, `--dry-run`, `--limit` |
| `merge_labels.py` | concatenates shards, checks coverage, writes `task_labels.parquet`, a markdown report and a hand-check CSV |
| `check_env.sh` | prints arch / GPU / python / vLLM / torch and checks the model directory; run first on the node |
| `download_model.sh` | `hf download Qwen/Qwen3-32B --local-dir ...` for a login node (or symlink the copy already on scratch) |
| `sbatch/label_gh_dev.slurm` | the Vista gh-dev job: check_env -> 50-query smoke test -> full run (both benchmarks) -> merge |
| `test_labeling.py` | 19 CPU-only tests with a stub model (`python -m pytest -q labeling`, 2 s) |
| `reports/` | `dry_run_prompt_stats.txt`, `<benchmark>_labels_report.md`, `<benchmark>_handcheck_sample.csv` (filled: `correct` = 1 / L1 / 0, `note`), `handcheck_summary.md` (accuracy and error classes from job 1134736) |
| `out/` (gitignored) | `<benchmark>/shard_XXXXX.parquet`, `metadata.json`, `labels_full.parquet`; `<benchmark>_limitN/` for smoke runs |

Input: `preproc/data/<benchmark>/queries.parquet` (Arman's build, committed on his branch; `query_id, theme, subtask,
query, prompt, n_chars`, row order = query index). LLMRouterBench 12,068 rows (9 themes), RouterBench 36,478 rows
(12 themes); 2 duplicated query strings in LLMRouterBench, none in RouterBench.

## How to run

```bash
# 0. login node, once: the model (~62 GB bf16). Either download ...
bash labeling/download_model.sh $SCRATCH/models/Qwen3-32B
#    ... or reuse the snapshot already on this account (same model, revision 9216db57, downloaded Oct 2026):
mkdir -p $SCRATCH/models && ln -s /scratch/11034/atzanakak/tmlr/hf_home/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137 $SCRATCH/models/Qwen3-32B

# 1. CPU, any time: prompts and token-length statistics, no model load (uses the model's tokenizer + chat template)
.venv/bin/python labeling/label_tasks.py --benchmark all --model $SCRATCH/models/Qwen3-32B --dry-run

# 2. fill in sbatch/label_gh_dev.slurm: -A account, the PYTHON environment (option a/b/c), MODEL_DIR if not the default
# 3. submit from the repo root (the job runs check_env.sh, the smoke test, the full run and the merge)
mkdir -p labeling/logs && sbatch labeling/sbatch/label_gh_dev.slurm
#    or interactively on a node: idev -p gh-dev -t 02:00:00 -A <account>, then
#    PYTHON=... MODEL_DIR=... bash labeling/check_env.sh
#    $PYTHON labeling/label_tasks.py --benchmark routerbench --model $MODEL_DIR --limit 50      # -> out/routerbench_limit50/
#    $PYTHON labeling/label_tasks.py --benchmark all --model $MODEL_DIR                          # -> out/<benchmark>/
#    $PYTHON labeling/merge_labels.py --benchmark all

# 4. if the job stopped on the time budget (exit code 3) or was killed: resubmit, finished shards are skipped
# 5. look at reports/<benchmark>_labels_report.md, fill `correct` in reports/<benchmark>_handcheck_sample.csv
```

Defaults of `label_tasks.py`: `--shard-size 1000`, `--max-query-chars 3000` (longer queries are cut in the middle,
60% head + 40% tail, with a `[... N characters omitted ...]` marker; the row gets `truncated=True`), `--dtype bfloat16
--tp 1 --gpu-memory-utilization 0.90 --max-model-len 4096 --max-tokens 64`, `--min-remaining-sec 300`.
A prompt that still exceeds `max_model_len - max_tokens` after the character cut is shrunk further with the model's
tokenizer until it fits (also flagged `truncated`). `--data-root` points elsewhere than `preproc/data`, `--out-dir`
elsewhere than `labeling/out`.

**Expected runtime.** ~48.5K unique prompts. The system prompt (~1.7K tokens: taxonomy + rules + glossary) is a
shared prefix, so with `enable_prefix_caching` it is computed once; the per-query part is about 70 tokens at the
median (SimpleQA, GSM8K) and 300-2,500 for code and ARC-AGI (dry-run table below), the output at most 64 tokens of
constrained JSON. On one GH200 with Qwen3-32B bf16
(the weights load in about 1.5 min from scratch, 61 GB; the earlier sglang run on this account showed that) the
labeling itself should take roughly **15-30 min for both benchmarks**, dominated by decode; guided decoding adds
some overhead per step (xgrammar compiles the schema once). The smoke test costs one extra model load. The 2-hour
gh-dev limit leaves margin; if it is hit, the time budget stops cleanly and a resubmit resumes.

## How resume works

- Rows are sorted by `query_id` and cut into shards of `--shard-size`; shard `i` is always the same rows, so a shard
  file on disk is complete and final. Each shard is written to `shard_XXXXX.parquet.tmp` and renamed (a kill leaves
  at most one `.tmp`, which is ignored).
- On start, existing shards are skipped; labels already on disk are reused for duplicate query texts in later shards.
- `metadata.json` (model path, sha256 of its `config.json`, taxonomy version, prompt hash, dtype, max_query_chars,
  shard_size, max_tokens, max_model_len, vLLM version, all args) is written once; a run into the same folder with a
  different value of any strict field is refused (vLLM version only warns). Changing the taxonomy or the prompt
  therefore means a new `--out-dir` (or deleting the folder) and a full relabel.
- With `SLURM_JOB_END_TIME` set (SLURM does), no new shard is started when less than `--min-remaining-sec` (300 s)
  remain; the script exits with code 3 and the sbatch script says to resubmit.
- `--limit N` labels a seeded random subset into `out/<benchmark>_limitN/`, never into the full-run folder, so a
  smoke test cannot mask a missing full shard.
- Identical `query` strings are sent once; the hints of the first occurrence are used.

Output columns per row (shards and `labels_full.parquet`): `query_id, theme, subtask, level1, level2, level3,
consistent, raw_output, truncated`. `consistent` is False when the model's Level 2 is not under its Level 1 (the
schema constrains each field to its enum but not the pair) or when the output did not parse (then `level1=other,
level2=other, level3=PARSE_ERROR`; the report counts both).

## How the output plugs into the handcrafted module

`merge_labels.py` writes `preproc/data/<benchmark>/task_labels.parquet` with `query_id, level1, level2, level3,
consistent`, in the row order of `queries.parquet` (= the query index). The handcrafted representation reads the
levels from per-query columns `task_level1`, `task_level2`, `task_level3` when present
(`handcrafted.DEFAULT_LEVEL_COLUMNS`), i.e. `level1 -> task_level1`, `level2 -> task_level2`, `level3 -> task_level3`.
A provided `task_level1` bypasses the Level-1 lookup table `task_taxonomy.level1_of(theme)`. `run_handcrafted.py`
reads the parquet itself by default (`--level-labels auto`, matched on `query_id`); a CSV (`index` or `query` column
plus the three `task_level*` columns) can be given instead. Level 3 is free text with high cardinality: meant for
inspection and clustering into a closed Level 3 later; as a one-hot it only appears in the `_L123` ablations.

## Taxonomy notes (v0.1.0) and the queries that motivated changes

Level 1 (11): `math, code, natural_science, medicine_biology, social_science_humanities, business_economics_law,
language_writing, general_knowledge_trivia, reasoning_commonsense, chinese_language, other`. Level 2 lists are in
`taxonomy.py` (7-10 per domain, each with an `other_<domain>` catch-all). Changes from the proposed list, after
reading 20 random queries per theme (`reports/` will hold the model's view; the sampling script was a 10-line pandas
loop, seed 0):

- **`reasoning_commonsense` replaces `reasoning_puzzles`**, with `everyday_activity_completion` and
  `pronoun_coreference_resolution` as subdomains. RouterBench is 27% HellaSwag ("[header] How to contour an oblong
  face ... A) ... B) ...", pick the continuation) and 3.5% Winogrande ("Aaron didn't know Dennis had a peanut
  allergy, so when _ made peanut chicken ..."); neither is a puzzle nor domain knowledge. ARC-AGI (400 full grid
  prompts), MMLU formal-logic / logical-fallacies, an HLE poker question and the MT-Bench "three statements,
  true/false/uncertain" items live there too.
- **`business_economics_law` split out of `social_science_humanities`.** MMLU professional-law alone is 1,534 queries
  (plus jurisprudence, international law, MMLU-Pro law 288), accounting_audit is an entire RouterBench theme, and
  MMLU-Pro has `business` and `economics` categories; a single social-science domain would have needed 15+
  subdomains. Social science keeps history, geography, philosophy, ethics (MMLU moral-scenarios is 895 queries),
  psychology (about 1,350 across MMLU and MMLU-Pro), sociology, politics, religion.
- **`language_writing` is defined by the text task, not the topic.** RouterBench's `consensus_summary` (research
  claims about ashwagandha, beta blockers, abortion and crime -> answer the question), `abstract2title` (perovskite
  solar-cell abstracts -> title) and `bias_detection` (one news sentence about Biden or Prigozhin -> biased?) would
  otherwise scatter over medicine, materials science and politics. Rule 2 of the system prompt says so explicitly;
  subdomains `summarization_title_generation`, `text_classification_analysis`, `information_extraction_formatting`
  (MT-Bench "output in JSON/CSV") were added for them.
- **`general_knowledge_trivia` has topic subdomains** (people, dates, places, media, sports, science facts,
  organizations/awards): SimpleQA is 36% of LLMRouterBench and all of it looks like "On which day, month and year
  was the DS-SAR satellite launched" or "What EP did Machine Girl release in 2016".
- **`natural_science` got `general_school_science`** for ARC-Challenge (1,470 grade-school questions that mix
  physics, biology and earth science in one item set) and `engineering_technology` (MMLU-Pro engineering 240,
  HLE engineering 64, MMLU electrical engineering: heat-transfer coefficients, boundary layers, directional heating).
  Biology stays in `medicine_biology` as proposed (GPQA biology, MMLU college biology are there).
- **`math` subdomains follow the data's spread**: GSM8K (7,450) is `arithmetic_word_problem`; AIME / LiveMathBench are
  mostly geometry, number theory and combinatorics; HLE math (976) is research-level (Alon-Tarsi numbers, p-adic
  metrics, posets), hence `abstract_algebra_topology_advanced`; MMLU statistics / MMLU-Pro math give
  `probability_statistics`. `competition_proof` was dropped: competition problems are labeled by topic instead.
- **`code` got `machine_learning_ai` and `computer_science_theory_security`**: ArenaHard coding is heavy on torch
  ("gather a dict on multiple gpus", NT-Xent loss), MMLU has machine-learning and computer-security subjects,
  HLE CS/AI asks about blockchain liveness and busy-beaver-style questions, none of which is "write code".
- **`chinese_language` subdomains match the 15 RouterBench Chinese sets**: `chinese_zodiac` is half of that theme
  (394 rows of the form "2021, ox, 90s"), then character/lantern riddles, 诗经/楚辞/唐诗/宋词 identification,
  idioms/homonyms, famous novels, hard translations. `chinese-remainder-theorem` (14 rows) is math; the prompt tells
  the model to use `chinese_language` only for tasks about the language or culture, so it may land in `math`.
- **Hints are declared fallible in the prompt**: ArenaHard's `math` subcategory contains "修改代码去bug" MATLAB
  debugging, a thermodynamics cycle and a two-sample t-test; MMLU `miscellaneous` is 783 rows of anything.
- ArenaHard also has Russian, Japanese and Chinese prompts (creative writing, code). Rule 7: label the task, not the
  language; `chinese_language` is for tasks about Chinese.

## Dry-run prompt lengths (CPU, Qwen3-32B tokenizer and chat template, thinking disabled)

Full output in `reports/dry_run_prompt_stats.txt` (three example prompts per benchmark, per-theme medians).

System prompt: 6,730 chars = **1,522 tokens**, shared by every call (prefix-cached). Prompt = system + hints + query:

| benchmark | rows | unique texts | cut at 3000 chars | mean | median | p90 | p99 | max | over 4032 tokens |
|---|---|---|---|---|---|---|---|---|---|
| llmrouterbench | 12,068 | 12,066 | 362 | 1,739 | 1,591 | 2,023 | 4,051 | 5,707 | 167 |
| routerbench | 36,478 | 36,478 | 22 | 1,689 | 1,656 | 1,825 | 1,967 | 2,316 | 0 |

Per theme (median tokens): ARC-AGI 3,980 (max 4,080; grids tokenize at about one token per character, so the
3000-char cut still leaves ~2,500 query tokens), LiveCodeBench 1,985, abstract2title 1,814, HellaSwag 1,795, HLE
1,691 (max 5,707, dense LaTeX), everything else 1,560-1,730. Total ~82.6M prompt tokens, of which ~73.8M are the
cached system prompt: about **8.8M unique tokens to prefill** plus at most 64 output tokens per query.

**The 167 over-limit prompts** (ARC-AGI and a few HLE) would be rejected by vLLM at `--max-model-len 4096`
(4096 - 64 output tokens = 4,032). Two safeguards: `label_tasks.py` measures each prompt with the model's tokenizer
and shrinks the query by 20% steps until it fits (the row is flagged `truncated`), and the sbatch script runs with
`--max-model-len 8192` so that no query is cut below 3000 chars (KV cache for 8K context is small next to the 61 GB
of weights). Both are recorded in `metadata.json`.

## Questions to settle with the team

1. **Final taxonomy.** Are 11 domains right for RQ1a, in particular `reasoning_commonsense` (puzzles + HellaSwag +
   Winogrande together) and `business_economics_law` as its own domain? Any change bumps `taxonomy.VERSION` and
   means a full relabel (~30 min of GPU).
2. **Force Level 1 from the theme for single-domain datasets?** AIME, LiveMathBench, GSM8K -> math; LiveCodeBench,
   MBPP -> code; HellaSwag, Winogrande, ARC-AGI -> reasoning_commonsense; SimpleQA -> trivia. The model will mostly
   agree, but forcing removes the noise (and the ability to detect that, say, an ArenaHard "math" prompt is code).
   Proposal: keep the model's labels in `task_labels.parquet`, report the theme x level1 crosstab, and decide a
   `level1_forced` column after seeing the disagreement rate.
3. **Whose loader exposes the columns.** Option 1: `preproc/data.py` merges `task_labels.parquet` on `query_id` and
   `Data` gains `task_level1/2/3` (Arman). Option 2: my module reads the parquet itself. Also where the labels file
   lives: next to `queries.parquet` in `preproc/data/<benchmark>/` (current default, Arman's folder) or under
   `labeling/out/`.
4. **Level 3.** Keep as free text for inspection, or cluster into a closed list (embedding + k-means on the ~48K
   phrases) for a `task_type_L3` one-hot?
5. **Hand-check.** Done once by Claude (`reports/handcheck_summary.md`): Level 1 94.0% / 92.5%, Levels 1+2 82.5% / 88.0%
   (LLMRouterBench / RouterBench). A human spot-check of the `0` rows is still worth 20 minutes. Which accuracy do we
   require before using Level 2, and do we bundle the v0.2.0 prompt fixes listed there?

## Before `sbatch`

- `#SBATCH -A`: your allocation (`sacctmgr show assoc user=$USER format=account` lists `bcs25073`, `bcs25105`,
  `mcb26038`).
- `PYTHON` in `sbatch/label_gh_dev.slurm`: option (a) apptainer vLLM image (pull on a login node), (b) your own venv
  with aarch64 wheels, or (c) an existing env on this account:
  `/scratch/11034/atzanakak/biomni_vista/envs/biotaskbench/bin/python` (vLLM 0.27.1, torch 2.13 cu130, python 3.12,
  aarch64; the GH200 driver reports CUDA 13.1). Both existing envs have been checked for the API the script uses
  (`LLM.chat(..., chat_template_kwargs=...)`, `StructuredOutputsParams(json=...)`); they have not been run here.
- `MODEL_DIR`: `$SCRATCH/models/Qwen3-32B` by default; download or symlink (above).
- The sbatch script passes `--max-model-len 8192` (script default 4096) because of the 167 ARC-AGI/HLE prompts above
  4,032 tokens; keep it unless memory is tight (then the shrink-to-fit safeguard takes over).
- `.venv` on the login node got `pyarrow`, `jsonschema`, `tokenizers`, `transformers`, `jinja2` for the CPU side
  (tests, dry run, merge); no torch, no vLLM.
