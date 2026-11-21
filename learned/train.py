"""Train only on permitted model columns and a subset of data.train; never data.val/test."""
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from .features import fingerprint
from .model import QueryEmbedding, contrastive_loss


@dataclass(frozen=True)
class TrainConfig:
    objective: str = "regression"
    hidden_dim: int = 128
    embedding_dim: int = 64
    epochs: int = 50
    batch_size: int = 128
    learning_rate: float = 1e-3
    patience: int = 5
    stop_fraction: float = 0.1
    threshold: float = 0.1
    margin: float = 1.0
    seed: int = 0
    device: str = "cpu"

    def __post_init__(self):
        if self.objective not in ("regression", "contrastive"):
            raise ValueError("objective must be regression or contrastive")
        if min(self.hidden_dim, self.embedding_dim, self.epochs, self.patience) < 1 or self.batch_size < 2:
            raise ValueError("dimensions, epochs, patience must be positive; batch_size must be >= 2")
        if not 0 < self.stop_fraction < 1 or self.learning_rate <= 0:
            raise ValueError("stop_fraction must be in (0,1), learning_rate must be positive")
        if not 0 <= self.threshold <= 1 or self.margin <= 0:
            raise ValueError("threshold must be in [0,1], margin must be positive")


class LearnedEmbedder:
    def __init__(self, model, sentences, config):
        self.model, self.sentences, self.config = model.eval(), sentences, config
        self.values = None

    def __call__(self, queries):
        queries = list(queries)
        if self.values is not None and all(q in self.sentences.positions for q in queries):
            return self.values[[self.sentences.positions[q] for q in queries]]
        x = self.sentences.embed(queries)
        if not len(x):
            return np.empty((0, self.config.embedding_dim), dtype=np.float32)
        chunks = []
        with torch.inference_mode():
            for start in range(0, len(x), self.config.batch_size):
                batch = torch.as_tensor(x[start:start + self.config.batch_size],
                                        dtype=torch.float32, device=self.config.device)
                chunks.append(self.model.embed(batch).cpu().numpy())
        return np.concatenate(chunks)


def train_embedding(x, profiles, query_indices, model_names, config, directory):
    """Inputs contain training queries and allowed model columns only."""
    if len(x) < 4 or profiles.shape != (len(x), len(model_names)) or not len(model_names):
        raise ValueError("Need >= 4 training queries and a nonempty matching quality-profile matrix")
    torch.manual_seed(config.seed)
    rng = np.random.default_rng(config.seed)
    order = rng.permutation(len(x))
    n_stop = max(2, min(len(x) - 2, round(len(x) * config.stop_fraction)))
    stop, fit = order[:n_stop], order[n_stop:]
    model = QueryEmbedding(x.shape[1], len(model_names), config.hidden_dim,
                           config.embedding_dim).to(config.device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    X = torch.as_tensor(x, dtype=torch.float32, device=config.device)
    Y = torch.as_tensor(profiles, dtype=torch.float32, device=config.device)

    def loss_for(ids):
        z, predicted = model(X[ids])
        if config.objective == "regression":
            return F.mse_loss(predicted, Y[ids])
        return contrastive_loss(z, Y[ids], config.threshold, config.margin)

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    history, best_loss, best_epoch, stale = [], float("inf"), 0, 0
    for epoch in range(1, config.epochs + 1):
        model.train()
        total, count = 0.0, 0
        shuffled = rng.permutation(fit)
        for start in range(0, len(shuffled), config.batch_size):
            ids = shuffled[start:start + config.batch_size]
            if len(ids) < 2:
                continue
            optimizer.zero_grad()
            loss = loss_for(ids)
            loss.backward()
            optimizer.step()
            total += loss.item() * len(ids)
            count += len(ids)
        model.eval()
        # Fixed validation batches make early-stopping loss comparable across epochs.
        valid_total, valid_count = 0.0, 0
        with torch.inference_mode():
            for start in range(0, len(stop), config.batch_size):
                ids = stop[start:start + config.batch_size]
                if len(ids) >= 2:
                    valid_total += loss_for(ids).item() * len(ids)
                    valid_count += len(ids)
        stop_loss = valid_total / valid_count
        if not np.isfinite(stop_loss) or not np.isfinite(total):
            raise RuntimeError("Non-finite training loss")
        history.append({"epoch": epoch, "train_loss": total / count, "stop_loss": stop_loss})
        print(f"  {config.objective} epoch {epoch}: train={total/count:.5f}, stop={stop_loss:.5f}", flush=True)
        if stop_loss < best_loss:
            best_loss, best_epoch, stale = stop_loss, epoch, 0
            torch.save({"state_dict": model.state_dict(), "input_dim": x.shape[1],
                        "models": list(model_names), "config": asdict(config)}, directory / "model.pt")
        else:
            stale += 1
            if stale >= config.patience:
                break
    (directory / "training.json").write_text(json.dumps({"config": asdict(config),
        "models": list(model_names), "fit_indices": np.asarray(query_indices)[fit].tolist(),
        "stop_indices": np.asarray(query_indices)[stop].tolist(), "best_epoch": best_epoch,
        "history": history}, indent=2))
    return load_model(directory / "model.pt", config.device)


def load_model(path, device="cpu"):
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    cfg = checkpoint["config"]
    model = QueryEmbedding(checkpoint["input_dim"], len(checkpoint["models"]),
                           cfg["hidden_dim"], cfg["embedding_dim"]).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    return model.eval()


def make_fit(data, sentences, config, checkpoint_dir):
    """Factory for the harness: fit(train_models) -> embed(list[str]) -> ndarray.

    A held-out model's scores never enter training, early stopping, or the checkpoint key.
    The same fitted embedding is reused across probe budgets and probe draws.
    """
    fitted = {}

    def fit(train_models):
        names = tuple(train_models)
        if not names or len(set(names)) != len(names) or not set(names) <= set(data.models):
            raise ValueError("train_models must be a nonempty unique subset of data.models")
        if names not in fitted:
            cols = [data.models.index(m) for m in names]
            x = sentences.values[data.train]
            profiles = data.S[np.ix_(data.train, cols)].astype(np.float32)
            signature = hashlib.sha256(profiles.tobytes() + np.asarray(data.train).tobytes()).hexdigest()
            key = fingerprint({"features": sentences.key, "models": names,
                               "training": signature, "config": asdict(config)})
            directory = Path(checkpoint_dir) / key
            if (directory / "model.pt").exists() and (directory / "training.json").exists():
                model = load_model(directory / "model.pt", config.device)
            else:
                print(f"Training {config.objective} on {len(names)} models, seed {config.seed}", flush=True)
                model = train_embedding(x, profiles, data.train, names, config, directory)
            embedder = LearnedEmbedder(model, sentences, config)
            embedding_path = directory / "embeddings.npy"
            if embedding_path.exists():
                embedder.values = np.load(embedding_path)
            else:
                embedder.values = embedder(data.queries)
                np.save(embedding_path, embedder.values)
            fitted[names] = embedder
        return fitted[names]
    return fit
