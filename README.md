# 🎯 SHL Assessment Recommendation Engine

An AI-powered recommendation system that suggests the most relevant SHL assessments based on natural-language job descriptions. Uses **semantic vector search** powered by a locally-running **BAAI/bge-large-en-v1.5** embedding model and FAISS to match queries against SHL's 153-assessment product catalog.

> **No API keys required** — the embedding model runs entirely on your machine.

## Architecture

```
                    ┌─────────────────────────────┐
                    │    Frontend (Next.js)        │
                    │    React / App Router        │
                    │    localhost:3000             │
                    └──────────┬──────────────────┘
                               │ fetch(/recommend)
                    ┌──────────▼──────────────────┐
                    │    FastAPI Backend           │
                    │    REST API (backend/app.py) │
                    │    GET /recommend?query=...  │
                    │    POST /recommend           │
                    │    localhost:8000             │
                    └──────┬───────────┬──────────┘
                           │           │
                ┌──────────▼──┐  ┌─────▼────────────┐
                │  FAISS      │  │  BGE-Large        │
                │  Vector     │  │  (Local Model)    │
                │  Index      │  │  bge-large-en-v1.5│
                │  (data/)    │  │  1024-dim vectors │
                └─────────────┘  └───────────────────┘
```

## How It Works

1. **Data Collection** — `scripts/scraper.py` scrapes SHL's [Product Catalog](https://www.shl.com/solutions/products/product-catalog/) using Playwright for browser automation
2. **Data Cleaning** — `scripts/clean_data.py` deduplicates and standardizes the raw data (177 → 153 unique assessments)
3. **Embedding Generation** — `backend/db.py` enriches each assessment with domain keywords, then generates 1024-dim vectors via a locally-running **BAAI/bge-large-en-v1.5** model (sentence-transformers)
4. **Vector Indexing** — Embeddings are L2-normalized and stored in a FAISS `IndexFlatIP` index for cosine similarity search
5. **Query Processing** — User queries are embedded in real-time (with a BGE-specific instruction prefix for asymmetric retrieval) and matched against the index, returning the top-K most relevant assessments
6. **Relevance Filtering** — Results below a minimum score threshold (0.40) are filtered out to prevent irrelevant matches

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | FastAPI + Uvicorn | REST API with auto-generated docs at `/docs` |
| **Frontend** | Next.js (React, App Router) | Dashboard UI with IBM Plex typography and dark theme |
| **Embeddings** | BAAI/bge-large-en-v1.5 (sentence-transformers) | Local semantic text-to-vector conversion (1024-dim) |
| **Vector Search** | FAISS (`IndexFlatIP`) | Fast cosine similarity search over 153 assessments |
| **Data Processing** | Pandas, NumPy | CSV cleaning, vector normalization |
| **Scraping** | Playwright | SHL catalog data extraction with browser automation |
| **Containerization** | Docker, Docker Compose | Isolated, reproducible deployment |

## Project Structure

```
shl_recommender/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── app.py                # FastAPI app — REST API endpoints
│   ├── db.py                 # Data loading, embedding generation, FAISS indexing
│   ├── embedding.py          # BGE model wrapper (sentence-transformers, local inference)
│   ├── recommender.py        # Search logic with relevance threshold filtering
│   └── Dockerfile            # Backend container image
├── frontend/
│   ├── app/
│   │   ├── globals.css       # Design system (dark theme, custom properties)
│   │   ├── layout.js         # Root layout with IBM Plex + DM Serif fonts
│   │   └── page.js           # Main dashboard UI (search, results table)
│   ├── package.json          # Next.js + React dependencies
│   ├── next.config.mjs       # Next.js configuration
│   ├── eslint.config.mjs     # Linting configuration
│   └── Dockerfile            # Frontend container image
├── scripts/
│   ├── scraper.py            # SHL catalog web scraper (Playwright)
│   └── clean_data.py         # Data deduplication and cleaning
├── data/
│   ├── raw_data.csv          # Raw scraped data
│   ├── clean_data.csv        # Cleaned assessment catalog (153 entries)
│   ├── embeddings.npy        # Cached embedding vectors
│   └── embeddings.faiss      # FAISS index file
├── docker-compose.yml        # Multi-service orchestration
├── .dockerignore
├── .gitignore
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Quick Start with Docker Compose _(recommended)_

The easiest way to run the full stack in an isolated environment. No Python, Node, or model downloads needed on your host — everything is containerized.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

### Run

```bash
# Clone the repo
git clone <repo-url> && cd shl_recommender

