"""Handcrafted query representation (Alexandros, representation (i) of the proposal, plus the RQ1a variant).

phi(x) = [ w_onehot * onehot(task type of x) , w_stats * zscore(statistics of the query string) ]

Everything here is frozen: nothing depends on the model pool, so every `fit` factory ignores `train_models` and
returns the same `embed`. The z-scores are fitted on `data.train` only (never on `data.val` or `data.test`) and the
one-hot categories are the task types seen in `data.train`. Distances in the harness are Euclidean, so the relative
weight of the one-hot block against the numeric block matters; it is a parameter (`onehot_weight`).

How the task-type label reaches `embed`: the harness calls `fit(pool)(data.queries)` with a plain list of strings,
so the label cannot travel with the query. The factories here take `data` and build a query string -> label lookup
from `data.theme`; `embed` looks each query up by its text. See README.md ("Open assumptions") and HARNESS_NOTES.md.

Usage:
    from handcrafted import fit_handcrafted, fit_task_type_only, fit_stats_only, fit_concat
    out = Results(data, "llmrouterbench")
    out.run("handcrafted", fit_handcrafted(data), tune_k=True)
"""
from __future__ import annotations

import math
import re
import warnings
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

# ---------------------------------------------------------------- tokenizers

_WS = re.compile(r"\S+")


def whitespace_tokenize(text: str) -> list[str]:
    return _WS.findall(text)


def get_tokenizer(spec: str = "tiktoken:cl100k_base") -> tuple[str, Callable[[str], int]]:
    """Return (name, count_tokens). `spec` is "tiktoken:<encoding>", "hf:<model name>" or "whitespace".
    Falls back to whitespace counting, with a warning, when the requested tokenizer is not installed or cannot load
    (tiktoken fetches its BPE table from the network on first use; HF tokenizers are downloaded too)."""
    kind, _, name = spec.partition(":")
    if kind == "whitespace":
        return "whitespace", lambda s: len(whitespace_tokenize(s))
    if kind not in ("tiktoken", "hf"):
        raise ValueError(f"unknown tokenizer spec {spec!r}; use 'tiktoken:<enc>', 'hf:<name>' or 'whitespace'")
    try:
        if kind == "tiktoken":
            import tiktoken
            enc = tiktoken.get_encoding(name or "cl100k_base")
            return f"tiktoken:{enc.name}", lambda s: len(enc.encode(s, disallowed_special=()))
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(name)
        return f"hf:{name}", lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
    except Exception as e:  # ImportError, unknown encoding, network errors, missing model
        warnings.warn(f"tokenizer {spec!r} unavailable ({type(e).__name__}: {e}); counting whitespace tokens instead")
        return "whitespace", lambda s: len(whitespace_tokenize(s))


# ---------------------------------------------------------------- query statistics (the one place to extend)

_SENTENCE_END = re.compile(r"[.!?]+(?:\s|$)")
_DIGIT = re.compile(r"\d")
_MATH = re.compile(r"[+\-*/=^<>%|\\∑∏∫√±×÷≤≥≠≈∞π∂∇∈∉⊂⊆∪∩∧∨¬→←⇒⇔]|\$[^$]+\$|\\\(|\\\[|\\frac|\\sqrt|\\int|\\sum")
_CODE = re.compile(
    r"```|`[^`]+`|[{}\[\];]|==|!=|<=|>=|=>|->|::|&&|\|\||\+\+|\bdef\b|\breturn\b|\bimport\b|\bclass\b|\bfunction\b|"
    r"\bprint\s*\(|\bfor\s*\(|\bwhile\s*\(|\bif\s*\(|#include|\bpublic\b|\bstatic\b|\bvoid\b|\bconst\b|\blet\b|\bvar\b|"
    r"\bSELECT\b|\bFROM\b|\bWHERE\b|\bnull\b|\bNone\b|\bTrue\b|\bFalse\b|\bprintf\b|\bstd::|\$\w+|\.py\b|\.js\b|\.cpp\b")
