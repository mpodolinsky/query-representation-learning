"""Data and timeline replay (Arman's component): load the processed benchmarks, release epochs, unseen-model
instances, splits and probes. `build.py` writes the files this module reads; see README.md for the schema."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
BENCHMARKS = ("llmrouterbench", "routerbench")
SPLIT_SEEDS = (0, 1, 2)
SPLIT_FRACTIONS = (0.7, 0.1, 0.2)  # train / val / test, per theme

# Table 1 of the proposal, in release order: (model id in the data, display name, release date, $/1M input, $/1M output)
LLMROUTERBENCH_MODELS = [
    ("deepseek-v3-0324", "DeepSeek-V3-0324", "2025-03-24", 0.25, 0.88),
    ("claude-sonnet-4", "Claude-Sonnet-4", "2025-05-22", 3.00, 15.00),
    ("deepseek-r1-0528", "DeepSeek-R1-0528", "2025-05-28", 0.50, 2.15),
    ("gemini-2.5-flash", "Gemini-2.5-Flash", "2025-06-17", 0.30, 2.50),
    ("gemini-2.5-pro", "Gemini-2.5-Pro", "2025-06-17", 1.25, 10.00),
    ("qwen3-235b-a22b-2507", "Qwen3-235B-A22B-2507", "2025-07-21", 0.09, 0.60),
    ("qwen3-235b-a22b-thinking-2507", "Qwen3-235B-A22B-Thinking-2507", "2025-07-25", 0.30, 2.90),
    ("intern-s1", "Intern-S1", "2025-07-26", 0.18, 0.54),
    ("gpt-5-chat", "GPT-5-chat", "2025-08-07", 1.25, 10.00),
    ("gpt-5", "GPT-5-medium", "2025-08-07", 1.25, 10.00),
    ("kimi-k2-0905", "Kimi-K2-0905", "2025-09-05", 0.50, 2.00),
    ("deepseek-v3.1-terminus", "DeepSeek-V3.1-Terminus", "2025-09-22", 0.27, 1.00),
    ("glm-4.6", "GLM-4.6", "2025-09-30", 0.60, 2.20),
]
# Table 1 (month granularity), with WizardLM-13B-V1.2 corrected from Sep to Jul (Hugging Face createdAt 2023-07-25).
# Prices: TOKEN_COSTS in deps/routerbench/routers/common.py, as that code applies them (per token × 1e6). Information
# only: costs come from the recorded `total_cost`.
ROUTERBENCH_MODELS = [
    ("claude-instant-v1", "claude-instant-v1", "2023-03", 0.08, 0.24),
    ("claude-v1", "claude-v1", "2023-03", 0.80, 2.40),
    ("claude-v2", "claude-v2", "2023-07", 0.80, 2.40),
    ("meta/llama-2-70b-chat", "llama-2-70b-chat", "2023-07", 0.09, 0.09),
    ("WizardLM/WizardLM-13B-V1.2", "WizardLM-13B-V1.2", "2023-07", 0.03, 0.03),
    ("meta/code-llama-instruct-34b-chat", "code-llama-instruct-34b-chat", "2023-08", 0.0776, 0.0776),
    ("mistralai/mistral-7b-chat", "mistral-7b-chat", "2023-09", 0.02, 0.02),
    ("gpt-3.5-turbo-1106", "gpt-3.5-turbo-1106", "2023-11", 0.10, 0.20),
    ("gpt-4-1106-preview", "gpt-4-1106-preview", "2023-11", 1.00, 3.00),
    ("zero-one-ai/Yi-34B-Chat", "Yi-34B-Chat", "2023-11", 0.08, 0.08),
    ("mistralai/mixtral-8x7b-chat", "mixtral-8x7b-chat", "2023-12", 0.06, 0.06),
]
MODEL_TABLES = {"llmrouterbench": LLMROUTERBENCH_MODELS, "routerbench": ROUTERBENCH_MODELS}


@dataclass
class Data:
    """One benchmark, one split and one model pool, in the form the harness's `evaluate` takes. The first nine fields
    are the harness's `Data` (michal-harness/router.py); the rest are optional extras."""
    queries: list[str]
    models: list[str]
    S: np.ndarray       # (Q, M) scores in [0, 1], every model on every query
    cost: np.ndarray    # (M,) mean per-query cost of each model in `models`
    train: np.ndarray   # query indices
    val: np.ndarray     # used ONLY to tune k; embedding training (early stopping included) must never see it
    test: np.ndarray
    theme: np.ndarray | None = None  # task type of each query (source dataset or eval family)
    split_seed: int = 0
    benchmark: str | None = None
    query_ids: np.ndarray | None = None
    subtask: np.ndarray | None = None  # finest task label available (falls back to theme)
    epoch: int | None = None           # release epoch of the pool
    new_model: str | None = None       # the unseen model of an instance (in `models`), None for an epoch pool


