"""Closed task-type taxonomy for the offline labeling of every query (domain -> subdomain -> free-text task).

Level 1 (domain) and Level 2 (subdomain) are fixed lists below: the LLM must pick from them (enforced by guided
decoding in label_tasks.py). Level 3 is a free 2-5 word phrase for inspection and later clustering only.

The lists were adjusted after reading ~20 random queries per theme of both benchmarks (labeling/README.md,
"Taxonomy notes"). Bump VERSION whenever a name in DOMAINS changes: label_tasks.py refuses to resume a run whose
metadata was written with another version, and the labels on disk carry it.
"""
from __future__ import annotations

VERSION = "0.1.0"

# Level 1 -> ordered list of Level 2 subdomains. Every domain ends with an `other_<domain>` catch-all, so a query
# that clearly belongs to the domain but to none of its subdomains still gets a consistent pair.
DOMAINS: dict[str, list[str]] = {
    "math": [
        "arithmetic_word_problem",            # GSM8K-style multi-step arithmetic in a story
        "algebra_precalculus",                # equations, functions, sequences, logarithms, complex numbers
        "number_theory",                      # divisibility, remainders, primes, digits
        "geometry_trigonometry",              # plane/solid geometry, coordinates, trig identities
        "combinatorics_discrete_graph_theory",  # counting, arrangements, graphs, posets, games on finite structures
        "probability_statistics",             # probability, distributions, hypothesis tests, descriptive statistics
        "calculus_analysis",                  # limits, derivatives, integrals, series, ODEs, real/complex analysis
        "linear_algebra",                     # matrices, vectors, eigenvalues, linear systems
        "abstract_algebra_topology_advanced",  # groups/rings/fields, topology, algebraic geometry, research-level math
        "other_math",
    ],
    "code": [
        "algorithms_data_structures",         # competitive-programming problems with input/output spec
        "implementation_from_spec",           # "write a function that ..." utility code
        "debugging_fixing",                   # find/fix the bug, why does this fail/error
        "code_explanation_review",            # explain, review, refactor, optimize existing code
        "sql_databases",                      # SQL queries, schema design, database questions
        "web_frontend",                       # HTML/CSS/JS, UI, browser/web app code
        "systems_scripting_devops",           # shell, OS, networking, build/deploy, concurrency, low-level
        "machine_learning_ai",                # ML/DL code and concepts (torch, training, models, AI theory)
        "computer_science_theory_security",   # complexity, automata, architecture, security, distributed systems
        "other_code",
    ],
    "natural_science": [
        "classical_physics",                  # mechanics, E&M, thermodynamics, waves, optics
        "modern_physics",                     # quantum, relativity, particle, nuclear, condensed matter, cosmology
        "general_physical_chemistry",         # stoichiometry, equilibrium, kinetics, bonding, inorganic
        "organic_chemistry",                  # reactions, synthesis, mechanisms, spectroscopy of organics
        "astronomy_astrophysics",             # stars, planets, exoplanets, observational astronomy
        "earth_environmental_science",        # geology, weather, climate, oceans, environment
        "engineering_technology",             # electrical, mechanical, heat transfer, materials, applied engineering
        "general_school_science",             # grade-school science questions mixing fields (ARC-Challenge style)
        "other_natural_science",
    ],
    "medicine_biology": [
        "clinical_medicine_diagnosis",        # patient vignettes, diagnosis, clinical management
        "pharmacology_treatment",             # drugs, therapies, mechanisms of action, dosing
        "anatomy_physiology",                 # structure and function of the body
        "genetics_molecular_cell_biology",    # DNA/RNA/protein, genetics, cell biology, biochemistry
        "microbiology_immunology_virology",   # pathogens, immune system, infectious disease
        "nutrition_public_health",            # diet, epidemiology, health policy, aging, sexual health
        "ecology_evolution_organismal_biology",  # ecosystems, evolution, plants/animals, organism-level biology
        "other_medicine_biology",
    ],
    "social_science_humanities": [
        "history",
        "geography_demography",
        "philosophy",                         # epistemology, metaphysics, philosophers' positions
        "ethics_moral_reasoning",             # moral dilemmas, applied ethics, moral scenarios
        "psychology",                         # cognition, development, clinical/abnormal, social psychology
        "sociology_anthropology",             # society, culture, prehistory/archaeology, communication
        "politics_international_relations",   # government, policy, foreign policy, security studies
        "religion_mythology",
        "other_social_science_humanities",
    ],
    "business_economics_law": [
        "law_legal_reasoning",                # statutes, cases, legal doctrine, jurisprudence, international law
        "accounting_auditing",                # financial statements, bookkeeping, audit procedures
        "finance_investment",                 # valuation, interest, portfolios, corporate finance
        "economics",                          # micro, macro, econometrics, economic reasoning
        "management_marketing",               # management, marketing, organizational behavior, public relations
        "business_ethics_professional_conduct",
        "other_business_economics_law",
    ],
    "language_writing": [
        "creative_writing",                   # stories, poems, scripts, fiction in any language
        "professional_writing",               # emails, letters, reports, outlines, lesson plans, blog posts
        "summarization_title_generation",     # summarize a text / claims, write a title or headline
        "text_classification_analysis",       # bias, sentiment, tone, stance of a given text
        "information_extraction_formatting",  # extract fields from text, convert to JSON/CSV/table
        "translation_multilingual",           # translate between languages, language-learning questions
        "grammar_editing_rewriting",          # fix grammar, rephrase, change style or register
        "reading_comprehension_qa",           # answer questions about a given passage
        "roleplay_conversation",              # act as a persona, chit-chat, advice in a role
        "other_language_writing",
    ],
    "general_knowledge_trivia": [
        "people_biography",                   # who did/was, birth dates, roles of named people
        "history_events_dates",               # when did X happen, what happened in year Y
        "geography_places",                   # where, place names, buildings, landmarks
        "entertainment_media_arts",           # film, TV, music, games, books, visual arts
        "sports",
        "science_technology_facts",           # named facts about science, tech, discoveries, products
        "politics_organizations_awards",      # elections, institutions, prizes, companies
        "other_trivia",
    ],
    "reasoning_commonsense": [
        "abstract_pattern_induction",         # ARC-AGI grid transformations, sequence/pattern puzzles
        "formal_logic_deduction",             # propositional/predicate logic, syllogisms, truth tables
        "logical_fallacies_argument_analysis",  # identify fallacies, evaluate arguments
        "riddles_brain_teasers",              # riddles, lateral thinking, word puzzles
        "everyday_activity_completion",       # pick the most plausible continuation of a scene (HellaSwag style)
        "pronoun_coreference_resolution",     # fill the blank / who does "_" refer to (Winogrande style)
        "physical_social_commonsense",        # naive physics, social norms, everyday causality
        "games_strategy_planning",            # game positions, optimal play, scheduling/planning puzzles
        "other_reasoning",
    ],
    "chinese_language": [
        "character_riddles",                  # 字谜, 灯谜
        "classical_poetry",                   # 诗经, 楚辞, 唐诗, 宋词, poem identification/completion
        "classical_literature_novels",        # 四大名著, 古籍, dynasties of masterpieces
        "idioms_homonyms_vocabulary",         # 成语, 谐音, word meanings
        "zodiac_calendar_culture",            # zodiac/生肖, traditional calendar, customs
        "translation_chinese",                # Chinese <-> other language translation
        "other_chinese_language",
    ],
    "other": [
        "mixed_multi_domain",                 # genuinely spans several domains with no primary one
        "unclear_insufficient_context",       # cannot tell what is asked (fragment, ids only, garbled)
        "other",
    ],
}

