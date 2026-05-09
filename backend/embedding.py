"""
Embedding utilities for the SHL Recommendation Engine.
Uses BAAI/bge-large-en-v1.5 via sentence-transformers for local inference.
No API key required — model weights are downloaded and cached locally.
"""

from sentence_transformers import SentenceTransformer

# Load model once at module level (downloads ~1.3 GB on first run, cached after)
_MODEL_NAME = "BAAI/bge-large-en-v1.5"
_model = None

# BGE models use an instruction prefix for queries (not for documents)
_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model on first use."""
    global _model
    if _model is None:
        print(f"🔄 Loading embedding model: {_MODEL_NAME}...")
        _model = SentenceTransformer(_MODEL_NAME)
        print(f"✅ Model loaded (dim={_model.get_embedding_dimension()})")
    return _model


def get_doc_embedding(text: str) -> list[float]:
    """Generate an embedding for a document (assessment data)."""
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def get_query_embedding(text: str) -> list[float]:
    """Generate an embedding for a user query (job description)."""
    model = _get_model()
    # BGE models prepend an instruction for query embeddings
    embedding = model.encode(
        _QUERY_INSTRUCTION + text, normalize_embeddings=True
    )
    return embedding.tolist()