# Build and start both services
docker compose up --build
```

> **First build takes ~5 minutes** — it downloads the BGE model (~1.3 GB) and installs all dependencies. Subsequent builds use cached layers and start in seconds.

### Access

| Service | URL |
|---------|-----|
| **Frontend UI** | [http://localhost:3000](http://localhost:3000) |
| **API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |

### Stop

```bash
docker compose down            # stop containers
docker compose down -v         # stop + remove model cache volume
```

---

## Local Development Setup

If you prefer running outside Docker for development.

### 1. Install Python dependencies

```bash
cd shl_recommender
pip install -r requirements.txt
```

> **Note:** The `sentence-transformers` package will download the BGE model (~1.3 GB) on first run. It's cached in `~/.cache/huggingface/` afterwards.

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Start the backend API

```bash
cd shl_recommender
uvicorn backend.app:app --reload --port 8000
```

On first run, the server will:
1. Download the `BAAI/bge-large-en-v1.5` model (~1.3 GB, cached after)
2. Generate embeddings for all 153 assessments (~30 seconds on CPU)

Embeddings are cached in `data/` for instant startup afterwards.

### 4. Start the frontend (in a separate terminal)

```bash
cd shl_recommender/frontend
npm run dev
```

### 5. Open the app

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Stopping the servers

Stop each server with `Ctrl + C` in their respective terminals, or kill them by port:

```bash
# Stop backend (port 8000)
kill $(lsof -ti :8000)

# Stop frontend (port 3000)
kill $(lsof -ti :3000)
```

---

## API Reference

### `GET /recommend`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | (required) | Job description or role requirement |
| `top_k` | int | 10 | Number of results (1–20) |

**Example:**
```bash
curl "http://localhost:8000/recommend?query=sales+manager&top_k=5"
```

**Response:**
```json
{
  "query": "sales manager",
  "count": 5,
  "assessments": [
    {
      "rank": 1,
      "name": "Sales Manager Solution",
      "url": "https://www.shl.com/...",
      "remote_testing": "Yes",
      "adaptive_irt": "Yes",
      "test_types": "Ability, Behavior, Personality",
      "score": 0.666
    }
  ]
}
```

### `POST /recommend`

Same as GET but accepts a JSON body:
```json
{ "query": "software engineer", "top_k": 10 }
```

---

## Design Decisions

- **Local Embeddings (BAAI/bge-large-en-v1.5)**: No API keys, no rate limits, no cost. The model runs locally via `sentence-transformers` producing 1024-dim vectors. BGE uses asymmetric retrieval — queries get an instruction prefix while documents don't
- **Domain Enrichment**: Assessment names are enriched with semantic category keywords before embedding (e.g., "Sales Manager" → "Sales, Business Development, Revenue...") to improve match quality for domain-specific queries
- **Cosine Similarity**: Vectors are L2-normalized and searched with `IndexFlatIP` (inner product = cosine similarity on unit vectors)
- **Score Threshold**: A minimum relevance threshold of 0.40 filters out poor matches, with a UI warning for low-confidence results
- **Cached Embeddings**: Vectors are saved to disk (`.npy` + `.faiss`) so the server starts instantly after the first run
- **Separate Frontend**: The Next.js frontend runs independently from the FastAPI backend, communicating via REST API with CORS enabled
- **Docker Compose**: Both services are containerized for reproducible, isolated deployment. The BGE model is baked into the backend image, and a named volume caches it across rebuilds
