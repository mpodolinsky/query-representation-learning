"""MLP query embedding, with a training-only quality-profile prediction head."""
import torch
from torch import nn
from torch.nn import functional as F


class QueryEmbedding(nn.Module):
    def __init__(self, input_dim, n_models, hidden_dim=128, embedding_dim=64):
        super().__init__()
        self.projection = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(),
                                        nn.Linear(hidden_dim, embedding_dim))
        self.profile_head = nn.Linear(embedding_dim, n_models)

    def embed(self, x):
        return F.normalize(self.projection(x), dim=1)

    def forward(self, x):
        z = self.embed(x)
        return z, torch.sigmoid(self.profile_head(z))


def contrastive_loss(z, profiles, threshold=0.1, margin=1.0):
    """Pairs with mean squared profile difference <= threshold are positive.

    Use each unordered pair once; self-pairs are excluded. Average positive and negative
    losses separately so a large negative class cannot drown out the positives.
    """
    i, j = torch.triu_indices(len(z), len(z), offset=1, device=z.device)
    if len(i) == 0:
        return z.sum() * 0
    positive = ((profiles[i] - profiles[j]).square().mean(1) <= threshold)
    distance = torch.linalg.vector_norm(z[i] - z[j], dim=1)
    losses = []
    if positive.any():
        losses.append(distance[positive].square().mean())
    if (~positive).any():
        losses.append(F.relu(margin - distance[~positive]).square().mean())
    return torch.stack(losses).mean()
