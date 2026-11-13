# Hand-check of the task labels (taxonomy v0.1.0, Qwen3-32B, job 1134736)

Checked by Claude on 2026-11-13 on the two 200-row stratified samples (`*_handcheck_sample.csv`, column `correct`:
`1` = level 1 and level 2 right, `L1` = level 1 right / level 2 wrong, `0` = level 1 wrong; `note` says what it
should have been). This is a model's judgment, not a human one: treat it as a first pass and spot-check the `0` rows.

| benchmark | level 1 correct | level 1 + level 2 correct |
|---|---|---|
| llmrouterbench | 188 / 200 = **94.0%** | 165 / 200 = **82.5%** |
| routerbench | 185 / 200 = **92.5%** | 176 / 200 = **88.0%** |

The samples are stratified by level 1 (at least 5 rows per domain), so rare domains and their errors are
over-represented relative to the full data; accuracy on the whole set should be a bit higher.

## Where level 1 goes wrong (27 rows of 400)

- **Psychology under `medicine_biology`** (3 of 15 RouterBench errors; 397 rows in the full data, the largest
  inconsistent pair). The model pairs `medicine_biology` with the subdomain `psychology`, which the taxonomy puts
  under `social_science_humanities`. Clinical psychology arguably is medicine; the fix is a decision, not a bug:
  either accept both (treat `psychology` as consistent with either parent) or add a sentence to the prompt.
- **HellaSwag "How to diagnose/treat X" items labeled `medicine_biology`** (3 of 15; 14 rows in the full data).
  The task is activity completion; rule 2 of the prompt should mention multiple-choice continuation explicitly.
- **`consensus_summary` labeled `other/mixed_multi_domain`** (2 of 15; 27 rows in the full data). Same fix: name
  "summarize several claims into an answer" in rule 2.
- **Economics questions labeled `math`, `medicine_biology` or `natural_science`** (4 of 12 LLMRouterBench errors:
  elasticity, marginal utility, PPF, eco-efficiency). The queries are computational; the model keys on the
  arithmetic. A prompt line "economics and finance calculations go to business_economics_law" would fix most.
- **ARC-Challenge science items labeled `reasoning_commonsense`** (2 of 15): "which sentence could not explain why
  the swimmer was faster", "which behavior did a bear learn". Boundary cases.
- One-offs: a formal-logic translation and a logical-fallacy item labeled philosophy / language_writing (both
  belong to `reasoning_commonsense`), an Early Modern English poem and a Thai poem labeled `chinese_language`
  (rule 7 needs "only when the task is about Chinese"), a ballet-terminology question labeled `other`.

## Where level 2 goes wrong with level 1 right (32 rows of 400)

Mostly adjacent subdomains: `general_physical_chemistry` for organic synthesis (3), `anatomy_physiology` for
cell/molecular biology (2), `nutrition_public_health` or `anatomy_physiology` for immunology (3),
`abstract_algebra_topology_advanced` for HLE problems that are really combinatorics or analysis (3),
`entertainment_media_arts` or `science_technology_facts` for sports trivia (3), `philosophy` for ethics (2),
`algorithms_data_structures` for an MBPP one-liner (1). None of these would change a Level-1 analysis; for Level 2
they are the noise floor to expect (about 8-12% of rows).

## Recommendation

Keep v0.1.0 for the first RQ1a runs (Level 1 is 92-94% clean, the errors are concentrated in known, small groups).
For a v0.2.0 relabel (25 min of GPU) bundle: the psychology decision, three prompt sentences (continuation items,
claim summaries, economics calculations), and the rule-7 wording. Do not relabel for anything smaller.
