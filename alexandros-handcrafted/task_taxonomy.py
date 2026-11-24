"""Level-1 domain of a query from the raw task-type label Arman's loader will provide (most likely the dataset name).

The proposal (Figure 1) frames task type as a hierarchy: Level 1 domain (math, code, science, ...), Level 2 subdomain
(linear algebra, algorithms, biology, ...), Level 3 specific task (matrix multiplication, shortest path, ...).
Level 1 is a lookup in the table below; Levels 2 and 3 come from an offline classification step (not here) as extra
per-query columns in the data. If the loader already provides a Level 1 column, this table is bypassed (see
`HandcraftedEmbedding` in handcrafted.py).

Coverage: the 21 LLMRouterBench datasets (github.com/meijamke/LLMRouterBench, README tables, 2026) and the 8 RouterBench
datasets (Hu et al. 2024, §4.2), plus the MMLU subjects and MMLU-Pro categories so that per-subject labels such as
"mmlu-astronomy" or "mmlu_pro_physics" resolve to a domain. Entries whose domain is a judgment call carry a TODO.
Unknown labels fall back to `FALLBACK` ("other"); `report_unknown` lists them so the table can be extended.

Matching is forgiving: labels are lower-cased and stripped of separators, so "MMLU-Pro", "mmlu_pro" and "MMLU Pro"
are the same key. Suffixes such as ".val.5", "_test", "-v0" are ignored, and a subject after the dataset name
("mmlu-astronomy.val.5") is looked up in the dataset's subject map.
"""
from __future__ import annotations

import re
import warnings
from collections import Counter
from dataclasses import dataclass, field

FALLBACK = "other"

# Level-1 domains used in this project (a fixed, documented set, so the one-hot has a known column order).
DOMAINS = ["math", "code", "logic", "science", "engineering", "medicine", "law", "business", "finance", "humanities",
           "social_science", "knowledge", "commonsense", "affective", "instruction_following", "conversation",
           "tool_use", "rag", FALLBACK]


@dataclass(frozen=True)
class Entry:
    level1: str                       # our Level-1 domain (one of DOMAINS)
    authors_category: str             # the category the benchmark authors assign (kept for reference)
    benchmark: str                    # "llmrouterbench", "routerbench" or both
    aliases: tuple[str, ...] = ()     # other spellings / identifiers
    note: str = ""
    todo: str = ""                    # non-empty when the domain is a judgment call to confirm
    subjects: dict | None = field(default=None, hash=False)  # subject -> level1, for per-subject labels (MMLU, MMLU-Pro)


# ---------------------------------------------------------------- MMLU subjects (57) and MMLU-Pro categories (14)

MMLU_SUBJECT_DOMAIN = {
    # STEM
    "abstract_algebra": "math", "college_mathematics": "math", "elementary_mathematics": "math",
    "high_school_mathematics": "math", "high_school_statistics": "math",
    "astronomy": "science", "college_biology": "science", "college_chemistry": "science", "college_physics": "science",
    "conceptual_physics": "science", "high_school_biology": "science", "high_school_chemistry": "science",
    "high_school_physics": "science",
    "college_computer_science": "code", "computer_security": "code", "high_school_computer_science": "code",
    "machine_learning": "code",
    "electrical_engineering": "engineering",
    # medicine / health
    "anatomy": "medicine", "clinical_knowledge": "medicine", "college_medicine": "medicine", "human_aging": "medicine",
    "medical_genetics": "medicine", "nutrition": "medicine", "professional_medicine": "medicine", "virology": "medicine",
    "human_sexuality": "medicine",
    # law
    "international_law": "law", "jurisprudence": "law", "professional_law": "law",
    # business / economics
    "business_ethics": "business", "management": "business", "marketing": "business", "professional_accounting": "business",
    "econometrics": "business", "high_school_macroeconomics": "business", "high_school_microeconomics": "business",
    # humanities
    "formal_logic": "logic", "logical_fallacies": "logic",
    "high_school_european_history": "humanities", "high_school_us_history": "humanities", "high_school_world_history": "humanities",
    "prehistory": "humanities", "philosophy": "humanities", "moral_disputes": "humanities", "moral_scenarios": "humanities",
    "world_religions": "humanities",
    # social sciences
    "high_school_geography": "social_science", "high_school_government_and_politics": "social_science",
    "high_school_psychology": "social_science", "professional_psychology": "social_science", "sociology": "social_science",
    "us_foreign_policy": "social_science", "public_relations": "social_science", "security_studies": "social_science",
    "global_facts": "knowledge", "miscellaneous": "knowledge",
}

