"""Frozen sentence features and the proposal's non-learned baselines."""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

DEFAULT_ENCODER = "sentence-transformers/all-MiniLM-L6-v2"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:20]


class SentenceFeatures:
    """Cache sentence vectors; encode new text with the same frozen encoder on demand."""

    def __init__(self, queries, cache_dir, encoder=DEFAULT_ENCODER, batch_size=64, device="cpu"):
        self.queries = list(queries)
        self.encoder_name, self.batch_size, self.device = encoder, batch_size, device
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.key = fingerprint({"queries": self.queries, "encoder": encoder, "normalize": True,
                                "max_seq_length": 256})
        self.path = self.cache_dir / f"sentences-{self.key}.npy"
        self.positions = {q: i for i, q in enumerate(self.queries)}
        self.encoder = None
        if self.path.exists():
            self.values = np.load(self.path)
        else:
            self.values = self._encode(self.queries)
            np.save(self.path, self.values)
            self.path.with_suffix(".json").write_text(json.dumps({
                "encoder": encoder, "max_seq_length": 256, "normalized": True,
                "query_hash": fingerprint(self.queries), "shape": list(self.values.shape)}, indent=2))

    def _encode(self, queries):
        if self.encoder is None:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer(self.encoder_name, device=self.device,
                                               cache_folder=str(self.cache_dir / "encoder"))
            self.encoder.max_seq_length = 256
        return np.asarray(self.encoder.encode(queries, batch_size=self.batch_size,
                          normalize_embeddings=True, convert_to_numpy=True,
                          show_progress_bar=len(queries) > self.batch_size), dtype=np.float32)

    def embed(self, queries):
        queries = list(queries)
        if not queries:
            return np.empty((0, self.values.shape[1]), dtype=np.float32)
        if all(q in self.positions for q in queries):
            return self.values[[self.positions[q] for q in queries]]
        return self._encode(queries)


def cached_embed(queries, values):
    """Dataset lookup for features that require benchmark-provided theme labels."""
    positions = {q: i for i, q in enumerate(queries)}
    values = np.asarray(values, dtype=np.float32)

    def embed(texts):
        try:
            return values[[positions[q] for q in texts]]
        except KeyError as exc:
            raise ValueError("Theme-based baselines require a query in the labeled benchmark") from exc
    return embed


def baselines(data, sentences):
    """Proposal baselines and a balanced concatenation; all scales fit on train only."""
    themes = sorted(set(data.theme))
    onehot = (np.asarray(data.theme)[:, None] == np.asarray(themes)[None, :]).astype(np.float32)
    # Lexical token count is an inexpensive query-length statistic (not an API billing count).
    stats = np.array([[len(q), len(re.findall(r"\w+|[^\w\s]", q)), q.count("\n") + 1]
                      for q in data.queries], dtype=np.float32)
    raw = np.column_stack([onehot, stats])
    handcrafted = StandardScaler().fit(raw[data.train]).transform(raw).astype(np.float32)
    # Match average squared block norms, since Euclidean squared distances add by block.
    # A single train-fitted scalar preserves relative geometry within each block.
    sentence_energy = np.square(sentences.values[data.train].astype(np.float64)).sum(1).mean()
    handcrafted_energy = np.square(handcrafted[data.train].astype(np.float64)).sum(1).mean()
    weight = np.sqrt(sentence_energy / handcrafted_energy) if handcrafted_energy > 0 else 1.0
    values = {"task_type": onehot, "handcrafted": handcrafted,
              "frozen": sentences.values,
              "combined": np.column_stack([sentences.values, handcrafted]),
              "combined_balanced": np.column_stack([sentences.values, handcrafted * weight])}
    return {name: cached_embed(data.queries, E) for name, E in values.items()}