# One line per domain for the model (what belongs where; the boundaries that matter in this data).
DOMAIN_DESCRIPTIONS: dict[str, str] = {
    "math": "mathematical problems of any level, from arithmetic word problems to research-level mathematics",
    "code": "writing, fixing, explaining or reasoning about programs, algorithms, software and computer science",
    "natural_science": "physics, chemistry, astronomy, earth science and engineering (non-living systems)",
    "medicine_biology": "medicine, health and all of biology (living systems)",
    "social_science_humanities": "history, geography, philosophy, ethics, psychology, sociology, politics, religion",
    "business_economics_law": "law, accounting, finance, economics, management, marketing, business ethics",
    "language_writing": "tasks about producing or transforming text: writing, summarizing, classifying, extracting, "
                        "translating, editing, role-play; label by the TEXT TASK, not by the topic of the text",
    "general_knowledge_trivia": "short factual recall questions (who/when/where/how many) with a single named answer",
    "reasoning_commonsense": "puzzles and reasoning that need no specialist knowledge: pattern induction, formal "
                             "logic, riddles, commonsense continuation, coreference, games",
    "chinese_language": "tasks about the Chinese language and classical Chinese culture (riddles, poetry, idioms, "
                        "zodiac), written in Chinese or about Chinese text",
    "other": "only when nothing above fits",
}