MMLU_PRO_CATEGORY_DOMAIN = {
    "math": "math", "physics": "science", "chemistry": "science", "biology": "science", "computer_science": "code",
    "engineering": "engineering", "health": "medicine", "law": "law", "business": "business", "economics": "business",
    "psychology": "social_science", "philosophy": "humanities", "history": "humanities", "other": "knowledge",
}

# ---------------------------------------------------------------- the datasets

TAXONOMY: dict[str, Entry] = {
    # ---- LLMRouterBench (21). Names as in the README tables; aliases include the README abbreviations and the
    #      lowercase folder names seen in results/bench/<dataset>/.
    "AIME": Entry("math", "Mathematics", "llmrouterbench", ("aime", "aime24", "aime25", "aime2024", "aime2025")),
    "MATH500": Entry("math", "Mathematics", "llmrouterbench", ("math_500", "math-500", "m500", "math")),
    "MATHBench": Entry("math", "Mathematics", "llmrouterbench", ("mathbench", "mben")),
    "LiveMathBench": Entry("math", "Mathematics", "llmrouterbench", ("livemathbench", "lmb")),
    "HumanEval": Entry("code", "Code", "llmrouterbench", ("humaneval", "he", "human_eval")),
    "MBPP": Entry("code", "Code", "llmrouterbench, routerbench", ("mbpp",)),
    "LiveCodeBench": Entry("code", "Code", "llmrouterbench", ("livecodebench", "lcb")),
    "SWE-Bench": Entry("code", "Code", "llmrouterbench", ("swebench", "swe", "swe_bench", "swe-bench-verified", "swebenchverified"),
                       note="resolving real GitHub issues; agentic. Level-2 label could separate it from function synthesis"),
    "BBH": Entry("logic", "Logic", "llmrouterbench", ("bbh", "big_bench_hard", "bigbenchhard"),
                 todo="BBH mixes 27 sub-tasks (some are language or math); 'logic' follows the authors. A per-sub-task label "
                      "(e.g. bbh-date_understanding) would deserve its own subject map"),
    "KORBench": Entry("logic", "Logic", "llmrouterbench", ("korbench", "kor")),
    "Knights & Knaves": Entry("logic", "Logic", "llmrouterbench", ("knights_and_knaves", "knightsandknaves", "knights-knaves", "kk", "k&k")),
    "MMLU-Pro": Entry("knowledge", "Knowledge", "llmrouterbench", ("mmlu_pro", "mmlupro", "mp"), subjects=MMLU_PRO_CATEGORY_DOMAIN,
                      todo="mixed subjects: 'knowledge' only when the label has no category suffix; with a suffix "
                           "(mmlu_pro_physics) the MMLU-Pro category map decides. Ask Arman whether the category is kept"),
    "GPQA": Entry("science", "Knowledge", "llmrouterbench", ("gpqa", "gpqa_diamond", "gpqa-diamond"),
                  todo="authors say Knowledge; graduate-level physics/chemistry/biology questions, so 'science' here. Confirm"),
    "FinQA": Entry("finance", "Knowledge", "llmrouterbench", ("finqa", "fqa"),
                   todo="numerical reasoning over financial tables: 'finance', but it is also math-like. Confirm"),
    "MedQA": Entry("medicine", "Knowledge", "llmrouterbench", ("medqa", "mqa", "medqa_usmle")),
    "HLE": Entry("knowledge", "Knowledge", "llmrouterbench", ("hle", "humanitys_last_exam", "humanityslastexam"),
                 todo="expert questions across all fields; 'knowledge' is a catch-all. If HLE keeps its subject field, map it"),
    "SimpleQA": Entry("knowledge", "Knowledge", "llmrouterbench", ("simpleqa", "sqa", "simple_qa")),
    "EmoryNLP": Entry("affective", "Affective", "llmrouterbench", ("emorynlp", "emory")),
    "MELD": Entry("affective", "Affective", "llmrouterbench", ("meld",)),
    "ArenaHard": Entry("instruction_following", "Instruction Following", "llmrouterbench", ("arenahard", "arena_hard", "ahard", "arena-hard-auto"),
                       todo="open-ended chat prompts judged by an LLM; could be merged with 'conversation' (MT-Bench). Decide"),
    "τ²-Bench": Entry("tool_use", "Tool Use", "llmrouterbench", ("tau2bench", "tau2", "tau2_bench", "tau-bench", "taubench", "τ2bench", "τ²bench")),
    # ---- RouterBench (8). Names as in Hu et al. 2024 §4.2; aliases include the likely eval_name prefixes.
    "HellaSwag": Entry("commonsense", "Commonsense Reasoning", "routerbench", ("hellaswag",)),
    "Winogrande": Entry("commonsense", "Commonsense Reasoning", "routerbench", ("winogrande",)),
    "ARC Challenge": Entry("science", "Commonsense Reasoning", "routerbench", ("arc_challenge", "arcchallenge", "arc-challenge", "arc", "arc_c"),
                           todo="authors file it under Commonsense Reasoning; the questions are grade-school science, "
                                "so 'science' here. Confirm"),
    "MMLU": Entry("knowledge", "Knowledge-based Language Understanding", "routerbench", ("mmlu",), subjects=MMLU_SUBJECT_DOMAIN,
                  todo="RouterBench stores MMLU per subject (ids like mmlu-astronomy.val.5): with the subject the MMLU map "
                       "decides, without it 'knowledge'. Confirm the exact id format with Arman"),
    "MT-Bench": Entry("conversation", "Conversation", "routerbench", ("mtbench", "mt_bench", "mt-bench")),
    "GSM8K": Entry("math", "Math", "routerbench", ("gsm8k", "gsm-8k", "gsm_8k")),
    "RAG": Entry("rag", "RAG", "routerbench", ("rag", "rag_dataset", "martian_rag"),
                 todo="the RouterBench RAG set has no formal name in the paper (800 client queries on sports, history, media, "
                      "politics). The identifier string is unknown; ask Arman"),
    # ---- the theme strings as they appear in Arman's build (preproc/data/<benchmark>/queries.parquet)
    "ARC-AGI": Entry("logic", "Reasoning", "llmrouterbench", ("arc-agi", "arcagi", "arc_agi"),
                     note="abstraction puzzles on colored grids; not ARC Challenge (grade-school science)"),
    "grade-school-math": Entry("math", "Math", "routerbench", ("grade_school_math", "gradeschoolmath"), note="RouterBench's name for GSM8K"),
    "chinese": Entry("humanities", "Chinese language and culture", "routerbench", (),
                     note="15 RouterBench Chinese sets (zodiac, riddles, classical poetry, idioms); 14 chinese-remainder-theorem rows are math"),
    "consensus_summary": Entry("knowledge", "Summarization", "routerbench", ("consensussummary",), note="answer a question from several research claims"),
    "bias_detection": Entry("knowledge", "Classification", "routerbench", ("biasdetection",), note="is this news sentence biased"),
    "abstract2title": Entry("knowledge", "Summarization", "routerbench", ("abstracttotitle",), note="title for a paper abstract"),
    "accounting_audit": Entry("business", "Accounting", "routerbench", ("accountingaudit",)),
    # ---- plain domain words, in case the loader already gives a coarse label (then it maps to itself)
    **{d: Entry(d, d, "any", (), note="a Level-1 domain name used directly as the label") for d in DOMAINS},
    "biology": Entry("science", "science", "any"), "physics": Entry("science", "science", "any"),
    "chemistry": Entry("science", "science", "any"), "coding": Entry("code", "code", "any"),
    "programming": Entry("code", "code", "any"), "mathematics": Entry("math", "math", "any"),
    "history": Entry("humanities", "humanities", "any"), "reasoning": Entry("logic", "logic", "any"),
    "health": Entry("medicine", "medicine", "any"), "economics": Entry("business", "business", "any"),
}