def release_epochs(benchmark):
    """One row per release event: epoch, date, the models released then, and the pool up to and including it."""
    rows, pool = [], []
    table = MODEL_TABLES[benchmark]
    for e, date in enumerate(sorted({m[2] for m in table})):
        new = [m[0] for m in table if m[2] == date]
        pool = pool + new
        rows.append({"epoch": e, "date": date, "new_models": new, "pool": pool})
    return pd.DataFrame(rows)


def unseen_instances(benchmark):
    """One unseen-model instance per model released after the first event. The pool is every model released strictly
    before the event, plus the new model (models released the same day are left out: they have no labels yet)."""
    rows = []
    for _, ev in release_epochs(benchmark).iloc[1:].iterrows():
        before = [m for m in ev.pool if m not in ev.new_models]
        for m in ev.new_models:
            rows.append({"instance": len(rows), "epoch": ev.epoch, "date": ev.date, "new_model": m,
                         "pool": before + [m]})
    return pd.DataFrame(rows)


@lru_cache(maxsize=None)
def _tables(benchmark, root):
    d = Path(root) / benchmark
    queries = pd.read_parquet(d / "queries.parquet")
    models = pd.read_csv(d / "models.csv")
    scores = pd.read_parquet(d / "scores.parquet")
    S = (scores.pivot(index="query_id", columns="model", values="score")
         .reindex(index=queries.query_id, columns=models.model).to_numpy(np.float64))
    assert not np.isnan(S).any(), "score matrix is incomplete"
    return queries, models, S


def load_split(benchmark, split_seed=0, root=DATA_DIR):
    """(train, val, test) query indices of one split seed."""
    z = np.load(Path(root) / benchmark / "splits" / f"seed{split_seed}.npz")
    return z["train"], z["val"], z["test"]


def load_data(benchmark, split_seed=0, epoch=None, instance=None, text="query", root=DATA_DIR):
    """`Data` for one benchmark and split seed. The pool is:
    - epoch=None, instance=None: every model (the final pool);
    - epoch=t: the models released up to and including epoch t (seen-model setting at t);
    - instance=i: the pool of unseen instance i, with `Data.new_model` set; pass it to `evaluate(new_model=...)`.
    text="query" gives the bare question, text="prompt" the full prompt as sent to the models."""
    assert benchmark in BENCHMARKS, f"benchmark must be one of {BENCHMARKS}"
    assert epoch is None or instance is None, "give epoch or instance, not both"
    assert text in ("query", "prompt")
    queries, models, S = _tables(benchmark, str(root))
    new_model = None
    if instance is not None:
        inst = unseen_instances(benchmark).iloc[instance]
        pool, epoch, new_model = inst.pool, int(inst.epoch), inst.new_model
    elif epoch is not None:
        pool = release_epochs(benchmark).iloc[epoch].pool
    else:
        pool = models.model.tolist()
    cols = [models.model.tolist().index(m) for m in pool]
    train, val, test = load_split(benchmark, split_seed, root)
    return Data(queries=queries[text].tolist(), models=list(pool), S=S[:, cols],
                cost=models.mean_cost.to_numpy(np.float64)[cols], train=train, val=val, test=test,
                theme=queries.theme.to_numpy(), split_seed=split_seed, benchmark=benchmark,
                query_ids=queries.query_id.to_numpy(), subtask=queries.subtask.to_numpy(), epoch=epoch,
                new_model=new_model)


def sample_probes(train, n, seed, theme=None):
    """Query indices of the `n` probes of a new model, drawn from the training queries `train`. Nested: with the same
    seed, the probes of a smaller n are contained in those of a larger n.
    theme=None: the first n of a seeded permutation of `train` (the harness's rule).
    theme=<task type of every query, e.g. Data.theme>: proportional stratified sampling, still nested. Each theme's
    training queries are permuted, the j-th of a theme of size N_t gets the key (j + 0.5) / N_t, and the probes are the
    n smallest keys (ties broken at random), so every prefix holds each theme in proportion to its size."""
    train = np.asarray(train)
    rng = np.random.default_rng(seed)
    if theme is None:
        return train[rng.permutation(len(train))[:n]]
    th = np.asarray(theme)[train]
    key = np.empty(len(train))
    for t in np.unique(th):
        pos = rng.permutation(np.flatnonzero(th == t))
        key[pos] = (np.arange(len(pos)) + 0.5) / len(pos)
    return train[np.lexsort((rng.random(len(train)), key))[:n]]
