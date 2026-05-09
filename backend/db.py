"""
FAISS index management for the SHL Recommendation Engine.
Builds and caches a vector index from assessment data + Gemini embeddings.
"""

import pandas as pd
import numpy as np
import faiss
import os
import re
from .embedding import get_doc_embedding

# Paths relative to the project root
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")

CLEAN_CSV_PATH = os.path.join(DATA_DIR, "clean_data.csv")
EMBEDDING_PATH = os.path.join(DATA_DIR, "embeddings.npy")
INDEX_PATH = os.path.join(DATA_DIR, "embeddings.faiss")

# ──────────────────────────────────────────────────────────────
# Domain enrichment: map name patterns to descriptive keywords
# so that the embedding captures *what the assessment is about*
# rather than just the assessment product name.
# ──────────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    # Technology / Engineering
    r"\.NET|ADO|MVC|MVVM|WCF|WPF|XAML": (
        "software development, programming, .NET technology, coding, "
        "computer science, IT engineering, software engineering"
    ),
    r"Network Engineer|Network Analyst": (
        "networking, IT infrastructure, systems administration, "
        "network security, TCP/IP, cloud computing"
    ),
    r"Technology Professional": (
        "IT, software engineering, technology, programming, "
        "computer science, data analysis, systems design"
    ),
    r"Sales Engineer": (
        "technical sales, presales engineering, solution architecture, "
        "client demos, technology consulting"
    ),
    r"Technician|Technologist": (
        "technical skills, equipment maintenance, lab work, "
        "applied science, technical operations"
    ),

    # Sales
    r"Sales Manager|Sales Director|Sales Supervisor": (
        "sales leadership, revenue management, team management, "
        "B2B sales, pipeline management, CRM"
    ),
    r"Sales Rep|Sales Associate|Sales Professional|Sales Support": (
        "direct sales, customer acquisition, retail sales, "
        "lead generation, account development"
    ),

    # Customer Service / Contact Center
    r"Customer Service|Contact Cent|Call Center": (
        "customer support, call handling, complaint resolution, "
        "CRM, service quality, phone support"
    ),
    r"Cashier|Teller": (
        "cash handling, point of sale, transaction processing, "
        "customer interaction, financial transactions"
    ),

    # Management / Leadership
    r"Director|Executive": (
        "executive leadership, strategic planning, C-suite, "
        "organizational management, board-level decisions"
    ),
    r"Manager\b(?!.*Sales)(?!.*Restaurant)(?!.*Store)(?!.*Hospitality)": (
        "people management, team leadership, project management, "
        "operational oversight, performance reviews"
    ),
    r"Supervisor|Team Lead|Coach": (
        "team supervision, shift management, frontline leadership, "
        "staff scheduling, performance monitoring"
    ),

    # Finance / Accounting
    r"Accounts Payable|Accounts Receivable|Bookkeeping|Accounting|Auditing": (
        "finance, accounting, bookkeeping, invoicing, financial reporting, "
        "AP/AR, general ledger, audit"
    ),
    r"Financial|Banker|Banking|Branch Manager": (
        "financial services, banking, loans, investment, "
        "client advisory, financial planning"
    ),

    # Healthcare
    r"Nurse|Nursing|Healthcare|Health Aide|Telenurse": (
        "healthcare, nursing, patient care, medical, clinical, "
        "hospital, health services"
    ),

    # Hospitality / Food Service
    r"Restaurant|Cook|Server\b|Host\b|Hospitality|Guest Service|Front Desk": (
        "hospitality, food service, restaurant operations, "
        "guest experience, food safety"
    ),

    # Insurance
    r"Insurance": (
        "insurance, underwriting, claims processing, risk assessment, "
        "policy management, actuarial"
    ),

    # Retail
    r"Retail|Store Manager|Stock Clerk": (
        "retail operations, merchandise, inventory management, "
        "store operations, visual merchandising"
    ),

    # Industrial / Manufacturing
    r"Industrial|Manufacturing|Workplace Safety": (
        "manufacturing, warehouse, industrial operations, "
        "workplace safety, OSHA, production line"
    ),

    # Entry Level / Graduate
    r"Entry Level|Apprentice|Graduate": (
        "entry-level hiring, campus recruitment, graduate assessment, "
        "early career, trainee evaluation"
    ),

    # General Professional
    r"Professional.*Individual|Administrative Professional|Project Manager": (
        "professional skills, office work, project management, "
        "administrative tasks, business operations"
    ),

    # Data
    r"Data Entry": (
        "data entry, typing speed, data processing, "
        "keyboard skills, accuracy, clerical"
    ),

    # Gaming
    r"Gaming": (
        "casino operations, gaming industry, dealer, "
        "gaming compliance, table games"
    ),

    # Global / Development
    r"Global Skills Development": (
        "leadership development, skills assessment, talent development, "
        "360 feedback, competency framework, coaching"
    ),
}