# Short glossary of the source datasets, given to the model as context for the hints (theme = source dataset).
DATASET_GLOSSARY: dict[str, str] = {
    # LLMRouterBench
    "aime": "AIME competition math problems",
    "arc-agi": "ARC-AGI abstract grid-transformation puzzles (the full prompt with training pairs)",
    "arenahard": "ArenaHard: real user prompts to chatbots, subcategories coding / math / creative_writing (noisy)",
    "gpqa": "GPQA: graduate-level physics, chemistry and biology questions",
    "hle": "Humanity's Last Exam: expert questions from every field, with a category hint",
    "livecodebench": "LiveCodeBench: competitive programming problems",
    "livemathbench": "LiveMathBench: recent math competition / exam problems",
    "mmlupro": "MMLU-Pro: multiple-choice exam questions, with a subject hint",
    "simpleqa": "SimpleQA: short factual trivia questions",
    # RouterBench
    "mmlu": "MMLU: multiple-choice exam questions, subject in the hint (mmlu-<subject>)",
    "hellaswag": "HellaSwag: choose the most plausible continuation of an everyday scene",
    "grade-school-math": "GSM8K: grade-school arithmetic word problems",
    "arc-challenge": "ARC-Challenge: grade-school science multiple choice",
    "winogrande": "Winogrande: fill the blank with the right entity (pronoun/coreference)",
    "chinese": "Chinese-language tasks: character riddles, classical poetry, idioms, zodiac, translation",
    "mbpp": "MBPP: write a short Python function from a one-sentence spec",
    "consensus_summary": "summarize several research claims into an answer to a question",
    "bias_detection": "decide whether a news sentence is biased",
    "abstract2title": "write a title for a scientific abstract",
    "mtbench": "MT-Bench: open-ended chatbot prompts (writing, roleplay, reasoning, math, coding, extraction)",
    "accounting_audit": "auditing / accounting multiple-choice questions",
}

LEVEL1: list[str] = list(DOMAINS)
LEVEL2_ALL: list[str] = [s for subs in DOMAINS.values() for s in subs]
LEVEL2_TO_LEVEL1: dict[str, str] = {s: d for d, subs in DOMAINS.items() for s in subs}
LEVEL3_MAX_CHARS = 60

assert len(LEVEL2_ALL) == len(set(LEVEL2_ALL)), "level-2 names must be unique across domains"
assert len(LEVEL1) <= 12, "keep the domain list small"
assert all(1 <= len(v) <= 10 for v in DOMAINS.values()), "4-10 subdomains per domain"


def level1_of(level2: str) -> str | None:
    """The domain a subdomain belongs to, None for an unknown name."""
    return LEVEL2_TO_LEVEL1.get(level2)


def is_consistent(level1: str, level2: str) -> bool:
    """True when `level2` is one of `level1`'s subdomains."""
    return level1 in DOMAINS and level2 in DOMAINS[level1]


def json_schema() -> dict:
    """JSON schema of one label, for guided decoding. level2 is the union of all subdomains (consistency with
    level1 is checked afterwards and recorded in the `consistent` column)."""
    return {
        "type": "object",
        "properties": {
            "level1": {"type": "string", "enum": LEVEL1},
            "level2": {"type": "string", "enum": LEVEL2_ALL},
            "level3": {"type": "string", "minLength": 1, "maxLength": LEVEL3_MAX_CHARS},
        },
        "required": ["level1", "level2", "level3"],
        "additionalProperties": False,
    }


def taxonomy_text() -> str:
    """The taxonomy as it appears in the system prompt: one block per domain with its description and subdomains."""
    lines = []
    for d, subs in DOMAINS.items():
        lines.append(f"- {d}: {DOMAIN_DESCRIPTIONS[d]}")
        lines.append("    level2: " + ", ".join(subs))
    return "\n".join(lines)


def glossary_text() -> str:
    return "\n".join(f"- {k}: {v}" for k, v in DATASET_GLOSSARY.items())


def summary() -> str:
    """Human-readable counts, for logs and the README."""
    n2 = sum(len(v) for v in DOMAINS.values())
    return f"taxonomy v{VERSION}: {len(LEVEL1)} domains, {n2} subdomains"


if __name__ == "__main__":
    print(summary())
    print(taxonomy_text())
