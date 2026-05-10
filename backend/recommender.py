"""
Recommendation engine for SHL assessments.
Uses FAISS similarity search over BGE embeddings (BAAI/bge-large-en-v1.5).
"""

import numpy as np
from .embedding import get_query_embedding
from .db import create_index

# Lazy-loaded globals
_index = None
_df = None

# Minimum cosine similarity to include a result.
# Below this threshold, results are considered irrelevant.
MIN_SCORE_THRESHOLD = 0.40


def _ensure_loaded():
    """Initialize the FAISS index on first use (not at import time)."""
    global _index, _df
    if _index is None:
        _index, _df = create_index()


def recommend(query: str, top_k: int = 10) -> list[dict]:
    """
    Given a natural-language query (job description, role, etc.),
    return the top_k most relevant SHL assessments.
    Results below MIN_SCORE_THRESHOLD are filtered out.
    """
    _ensure_loaded()

    # Embed the user query
    query_emb = np.array([get_query_embedding(query)], dtype="float32")

    # L2-normalize to match the indexed document vectors
    norm = np.linalg.norm(query_emb, axis=1, keepdims=True)
    if norm > 0:
        query_emb = query_emb / norm

    # Search (request more than top_k since we filter by threshold)
    search_k = min(top_k * 2, _index.ntotal)  # type: ignore[union-attr]
    scores, indices = _index.search(query_emb, search_k)  # type: ignore[union-attr]

    # Build results — filter by threshold and limit to top_k
    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx == -1:
            continue
        if score < MIN_SCORE_THRESHOLD:
            continue
        if len(results) >= top_k:
            break

        row = _df.iloc[idx]  # type: ignore[union-attr]
        results.append({
            "rank": len(results) + 1,
            "name": row["name"],
            "url": row["url"],
            "remote_testing": row["remote_testing"],
            "adaptive_irt": row["adaptive_irt"],
            "test_types": row["test_types"],
            "score": round(float(score), 4),
        })

    return results