# Test type full descriptions for richer context
TEST_TYPE_DESCRIPTIONS = {
    "Ability": "cognitive ability, reasoning, problem-solving, numerical, verbal",
    "Behavior": "behavioral assessment, personality traits, work style, cultural fit",
    "Competency": "competency-based evaluation, job competencies, performance prediction",
    "Knowledge": "job knowledge test, technical knowledge, domain expertise",
    "Personality": "personality profiling, Big Five traits, work preferences, motivation",
    "Simulation": "work simulation, situational judgment, realistic job preview",
    "Development": "development feedback, growth areas, coaching recommendations",
    "Experience": "experience evaluation, background assessment, career history",
}


def _infer_domain(name: str) -> str:
    """Match the assessment name against domain patterns to add rich context."""
    domains = []
    for pattern, keywords in DOMAIN_KEYWORDS.items():
        if re.search(pattern, name, re.IGNORECASE):
            domains.append(keywords)
    return "; ".join(domains) if domains else ""


def _expand_test_types(test_types_str: str) -> str:
    """Expand 'Ability, Behavior' → 'cognitive ability, reasoning... behavioral assessment...'"""
    if not test_types_str:
        return ""
    expanded = []
    for t in test_types_str.split(", "):
        t = t.strip()
        if t in TEST_TYPE_DESCRIPTIONS:
            expanded.append(TEST_TYPE_DESCRIPTIONS[t])
    return "; ".join(expanded)


def _build_embedding_text(row: pd.Series) -> str:
    """
    Build a rich, semantically-meaningful string for embedding.
    Combines assessment name, inferred domain, and expanded test types.
    Excludes noisy metadata (remote, adaptive) that dilutes semantic signal.
    """
    name = row.get("name", "")
    test_types = row.get("test_types", "")

    parts = [
        f"Assessment: {name}",
        f"Measures: {test_types}",
    ]

    # Add expanded test type descriptions
    expanded = _expand_test_types(test_types)
    if expanded:
        parts.append(f"Skills tested: {expanded}")

    # Add domain-inferred keywords
    domain = _infer_domain(name)
    if domain:
        parts.append(f"Domain: {domain}")

    return " | ".join(parts)


def create_index():
    """
    Build (or load cached) FAISS index and return (index, dataframe).
    Uses cosine similarity via inner product on L2-normalized vectors.
    """
    # Load the cleaned assessment data
    if not os.path.exists(CLEAN_CSV_PATH):
        raise FileNotFoundError(
            f"Clean data not found at {CLEAN_CSV_PATH}. "
            "Run 'python scripts/clean_data.py' first."
        )

    df = pd.read_csv(CLEAN_CSV_PATH)
    if df.empty:
        raise ValueError(f"Clean data at {CLEAN_CSV_PATH} is empty.")

    # Generate or load embeddings
    if os.path.exists(EMBEDDING_PATH):
        print("📦 Loading cached embeddings...")
        embeddings = np.load(EMBEDDING_PATH)

        # Regenerate if row count changed
        if embeddings.shape[0] != len(df):
            print("⚠️  Row count mismatch — regenerating embeddings...")
            embeddings = _generate_embeddings(df)
    else:
        embeddings = _generate_embeddings(df)

    # L2-normalize for cosine similarity via inner product
    faiss.normalize_L2(embeddings)

    # Build FAISS index (inner product = cosine sim on normalized vectors)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Cache the FAISS index
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index built with {index.ntotal} vectors (dim={dim})")

    return index, df


def _generate_embeddings(df: pd.DataFrame) -> np.ndarray:
    """Generate embeddings for all assessment rows with rate-limit handling."""
    import time

    print(f"🔄 Generating embeddings for {len(df)} assessments...")
    embeddings = []

    # Check for partial progress
    partial_path = EMBEDDING_PATH + ".partial.npy"
    start_idx = 0
    if os.path.exists(partial_path):
        partial = np.load(partial_path)
        embeddings = list(partial)
        start_idx = len(embeddings)
        print(f"📎 Resuming from checkpoint at index {start_idx}...")

    for i in range(start_idx, len(df)):
        row = df.iloc[i]
        text = _build_embedding_text(row)

        # Retry with exponential backoff on rate limit errors
        for attempt in range(5):
            try:
                emb = get_doc_embedding(text)
                embeddings.append(emb)
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait = 2 ** attempt * 5  # 5s, 10s, 20s, 40s, 80s
                    print(f"   ⏳ Rate limited — waiting {wait}s (attempt {attempt + 1}/5)...")
                    time.sleep(wait)
                else:
                    raise

        # Progress update
        if (i + 1) % 20 == 0:
            print(f"   Embedded {i + 1}/{len(df)}...")
            # Save partial progress every 20 items
            np.save(partial_path, np.array(embeddings, dtype="float32"))

        # Small delay to stay under 100 req/min limit
        time.sleep(0.7)

    arr = np.array(embeddings, dtype="float32")
    np.save(EMBEDDING_PATH, arr)

    # Clean up partial file
    if os.path.exists(partial_path):
        os.remove(partial_path)

    print(f"💾 Embeddings saved to {EMBEDDING_PATH}")
    return arr