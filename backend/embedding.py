"""
Gemini embedding utilities for the SHL Recommendation Engine.
Uses Google's text-embedding-004 model for both document and query embeddings.
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env from the project root (one level up from backend/)
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. "
        "Create a .env file in the project root with: GEMINI_API_KEY=your_key"
    )

genai.configure(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "models/gemini-embedding-001"


def get_doc_embedding(text: str) -> list[float]:
    """Generate an embedding for a document (assessment data)."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def get_query_embedding(text: str) -> list[float]:
    """Generate an embedding for a user query (job description)."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]