_UPPER = re.compile(r"[A-Z]")
_LETTER = re.compile(r"[A-Za-z]")
_PUNCT = re.compile(r"[^\w\s]")


@dataclass(frozen=True)
class Feature:
    """One query statistic. `fn(text, words, n_tokens) -> float`. `log` applies log1p before standardization (for
    heavy-tailed counts), so a few very long queries do not stretch the scale of everyone else."""
    name: str
    fn: Callable[[str, list[str], int], float]
    log: bool = False


def _frac(num, den):
    return num / den if den else 0.0


FEATURES: list[Feature] = [
    Feature("n_tokens", lambda t, w, n: n, log=True),
    Feature("n_chars", lambda t, w, n: len(t), log=True),
    Feature("n_words", lambda t, w, n: len(w), log=True),
    Feature("n_sentences", lambda t, w, n: max(1, len(_SENTENCE_END.findall(t))) if t.strip() else 0, log=True),
    Feature("n_lines", lambda t, w, n: t.count("\n") + 1 if t else 0, log=True),
    Feature("n_question_marks", lambda t, w, n: t.count("?"), log=True),
    Feature("n_code_markers", lambda t, w, n: len(_CODE.findall(t)), log=True),
    Feature("has_code", lambda t, w, n: float(bool(_CODE.search(t)))),
    Feature("digit_density", lambda t, w, n: _frac(len(_DIGIT.findall(t)), len(t))),
    Feature("math_symbol_density", lambda t, w, n: _frac(len(_MATH.findall(t)), len(t))),
    Feature("punct_density", lambda t, w, n: _frac(len(_PUNCT.findall(t)), len(t))),
    Feature("frac_uppercase", lambda t, w, n: _frac(len(_UPPER.findall(t)), len(_LETTER.findall(t)))),
    Feature("frac_non_ascii", lambda t, w, n: _frac(sum(ord(c) > 127 for c in t), len(t))),
    Feature("avg_word_length", lambda t, w, n: _frac(sum(map(len, w)), len(w))),
    Feature("chars_per_token", lambda t, w, n: _frac(len(t), n)),  # tokenizer "surprise": code and math tokenize worse
]
FEATURE_NAMES = [f.name for f in FEATURES]


def query_stats(queries: list[str], count_tokens: Callable[[str], int] | None = None,
                features: list[Feature] = FEATURES) -> np.ndarray:
    """Raw (not standardized, not logged) statistics, shape (n_queries, len(features))."""
    count_tokens = count_tokens or get_tokenizer()[1]
    X = np.empty((len(queries), len(features)))
    for i, q in enumerate(queries):
        q = q if isinstance(q, str) else str(q)
        words, n_tok = whitespace_tokenize(q), count_tokens(q)
        X[i] = [f.fn(q, words, n_tok) for f in features]
    return X


# ---------------------------------------------------------------- the embedding

def _train_rows(data) -> list[str]:
    return [data.queries[i] for i in data.train]


def _label_lookup(data) -> dict[str, object]:
    """query text -> task type, from `data.theme`. Duplicated texts with different labels keep the first and warn."""
    if getattr(data, "theme", None) is None:
        raise ValueError("data.theme is None: the task-type variants need a task-type label per query "
                         "(Arman's loader must fill Data.theme). Use fit_stats_only otherwise.")
    theme = np.asarray(data.theme)
    assert len(theme) == len(data.queries), "data.theme must have one label per query"
    lookup, conflicts = {}, 0
    for q, t in zip(data.queries, theme.tolist()):
        if q in lookup and lookup[q] != t:
            conflicts += 1
        lookup.setdefault(q, t)
    if conflicts:
        warnings.warn(f"{conflicts} duplicated query texts carry different task types; the first label is used")
    return lookup