# ---------------------------------------------------------------- lookup

_SEP = re.compile(r"[\s\-_./:,()\[\]]+")
_SPLIT_TOKENS = {"val", "dev", "test", "train", "validation", "eval", "diamond", "verified", "auto", "v0", "v1", "v2"}


def normalize(label) -> str:
    """Lower-case and drop separators: 'MMLU-Pro' -> 'mmlupro'."""
    return re.sub(r"[^0-9a-zͰ-Ͽ²]", "", str(label).lower().replace("&", "and").replace("²", "2"))


def _tokens(label) -> list[str]:
    toks = [t for t in _SEP.split(str(label).strip().lower()) if t]
    return [t for t in toks if t not in _SPLIT_TOKENS and not t.isdigit()] or toks


_INDEX: dict[str, Entry] = {}
for _name, _entry in TAXONOMY.items():
    for _key in (_name, *_entry.aliases):
        _INDEX.setdefault(normalize(_key), _entry)


def lookup(label) -> tuple[Entry | None, str | None]:
    """(entry, subject) for a raw label: exact (normalized) match first, then the longest prefix of the label's tokens
    that names a dataset, with the remaining tokens as the subject. (None, None) if nothing matches."""
    if label is None:
        return None, None
    key = normalize(label)
    if key in _INDEX:
        return _INDEX[key], None
    toks = _tokens(label)
    for i in range(len(toks), 0, -1):
        head = normalize("".join(toks[:i]))
        if head in _INDEX:
            return _INDEX[head], "_".join(toks[i:]) or None
    return None, None


