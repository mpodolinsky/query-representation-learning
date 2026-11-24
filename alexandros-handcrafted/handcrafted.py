"""Handcrafted query representation (Alexandros, representation (i) of the proposal, plus the RQ1a variant).

phi(x) = [ w_task * ( w_1 * onehot(level-1 domain), w_2 * onehot(level-2 subdomain) ),
           w_stats * zscore(statistics of the query string)  (optionally PCA-whitened) ]

The main variant (`handcrafted`) uses Levels 1 and 2. Level 3 is free text with thousands of categories (one per
query, nearly), so its one-hot is a named ablation (`handcrafted_L123`, `task_type_L123`), not part of the default.
A third, optional block (`within_level`) is a one-hot with a weight so large that the Euclidean nearest neighbors
never cross a category boundary while the category still has neighbors to give: `stats_within_theme` is the
statistics block with the kNN restricted to the query's own theme (dataset), to tell whether the statistics carry
signal beyond the task type.

Everything here is frozen: nothing depends on the model pool, so every `fit` factory ignores `train_models` and
returns the same `embed`. The z-scores are fitted on `data.train` only (never on `data.val` or `data.test`) and the
one-hot categories are the task types seen in `data.train`. Distances in the harness are Euclidean, so the relative
weight of the one-hot block against the numeric block matters; it is a parameter (`onehot_weight`).

How the task-type label reaches `embed`: the harness calls `fit(pool)(data.queries)` with a plain list of strings,
so the label cannot travel with the query. The factories here take `data` and build query string -> label lookups;
`embed` looks each query up by its text. See README.md ("Open assumptions") and HARNESS_NOTES.md.

Task-type levels (the proposal's Figure 1): Level 1 = domain, Level 2 = subdomain, Level 3 = specific task.
Where the labels of a level come from, in order: the `labels` argument (explicit arrays), a per-query column of the
data (`level_columns`, default task_level1/2/3), and for Level 1 only the taxonomy table (task_taxonomy.py) applied
to the raw label in `data.theme`. Level 0 is the raw label itself. A level with no source is skipped, so the module
works with Level 1 alone until the finer labels exist; asking only for missing levels raises MissingLevels.

Usage:
    from handcrafted import fit_handcrafted, fit_task_type_only, fit_stats_only, fit_concat
    out = Results(data, "llmrouterbench")
    out.run("task_type_L1", fit_task_type_only(data, levels=(1,)), tune_k=True)   # RQ1a per level
    out.run("handcrafted", fit_handcrafted(data), tune_k=True)                  # Levels 1 + 2 + statistics
"""
from __future__ import annotations

import math
import re
import warnings
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

import task_taxonomy

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

class MissingLevels(ValueError):
    """Raised when none of the requested task-type levels has a label source in the data."""


DEFAULT_LEVEL_COLUMNS = {1: "task_level1", 2: "task_level2", 3: "task_level3"}


def _text_lookup(queries, labels, what) -> dict[str, object]:
    """query text -> label. Duplicated texts with different labels keep the first and warn."""
    labels = np.asarray(labels, dtype=object)
    assert len(labels) == len(queries), f"{what}: one label per query expected"
    lookup, conflicts = {}, 0
    for q, t in zip(queries, labels.tolist()):
        if q in lookup and lookup[q] != t:
            conflicts += 1
        lookup.setdefault(q, t)
    if conflicts:
        warnings.warn(f"{what}: {conflicts} duplicated query texts carry different labels; the first label is used")
    return lookup


def level_labels(data, level, labels=None, level_columns=DEFAULT_LEVEL_COLUMNS, raw_column="theme", warn=True):
    """Per-query labels of one task-type level, or None if the data has no source for it.
    Sources, in order: `labels[level]`, the data attribute `level_columns[level]`, the taxonomy (Level 1 only) applied
    to the raw label in `data.<raw_column>`. Level 0 is the raw label itself."""
    if labels and labels.get(level) is not None:
        return np.asarray(labels[level], dtype=object)
    col = level_columns.get(level)
    if col and getattr(data, col, None) is not None:
        return np.asarray(getattr(data, col), dtype=object)
    raw = getattr(data, raw_column, None)
    if raw is None:
        return None
    if level == 0:
        return np.asarray(raw, dtype=object)
    if level == 1:
        return np.asarray(task_taxonomy.map_labels(raw, warn=warn), dtype=object)
    return None