@dataclass
class HandcraftedEmbedding:
    """Frozen embedding `embed(list[str]) -> (n, d)`, fitted on `data.train` at construction.

    Blocks (each can be switched off):
      one-hot of the task type (`data.theme`), categories = those present in the training split, unknown -> all zeros;
      z-scored query statistics (`FEATURES`), with log1p on the count features first, clipped at ±`clip` std.
    Weights: `onehot_weight` and `stats_weight` multiply the blocks. A float is used as is. "balanced" scales the
    one-hot block so that its total variance on the training queries equals that of the numeric block (so in the
    Euclidean distance neither block dominates by construction); with the numeric block off, "balanced" means 1.0.
    The rows for `data.queries` are precomputed once; `embed` looks queries up by text and computes fresh statistics
    for texts it has not seen (those get an all-zero one-hot row, with a warning)."""
    data: object
    use_task_type: bool = True
    use_stats: bool = True
    onehot_weight: float | str = "balanced"
    stats_weight: float = 1.0
    tokenizer: str = "tiktoken:cl100k_base"
    clip: float = 5.0
    features: list[Feature] = field(default_factory=lambda: list(FEATURES))
    # fitted state
    categories: list = field(init=False, default_factory=list)
    mean_: np.ndarray | None = field(init=False, default=None)
    std_: np.ndarray | None = field(init=False, default=None)
    onehot_scale: float = field(init=False, default=1.0)
    tokenizer_name: str = field(init=False, default="")

    def __post_init__(self):
        assert self.use_task_type or self.use_stats, "switch on at least one block"
        data = self.data
        train_idx = np.asarray(data.train)
        self._rows: dict[str, np.ndarray] = {}
        self._labels = _label_lookup(data) if self.use_task_type else {}
        self.tokenizer_name, self._count_tokens = get_tokenizer(self.tokenizer) if self.use_stats else ("", None)

        if self.use_task_type:
            train_labels = np.asarray(data.theme)[train_idx]
            self.categories = sorted(set(train_labels.tolist()), key=str)
        if self.use_stats:
            X = self._raw(list(data.queries))                      # (Q, d_stats), logged
            self.mean_ = X[train_idx].mean(0)
            self.std_ = X[train_idx].std(0)
            self.std_[self.std_ < 1e-12] = 1.0                      # constant feature -> stays 0 after centering
            Z = self._standardize(X)
        else:
            Z = np.zeros((len(data.queries), 0))
        H = self._onehot([self._labels.get(q) for q in data.queries]) if self.use_task_type else np.zeros((len(data.queries), 0))
        self.onehot_scale = self._resolve_onehot_weight(H[train_idx], Z[train_idx])
        E = np.hstack([self.onehot_scale * H, self.stats_weight * Z])
        for q, row in zip(data.queries, E):
            self._rows.setdefault(q, row)

    # -- pieces
    def _raw(self, queries):
        X = query_stats(queries, self._count_tokens, self.features)
        log = np.array([f.log for f in self.features])
        X[:, log] = np.log1p(np.maximum(X[:, log], 0))
        return X

    def _standardize(self, X):
        Z = (X - self.mean_) / self.std_
        return np.clip(Z, -self.clip, self.clip) if self.clip else Z

    def _onehot(self, labels):
        index = {c: j for j, c in enumerate(self.categories)}
        H = np.zeros((len(labels), len(self.categories)))
        for i, lab in enumerate(labels):
            j = index.get(lab)
            if j is not None:
                H[i, j] = 1.0
        return H

    def _resolve_onehot_weight(self, H_train, Z_train):
        if not self.use_task_type:
            return 0.0
        if self.onehot_weight != "balanced":
            return float(self.onehot_weight)
        if not self.use_stats or Z_train.shape[1] == 0:
            return 1.0
        var_stats = (self.stats_weight ** 2) * Z_train.var(0).sum()
        var_onehot = H_train.var(0).sum()
        return math.sqrt(var_stats / var_onehot) if var_onehot > 0 else 1.0

    # -- the embed function
    @property
    def dim(self) -> int:
        return (len(self.categories) if self.use_task_type else 0) + (len(self.features) if self.use_stats else 0)

    @property
    def feature_names(self) -> list[str]:
        names = [f"task={c}" for c in self.categories] if self.use_task_type else []
        return names + ([f.name for f in self.features] if self.use_stats else [])

    def __call__(self, queries: list[str]) -> np.ndarray:
        E = np.empty((len(queries), self.dim))
        missing = [i for i, q in enumerate(queries) if q not in self._rows]
        for i, q in enumerate(queries):
            if q in self._rows:
                E[i] = self._rows[q]
        if missing:
            texts = [queries[i] for i in missing]
            if self.use_task_type:
                unknown = [q for q in texts if q not in self._labels]
                if unknown:
                    warnings.warn(f"{len(unknown)} queries have no task-type label (not in data.queries); "
                                  "their one-hot block is all zeros")
            H = self.onehot_scale * self._onehot([self._labels.get(q) for q in texts]) if self.use_task_type \
                else np.zeros((len(texts), 0))
            Z = self.stats_weight * self._standardize(self._raw(texts)) if self.use_stats else np.zeros((len(texts), 0))
            E[missing] = np.hstack([H, Z])
        return E

    def fit(self, train_models=None):
        """The harness `fit` contract: frozen, so the pool is ignored."""
        return self

    def describe(self) -> str:
        parts = []
        if self.use_task_type:
            parts.append(f"one-hot task type ({len(self.categories)} categories) x {self.onehot_scale:.3g}")
        if self.use_stats:
            parts.append(f"{len(self.features)} z-scored statistics ({self.tokenizer_name}) x {self.stats_weight:g}")
        return " + ".join(parts) + f" -> d = {self.dim}"