def level1_of(label) -> str:
    """Level-1 domain of a raw task-type label; FALLBACK when unknown."""
    entry, subject = lookup(label)
    if entry is None:
        return FALLBACK
    if subject and entry.subjects:
        key = normalize(subject)
        for subj, dom in entry.subjects.items():
            if normalize(subj) == key:
                return dom
        for subj, dom in entry.subjects.items():  # the subject may carry extra tokens ('astronomy_val')
            if normalize(subj) in key or key in normalize(subj):
                return dom
    return entry.level1


def map_labels(labels, warn=True) -> list[str]:
    """Level-1 domain for every raw label; warns once with the unknown labels (mapped to FALLBACK)."""
    out, unknown = [], Counter()
    for lab in labels:
        d = level1_of(lab)
        if d == FALLBACK and lookup(lab)[0] is None:
            unknown[str(lab)] += 1
        out.append(d)
    if unknown and warn:
        warnings.warn(f"{sum(unknown.values())} queries with {len(unknown)} task-type labels not in the taxonomy, mapped to "
                      f"'{FALLBACK}': {dict(unknown.most_common(10))}{' ...' if len(unknown) > 10 else ''}")
    return out


def report(labels) -> str:
    """Human-readable coverage table for the distinct raw labels in `labels` (for --dry-run)."""
    counts = Counter(str(l) for l in labels)
    lines = [f"{'raw label':40s} {'n':>7s}  level1           via"]
    for lab, n in counts.most_common():
        entry, subject = lookup(lab)
        via = "UNKNOWN -> other" if entry is None else (f"{entry.authors_category}" + (f", subject '{subject}'" if subject else ""))
        lines.append(f"{lab[:40]:40s} {n:7d}  {level1_of(lab):16s} {via}")
    return "\n".join(lines)


def todos() -> list[str]:
    return [f"{name}: {e.todo}" for name, e in TAXONOMY.items() if e.todo]
