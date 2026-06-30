"""Question clustering with sklearn AgglomerativeClustering on normalized embeddings."""
from __future__ import annotations

import numpy as np
from sklearn.cluster import AgglomerativeClustering


def cluster_vectors(vectors: list[np.ndarray], distance_threshold: float = 0.35) -> list[int]:
    if len(vectors) < 2:
        return [0] * len(vectors)
    X = np.vstack(vectors)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1
    Xn = X / norms
    model = AgglomerativeClustering(
        n_clusters=None, distance_threshold=distance_threshold, metric="euclidean", linkage="average"
    )
    return [int(x) for x in model.fit_predict(Xn)]