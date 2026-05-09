"""
FastAPI application for the SHL Assessment Recommendation Engine.
Provides REST API endpoints for assessment recommendations.
The frontend is a separate Next.js app (see frontend/).
"""

import traceback
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .recommender import recommend

app = FastAPI(
    title="SHL Assessment Recommendation Engine",
    description="Recommends SHL assessments based on job descriptions or natural-language queries.",
    version="1.0.0",
)

# Allow cross-origin requests (needed if frontend is served separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Response Models ---

class Assessment(BaseModel):
    rank: int
    name: str
    url: str
    remote_testing: str
    adaptive_irt: str
    test_types: str
    score: float


class RecommendResponse(BaseModel):
    query: str
    count: int
    assessments: list[Assessment]


# --- Request Models ---

class RecommendRequest(BaseModel):
    query: str
    top_k: int = Field(10, ge=1, le=20, description="Number of results to return")


# --- Endpoints ---



@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/recommend", response_model=RecommendResponse)
def recommend_get(
    query: str = Query(..., description="Job description or natural-language query"),
    top_k: int = Query(10, ge=1, le=20, description="Number of results to return"),
):
    """Recommend SHL assessments based on a text query (GET)."""
    try:
        results = recommend(query, top_k=top_k)
        return RecommendResponse(query=query, count=len(results), assessments=results)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ Error in /recommend: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend", response_model=RecommendResponse)
def recommend_post(request: RecommendRequest):
    """Recommend SHL assessments based on a text query (POST)."""
    try:
        results = recommend(request.query, top_k=request.top_k)
        return RecommendResponse(
            query=request.query, count=len(results), assessments=results
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ Error in POST /recommend: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))