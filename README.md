# 🎯 SHL Assessment Recommendation Engine

An AI-powered recommendation system that suggests the most relevant SHL assessments based on natural-language job descriptions. Uses **semantic vector search** powered by Google Gemini embeddings and FAISS to match queries against SHL's 153-assessment product catalog.

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
                │  FAISS      │  │  Gemini           │
                │  Vector     │  │  Embedding API    │
                │  Index      │  │  (embedding-001)  │
                │  (data/)    │  │                   │
                └─────────────┘  └───────────────────┘
```

## How It Works

1. **Data Collection** — `scripts/scraper.py` scrapes SHL's [Product Catalog](https://www.shl.com/solutions/products/product-catalog/) using Playwright for browser automation
2. **Data Cleaning** — `scripts/clean_data.py` deduplicates and standardizes the raw data (177 → 153 unique assessments)
3. **Embedding Generation** — `backend/db.py` enriches each assessment with domain keywords, then generates 3072-dim vectors via Google Gemini (`gemini-embedding-001`)
4. **Vector Indexing** — Embeddings are L2-normalized and stored in a FAISS `IndexFlatIP` index for cosine similarity search
5. **Query Processing** — User queries are embedded in real-time and matched against the index, returning the top-K most relevant assessments
6. **Relevance Filtering** — Results below a minimum score threshold (0.40) are filtered out to prevent irrelevant matches

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------| 
| **API** | FastAPI + Uvicorn | REST API with auto-generated docs at `/docs` |
| **Frontend** | Next.js (React, App Router) | Dashboard UI with IBM Plex typography and dark theme |
| **Embeddings** | Google Gemini (`gemini-embedding-001`) | Semantic text-to-vector conversion |
| **Vector Search** | FAISS (`IndexFlatIP`) | Fast cosine similarity search over 153 assessments |
| **Data Processing** | Pandas, NumPy | CSV cleaning, vector normalization |
| **Scraping** | Playwright | SHL catalog data extraction with browser automation |

## Project Structure

```
shl_recommender/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── app.py                # FastAPI app — REST API endpoints
│   ├── db.py                 # Data loading, embedding generation, FAISS indexing
│   ├── embedding.py          # Gemini API wrapper for text embeddings
│   └── recommender.py        # Search logic with relevance threshold filtering
├── frontend/
│   ├── app/
│   │   ├── globals.css       # Design system (dark theme, custom properties)
│   │   ├── layout.js         # Root layout with IBM Plex + DM Serif fonts
│   │   └── page.js           # Main dashboard UI (search, results table)
│   ├── package.json          # Next.js + React dependencies
│   ├── next.config.mjs       # Next.js configuration
│   └── eslint.config.mjs     # Linting configuration
├── scripts/
│   ├── scraper.py            # SHL catalog web scraper (Playwright)
│   └── clean_data.py         # Data deduplication and cleaning
├── data/
│   ├── raw_data.csv          # Raw scraped data
│   ├── clean_data.csv        # Cleaned assessment catalog (153 entries)
│   ├── embeddings.npy        # Cached embedding vectors
│   └── embeddings.faiss      # FAISS index file
├── .env                      # API key (not committed)
├── .env.example              # Template for .env
├── .gitignore
├── requirements.txt          # Python dependencies
└── README.md
```

## Setup

### 1. Install Python dependencies

```bash
cd shl_recommender
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Configure API key

Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey), then:

```bash
cp .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

### 4. Start the backend API

```bash
cd shl_recommender
uvicorn backend.app:app --reload --port 8000
```

On first run, the server will generate embeddings for all 153 assessments (~2-3 minutes due to API rate limits). These are cached in `data/` for instant startup afterwards.

### 5. Start the frontend (in a separate terminal)

```bash
cd shl_recommender/frontend
npm run dev
```

### 6. Open the app

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

## Design Decisions

- **Domain Enrichment**: Assessment names are enriched with semantic category keywords before embedding (e.g., "Sales Manager" → "Sales, Business Development, Revenue...") to improve match quality for domain-specific queries
- **Cosine Similarity**: Vectors are L2-normalized and searched with `IndexFlatIP` (inner product = cosine similarity on unit vectors)
- **Score Threshold**: A minimum relevance threshold of 0.40 filters out poor matches, with a UI warning for low-confidence results
- **Exponential Backoff**: Rate-limit handling with retry logic for Gemini's free-tier API quotas (100 req/min)
- **Cached Embeddings**: Vectors are saved to disk (`.npy` + `.faiss`) so the server starts instantly after the first run
- **Separate Frontend**: The Next.js frontend runs independently from the FastAPI backend, communicating via REST API with CORS enabled