# ---------------------------------------------------------------- fit factories (what the harness takes)

def fit_task_type_only(data, **kw) -> Callable:
    """RQ1a: one-hot task-type label alone. `fit(train_models) -> embed`."""
    return HandcraftedEmbedding(data, use_task_type=True, use_stats=False, **kw).fit


def fit_stats_only(data, **kw) -> Callable:
    """Standardized query statistics alone (no label)."""
    return HandcraftedEmbedding(data, use_task_type=False, use_stats=True, **kw).fit


def fit_handcrafted(data, **kw) -> Callable:
    """Representation (i): one-hot task type + standardized query statistics."""
    return HandcraftedEmbedding(data, use_task_type=True, use_stats=True, **kw).fit


def fit_concat_factory(other_fit, data, features_weight: float | str = "balanced", **kw) -> Callable:
    """Representation (iii) for an embedding given as a factory `other_fit(train_models) -> embed`
    (e.g. a learned embedding that is retrained per pool). The handcrafted block is appended to each row.
    `features_weight`: float, or "balanced" to give the handcrafted block the same total variance on the training
    queries as the other block (computed inside the returned embed, so it adapts to a retrained embedding)."""
    hand = HandcraftedEmbedding(data, **kw)
    train_texts = set(_train_rows(data))

    def fit(train_models):
        other = other_fit(train_models)

        def embed(queries):
            A = np.asarray(other(queries), dtype=float)
            B = hand(queries)
            if features_weight == "balanced":
                tr = np.fromiter((q in train_texts for q in queries), bool, len(queries))
                rows = tr if tr.any() else np.ones(len(queries), bool)
                va, vb = A[rows].var(0).sum(), B[rows].var(0).sum()
                w = math.sqrt(va / vb) if vb > 0 and va > 0 else 1.0
            else:
                w = float(features_weight)
            return np.hstack([A, w * B])
        return embed
    return fit


def fit_concat(other_embed, data, features_weight: float | str = "balanced", **kw) -> Callable:
    """Representation (iii) for a frozen embedding `other_embed(list[str]) -> ndarray` (e.g. an L2-normalized
    sentence encoder): `fit_concat(embed, data)` is a `fit` whose rows are [other_embed(q), w * handcrafted(q)]."""
    return fit_concat_factory(lambda train_models: other_embed, data, features_weight, **kw)


VARIANTS = {  # name written in results.csv -> factory(data, **kw)
    "task_type": fit_task_type_only,
    "stats": fit_stats_only,
    "handcrafted": fit_handcrafted,
}