def _whitening(Z_train, eps=1e-8):
    """PCA whitening fitted on the standardized training block: returns W such that (Z @ W) has identity covariance
    on the training rows. Components with (near) zero variance are dropped, so the output can have fewer columns."""
    cov = np.cov(Z_train, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    keep = vals > eps * vals.max()
    return vecs[:, keep] / np.sqrt(vals[keep])


@dataclass
class HandcraftedEmbedding:
    """Frozen embedding `embed(list[str]) -> (n, d)`, fitted on `data.train` at construction.

    Blocks (each can be switched off):
      task type: one one-hot block per requested level (see `level_labels`), categories = those present in the
        training split, an unknown category -> all zeros for that level's block; each level scaled by `level_weights`;
      statistics: z-scored `FEATURES` (log1p on the count features first, clipped at ±`clip` std), optionally
        PCA-whitened on the training split (`whiten=True`, decorrelates n_tokens / n_chars / n_words / chars_per_token).
    Weights: `onehot_weight` multiplies the whole task-type block, `stats_weight` the numeric block. A float is used
    as is. "balanced" scales the task-type block so that its total variance on the training queries equals that of
    the numeric block (neither block dominates the Euclidean distance by construction); with the numeric block off,
    "balanced" means 1.0. `level_weights` (dict level -> float, default 1.0 each) set the relative weight of the
    levels inside the task-type block before that scaling.
    `within_level` (None by default) adds a one-hot of that level (0 = the raw theme) weighted by `within_weight`,
    chosen so large that two queries of different categories are always farther apart than any two queries of the
    same category: the harness's Euclidean kNN then stays inside the query's category as long as it has neighbors
    left, and only then spills over (ordered by the other blocks). The construction warns if `within_weight` is
    not large enough for the other blocks' spread on `data.queries`.
    The rows for `data.queries` are precomputed once; `embed` looks queries up by text and computes fresh statistics
    for texts it has not seen (those get all-zero task-type blocks, with a warning)."""
    data: object
    use_task_type: bool = True
    use_stats: bool = True
    levels: tuple = (1, 2)                     # requested task-type levels; the ones without a source are skipped
    level_weights: dict | None = None          # level -> weight inside the task-type block (default 1.0 each)
    level_columns: dict = field(default_factory=lambda: dict(DEFAULT_LEVEL_COLUMNS))
    raw_column: str = "theme"                  # where the raw task-type label (dataset name) lives in the data
    labels: dict | None = None                 # explicit {level: array of labels aligned with data.queries}
    onehot_weight: float | str = "balanced"
    stats_weight: float = 1.0
    whiten: bool = False
    within_level: int | None = None            # restrict the kNN to this level's category (0 = raw theme); see above
    within_weight: float = 100.0
    tokenizer: str = "tiktoken:cl100k_base"
    clip: float = 5.0
    features: list[Feature] = field(default_factory=lambda: list(FEATURES))
    # fitted state
    level_categories: dict = field(init=False, default_factory=dict)   # level -> sorted categories seen in train
    within_categories: list = field(init=False, default_factory=list)  # categories of the within block (train)
    mean_: np.ndarray | None = field(init=False, default=None)
    std_: np.ndarray | None = field(init=False, default=None)
    whitening_: np.ndarray | None = field(init=False, default=None)
    onehot_scale: float = field(init=False, default=1.0)
    tokenizer_name: str = field(init=False, default="")

    def __post_init__(self):
        assert self.use_task_type or self.use_stats, "switch on at least one block"
        data = self.data
        train_idx = np.asarray(data.train)
        queries = list(data.queries)
        self._rows: dict[str, np.ndarray] = {}
        self._lookups: dict[int, dict] = {}
        self._within_lookup: dict = {}
        self.tokenizer_name, self._count_tokens = get_tokenizer(self.tokenizer) if self.use_stats else ("", None)

        if self.use_task_type:
            missing = []
            for level in self.levels:
                labs = level_labels(data, level, self.labels, self.level_columns, self.raw_column)
                if labs is None:
                    missing.append(level)
                    continue
                self._lookups[level] = _text_lookup(queries, labs, f"level {level}")
                self.level_categories[level] = sorted(set(labs[train_idx].tolist()), key=str)
            if not self.level_categories:
                raise MissingLevels(
                    f"none of the requested task-type levels {tuple(self.levels)} has labels: levels 2 and 3 need the "
                    f"columns {[self.level_columns.get(l) for l in self.levels if l > 1]} on the data (or the `labels` "
                    f"argument), level 1 needs them or a raw label in data.{self.raw_column}. Use fit_stats_only otherwise.")
            if missing:
                warnings.warn(f"task-type levels {missing} have no labels in the data and are skipped; "
                              f"using levels {self.available_levels}")
            H = self._task_block(queries)
        else:
            H = np.zeros((len(queries), 0))

        if self.use_stats:
            X = self._raw(queries)                                  # (Q, d_stats), logged
            self.mean_ = X[train_idx].mean(0)
            self.std_ = X[train_idx].std(0)
            self.std_[self.std_ < 1e-12] = 1.0                      # constant feature -> stays 0 after centering
            Z = (X - self.mean_) / self.std_
            if self.clip:
                Z = np.clip(Z, -self.clip, self.clip)
            if self.whiten:
                self.whitening_ = _whitening(Z[train_idx])
            Z = self._stats_transform(X)
        else:
            Z = np.zeros((len(queries), 0))
        self.onehot_scale = self._resolve_onehot_weight(H[train_idx], Z[train_idx])
        E = np.hstack([self.onehot_scale * H, self.stats_weight * Z])

        if self.within_level is not None:
            labs = level_labels(data, self.within_level, self.labels, self.level_columns, self.raw_column)
            if labs is None:
                raise MissingLevels(f"within_level={self.within_level} has no labels in the data")
            self._within_lookup = _text_lookup(queries, labs, f"within level {self.within_level}")
            self.within_categories = sorted(set(labs[train_idx].tolist()), key=str)
            spread = 2 * np.linalg.norm(E, axis=1).max()        # upper bound of any distance inside a category
            if spread >= self.within_weight * math.sqrt(2):
                warnings.warn(f"within_weight={self.within_weight:g} is too small: two queries of one category can be "
                              f"{spread:.1f} apart, more than the {self.within_weight * math.sqrt(2):.1f} between "
                              f"categories; the kNN may cross categories. Raise within_weight.")
            E = np.hstack([E, self._within_block(queries)])
        for q, row in zip(queries, E):
            self._rows.setdefault(q, row)

    # -- pieces
    @property
    def available_levels(self) -> list[int]:
        return list(self.level_categories)

    def _level_weight(self, level) -> float:
        return float((self.level_weights or {}).get(level, 1.0))

    @staticmethod
    def _onehot(queries, lookup, cats) -> np.ndarray:
        """(n, len(cats)) one-hot of the category of each query text; an unknown category is an all-zero row."""
        index = {c: j for j, c in enumerate(cats)}
        H = np.zeros((len(queries), len(cats)))
        for i, q in enumerate(queries):
            j = index.get(lookup.get(q))
            if j is not None:
                H[i, j] = 1.0
        return H

    def _task_block(self, queries) -> np.ndarray:
        """Concatenated per-level one-hot blocks (unscaled by onehot_weight) for query texts."""
        blocks = [self._level_weight(level) * self._onehot(queries, self._lookups[level], cats)
                  for level, cats in self.level_categories.items()]
        return np.hstack(blocks) if blocks else np.zeros((len(queries), 0))

    def _within_block(self, queries) -> np.ndarray:
        """The weighted one-hot of the within-level category (empty when `within_level` is None)."""
        if self.within_level is None:
            return np.zeros((len(queries), 0))
        return self.within_weight * self._onehot(queries, self._within_lookup, self.within_categories)

    def _raw(self, queries):
        X = query_stats(queries, self._count_tokens, self.features)
        log = np.array([f.log for f in self.features])
        X[:, log] = np.log1p(np.maximum(X[:, log], 0))
        return X

    def _stats_transform(self, X):
        Z = (X - self.mean_) / self.std_
        if self.clip:
            Z = np.clip(Z, -self.clip, self.clip)
        return Z @ self.whitening_ if self.whitening_ is not None else Z

    def _resolve_onehot_weight(self, H_train, Z_train):
        if not self.use_task_type:
            return 0.0
        if self.onehot_weight != "balanced":
            return float(self.onehot_weight)
        if not self.use_stats or Z_train.shape[1] == 0:
            return 1.0
        var_stats = (self.stats_weight ** 2) * Z_train.var(0).sum()
        var_task = H_train.var(0).sum()
        return math.sqrt(var_stats / var_task) if var_task > 0 else 1.0

    # -- the embed function
    @property
    def n_task_dims(self) -> int:
        return sum(len(c) for c in self.level_categories.values())

    @property
    def n_stats_dims(self) -> int:
        if not self.use_stats:
            return 0
        return self.whitening_.shape[1] if self.whitening_ is not None else len(self.features)

    @property
    def n_within_dims(self) -> int:
        return len(self.within_categories)

    @property
    def dim(self) -> int:
        return self.n_task_dims + self.n_stats_dims + self.n_within_dims

    @property
    def feature_names(self) -> list[str]:
        names = [f"L{level}={c}" for level, cats in self.level_categories.items() for c in cats]
        if self.use_stats:
            names += [f"stats_pc{j + 1}" for j in range(self.n_stats_dims)] if self.whitening_ is not None \
                else [f.name for f in self.features]
        names += [f"within_L{self.within_level}={c}" for c in self.within_categories]
        return names

    def __call__(self, queries: list[str]) -> np.ndarray:
        E = np.empty((len(queries), self.dim))
        missing = [i for i, q in enumerate(queries) if q not in self._rows]
        for i, q in enumerate(queries):
            if q in self._rows:
                E[i] = self._rows[q]
        if missing:
            texts = [queries[i] for i in missing]
            if self.use_task_type or self.within_level is not None:
                known = next(iter(self._lookups.values()), self._within_lookup)
                unknown = [q for q in texts if q not in known]
                if unknown:
                    warnings.warn(f"{len(unknown)} queries have no task-type label (not in data.queries); "
                                  "their task-type blocks are all zeros")
            H = self.onehot_scale * self._task_block(texts) if self.use_task_type else np.zeros((len(texts), 0))
            Z = self.stats_weight * self._stats_transform(self._raw(texts)) if self.use_stats else np.zeros((len(texts), 0))
            E[missing] = np.hstack([H, Z, self._within_block(texts)])
        return E

    def fit(self, train_models=None):
        """The harness `fit` contract: frozen, so the pool is ignored."""
        return self

    def stats_block(self, queries=None) -> np.ndarray:
        """The standardized (and whitened, if enabled) statistics block alone, unweighted, for diagnostics."""
        assert self.use_stats
        return self._stats_transform(self._raw(list(self.data.queries if queries is None else queries)))

    def describe(self) -> str:
        parts = []
        if self.use_task_type:
            lv = ", ".join(f"L{l}: {len(c)} cats x {self._level_weight(l):g}" for l, c in self.level_categories.items())
            parts.append(f"task type ({lv}) x {self.onehot_scale:.3g}")
        if self.use_stats:
            kind = f"{self.n_stats_dims} whitened components of {len(self.features)}" if self.whiten else f"{len(self.features)} z-scored"
            parts.append(f"{kind} statistics ({self.tokenizer_name}) x {self.stats_weight:g}")
        if self.within_level is not None:
            parts.append(f"kNN within level {self.within_level} ({self.n_within_dims} cats x {self.within_weight:g})")
        return " + ".join(parts) + f" -> d = {self.dim}"


# ---------------------------------------------------------------- fit factories (what the harness takes)

def fit_task_type_only(data, levels=(1,), **kw) -> Callable:
    """RQ1a: the task-type one-hot alone. `levels` picks the hierarchy levels, e.g. (1,), (2,), (1, 2), (1, 2, 3);
    (0,) is the raw label (dataset name). `fit(train_models) -> embed`."""
    return HandcraftedEmbedding(data, use_task_type=True, use_stats=False, levels=tuple(levels), **kw).fit


def fit_stats_only(data, **kw) -> Callable:
    """Standardized query statistics alone (no label). `whiten=True` for the PCA-whitened block."""
    return HandcraftedEmbedding(data, use_task_type=False, use_stats=True, **kw).fit


def fit_stats_within(data, level=0, **kw) -> Callable:
    """The statistics block with the kNN restricted to the query's own category of `level` (0 = the raw theme):
    if this beats the category's one-hot alone, the statistics carry signal beyond the task type."""
    return HandcraftedEmbedding(data, use_task_type=False, use_stats=True, within_level=level, **kw).fit


def fit_handcrafted(data, levels=(1, 2), **kw) -> Callable:
    """Representation (i): hierarchical task-type one-hot (the available levels among `levels`) + statistics.
    The default is Levels 1 and 2; Level 3 (free text, thousands of categories) is the named ablation `_L123`."""
    return HandcraftedEmbedding(data, use_task_type=True, use_stats=True, levels=tuple(levels), **kw).fit


def fit_concat_factory(other_fit, data, features_weight: float | str = "balanced", **kw) -> Callable:
    """Representation (iii) for an embedding given as a factory `other_fit(train_models) -> embed`
    (e.g. a learned embedding that is retrained per pool). The handcrafted block is appended to each row.
    `features_weight`: float, or "balanced" to give the handcrafted block the same total variance on the training
    queries as the other block (computed inside the returned embed, so it adapts to a retrained embedding)."""
    hand = HandcraftedEmbedding(data, **kw)
    train_texts = {data.queries[i] for i in data.train}

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


def _levels_variant(levels):
    return lambda data, **kw: fit_task_type_only(data, levels=levels, **kw)


VARIANTS = {  # name written in results.csv -> factory(data, **kw). Variants whose levels are missing raise MissingLevels.
    "task_type_raw": _levels_variant((0,)),          # the raw label as given (dataset name): the proposal's flat one-hot
    "task_type_L1": _levels_variant((1,)),           # RQ1a per level
    "task_type_L2": _levels_variant((2,)),
    "task_type_L3": _levels_variant((3,)),
    "task_type_L12": _levels_variant((1, 2)),
    "task_type_L123": _levels_variant((1, 2, 3)),    # ablation: with the free-text Level 3 as a one-hot
    "stats": fit_stats_only,
    "stats_whitened": lambda data, **kw: fit_stats_only(data, whiten=True, **kw),
    "stats_within_theme": lambda data, **kw: fit_stats_within(data, level=0, **kw),   # kNN inside the query's theme
    "handcrafted_L1": lambda data, **kw: fit_handcrafted(data, levels=(1,), **kw),
    "handcrafted": fit_handcrafted,                  # representation (i): Levels 1 + 2 + statistics
    "handcrafted_L123": lambda data, **kw: fit_handcrafted(data, levels=(1, 2, 3), **kw),   # ablation: + Level 3
    "handcrafted_whitened": lambda data, **kw: fit_handcrafted(data, whiten=True, **kw),
}
DEFAULT_VARIANTS = ["task_type_raw", "task_type_L1", "task_type_L2", "task_type_L12", "task_type_L123",
                    "stats", "stats_whitened", "stats_within_theme",
                    "handcrafted_L1", "handcrafted", "handcrafted_L123", "handcrafted_whitened"]
DEFAULT_UNSEEN_VARIANTS = ["handcrafted"]        # the unseen loop is 8 budgets x 5 seeds per held-out model: main variant only
DEFAULT_K_GRID = (5, 10, 20, 50, 100, 200, 300, 500, 1000)   # the harness grid tops at 200, where every variant landed
