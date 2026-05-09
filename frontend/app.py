"""
SHL Assessment Recommendation Engine — Premium Dashboard UI
Design: SHL brand colors + dark dashboard glassmorphism
"""
import streamlit as st
import requests

st.set_page_config(page_title="SHL Assessment Recommender", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ── Full CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root ── */
:root {
    --shl-navy: #0a1628;
    --shl-dark: #0d1b2a;
    --shl-card: rgba(13, 27, 42, 0.85);
    --shl-blue: #1b98e0;
    --shl-blue-bright: #29b6f6;
    --shl-green: #4caf50;
    --shl-green-light: #66bb6a;
    --shl-border: rgba(27, 152, 224, 0.15);
    --shl-glow: rgba(27, 152, 224, 0.35);
    --text-primary: #e8edf3;
    --text-secondary: #8fa3bf;
    --text-muted: #5a7394;
}

.stApp {
    background: linear-gradient(145deg, #060e1a 0%, #0a1628 40%, #0d1b2a 100%) !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081220 0%, #0a1628 50%, #081220 100%) !important;
    border-right: 1px solid var(--shl-border) !important;
}
section[data-testid="stSidebar"] .stMarkdown h3 { color: var(--text-primary) !important; font-weight: 600 !important; font-size: 0.92rem !important; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stMarkdown li { color: var(--text-secondary) !important; font-size: 0.84rem !important; }
section[data-testid="stSidebar"] hr { border-color: var(--shl-border) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(27, 152, 224, 0.06) !important; border: 1px solid var(--shl-border) !important;
    color: var(--text-secondary) !important; border-radius: 10px !important; padding: 10px 14px !important;
    font-size: 0.82rem !important; text-align: left !important; transition: all 0.25s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(27, 152, 224, 0.12) !important; border-color: var(--shl-glow) !important;
    color: var(--shl-blue-bright) !important; transform: translateX(3px);
}
.stSlider > div > div > div > div { background: var(--shl-blue) !important; }
.stSlider label { color: var(--text-secondary) !important; }

/* ── Main ── */
.block-container { padding-top: 1.5rem !important; max-width: 960px !important; }

/* ── Text Area ── */
.stTextArea textarea {
    background: var(--shl-dark) !important; border: 1px solid var(--shl-border) !important;
    border-radius: 12px !important; color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.92rem !important; padding: 14px 18px !important;
    transition: all 0.25s ease !important;
}
.stTextArea textarea:focus { border-color: var(--shl-blue) !important; box-shadow: 0 0 0 3px rgba(27,152,224,0.12) !important; }
.stTextArea textarea::placeholder { color: var(--text-muted) !important; }
.stTextArea label { color: var(--text-secondary) !important; font-weight: 500 !important; }

/* ── Primary Button ── */
.stButton > button[kind="primary"],
div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
    background: linear-gradient(135deg, #1b98e0 0%, #1565c0 100%) !important;
    border: none !important; border-radius: 10px !important; color: #fff !important;
    font-weight: 600 !important; font-size: 0.92rem !important; padding: 11px 24px !important;
    box-shadow: 0 4px 16px rgba(27,152,224,0.25) !important; transition: all 0.25s ease !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 28px rgba(27,152,224,0.35) !important; }

/* ── Alerts ── */
.stAlert, div[data-testid="stNotification"] { border-radius: 10px !important; }

/* ── Hero ── */
.hero { text-align: center; padding: 12px 0 4px; }
.hero-brand { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 6px; }
.hero-shl { font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 800; color: #fff; letter-spacing: -0.03em; }
.hero-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.hero-tagline { font-size: 1.05rem; color: var(--text-secondary); margin-top: 4px; font-weight: 400; }
.hero-tagline strong { color: var(--shl-blue-bright); font-weight: 600; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, var(--shl-glow), transparent); margin: 18px 0; }

/* ── Results ── */
.results-bar { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.results-title { font-size: 1.15rem; font-weight: 700; color: var(--text-primary); }
.results-pill { background: rgba(27,152,224,0.12); color: var(--shl-blue-bright); padding: 4px 14px; border-radius: 20px; font-size: 0.76rem; font-weight: 600; }

/* ── Assessment Card ── */
.a-card {
    background: linear-gradient(135deg, rgba(13,27,42,0.9) 0%, rgba(20,35,55,0.7) 100%);
    border: 1px solid var(--shl-border); border-radius: 14px; padding: 20px 22px;
    margin-bottom: 12px; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden;
}
.a-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--shl-blue), var(--shl-green), transparent);
    opacity: 0; transition: opacity 0.3s ease;
}
.a-card:hover { border-color: var(--shl-glow); transform: translateY(-2px); box-shadow: 0 10px 36px rgba(27,152,224,0.1); }
.a-card:hover::before { opacity: 1; }

.card-row { display: flex; align-items: flex-start; gap: 14px; }
.card-body { flex: 1; min-width: 0; }
.card-link { font-size: 1.02rem; font-weight: 600; color: var(--shl-blue-bright); text-decoration: none; transition: color 0.2s; }
.card-link:hover { color: #80d8ff; text-decoration: underline; text-underline-offset: 3px; }

/* Badges */
.badges { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.b { display: inline-flex; align-items: center; gap: 3px; padding: 3px 10px; border-radius: 16px; font-size: 0.72rem; font-weight: 600; }
.b-ry { background: rgba(76,175,80,0.1); color: #66bb6a; border: 1px solid rgba(76,175,80,0.2); }
.b-rn { background: rgba(239,83,80,0.07); color: #ef5350; border: 1px solid rgba(239,83,80,0.15); }
.b-ay { background: rgba(27,152,224,0.1); color: var(--shl-blue-bright); border: 1px solid rgba(27,152,224,0.2); }
.b-an { background: rgba(239,83,80,0.07); color: #ef5350; border: 1px solid rgba(239,83,80,0.15); }
.b-t { background: rgba(255,255,255,0.04); color: var(--text-secondary); border: 1px solid rgba(255,255,255,0.08); }

/* Score */
.score-row { display: flex; align-items: center; gap: 10px; margin-top: 12px; }
.score-lbl { font-size: 0.76rem; color: var(--text-muted); min-width: 60px; }
.score-track { flex: 1; height: 4px; background: rgba(255,255,255,0.04); border-radius: 3px; overflow: hidden; }
.score-fill { height: 100%; border-radius: 3px; }
.sf-hi { background: linear-gradient(90deg, #4caf50, #66bb6a); box-shadow: 0 0 8px rgba(76,175,80,0.3); }
.sf-md { background: linear-gradient(90deg, #1b98e0, #29b6f6); box-shadow: 0 0 8px rgba(27,152,224,0.3); }
.sf-lo { background: linear-gradient(90deg, #ff9800, #ffb74d); box-shadow: 0 0 8px rgba(255,152,0,0.2); }
.score-val { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 600; min-width: 48px; text-align: right; }
.sv-hi { color: #66bb6a; } .sv-md { color: #29b6f6; } .sv-lo { color: #ffb74d; }

/* Rank */
.rank-circle {
    width: 36px; height: 36px; min-width: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace;
}
.rk-def { background: rgba(27,152,224,0.12); color: var(--shl-blue-bright); border: 1px solid rgba(27,152,224,0.2); }

/* Footer */
.app-ft { text-align: center; padding: 28px 0 12px; color: var(--text-muted); font-size: 0.73rem; }
.app-ft a { color: var(--shl-blue-bright); text-decoration: none; }

/* Dot pattern (SHL style) */
.dots { position: fixed; top: 0; right: 0; width: 300px; height: 300px; opacity: 0.03; pointer-events: none;
    background-image: radial-gradient(circle, #1b98e0 1px, transparent 1px); background-size: 24px 24px; }
</style>
<div class="dots"></div>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

# ── Sidebar ──
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_k = st.slider("Number of results", min_value=1, max_value=20, value=10)
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    st.markdown("<p style='color:#5a7394;font-size:0.8rem;margin-bottom:10px;'>Click to try instantly</p>", unsafe_allow_html=True)
    examples = [
        "I need a test for a mid-level sales manager role",
        "Looking for assessments for entry-level customer service representatives",
        "Need cognitive ability and personality tests for a bank operations supervisor",
        "Hiring software engineers — need .NET and coding knowledge tests",
        "Assessment for healthcare nursing roles with remote testing support",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state["query_input"] = ex
    st.markdown("---")
    st.markdown("<p style='color:#3a5575;font-size:0.72rem;text-align:center;'>Powered by Gemini Embeddings & FAISS</p>", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-brand">
        <span class="hero-shl">SHL</span>
        <span class="hero-dot" style="background:#1b98e0;"></span>
        <span class="hero-dot" style="background:#4caf50;"></span>
        <span class="hero-dot" style="background:#1565c0;"></span>
    </div>
    <div style="font-family:'Inter',sans-serif;font-size:1.6rem;font-weight:700;color:#e8edf3;margin:4px 0;">
        Assessment Recommender
    </div>
    <p class="hero-tagline">
        Enter a <strong>job description</strong> or <strong>role requirement</strong> to discover the most relevant assessments.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Search ──
query = st.text_area(
    "📝 Job Description / Query",
    value=st.session_state.get("query_input", ""),
    height=110,
    placeholder="e.g. I need a personality and cognitive ability test for a retail store manager who will lead a team of 15 people...",
)
col1, col2 = st.columns([2, 4])
with col1:
    search_clicked = st.button("🔍  Recommend Assessments", type="primary", use_container_width=True)

# ── Results ──
if search_clicked and query.strip():
    with st.spinner("✨ Analyzing query and finding best matches..."):
        try:
            resp = requests.get(f"{API_URL}/recommend", params={"query": query, "top_k": top_k}, timeout=300)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Start it with: `uvicorn backend.app:app --reload --port 8000`")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()

    items = data.get("assessments", [])
    if not items:
        st.markdown('<div style="text-align:center;padding:40px;color:#5a7394;"><div style="font-size:2.5rem;margin-bottom:10px;">🔍</div>No matching assessments found. Try a broader query.</div>', unsafe_allow_html=True)
    else:
        top_score = items[0]["score"] if items else 0
        if top_score < 0.60:
            st.info("💡 **Note:** The SHL catalog may not have assessments for this specific domain. Showing closest matches. Try a broader job description.")

        st.markdown(f'<div class="divider"></div><div class="results-bar"><span class="results-title">Results</span><span class="results-pill">{len(items)} found</span></div>', unsafe_allow_html=True)

        for a in items:
            rank, score = a["rank"], a["score"]
            pct = max(0, min(100, score * 100))

            # Rank
            if rank <= 3:
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                rk = f'<span style="font-size:1.7rem;line-height:1;">{medals[rank]}</span>'
            else:
                rk = f'<div class="rank-circle rk-def">{rank}</div>'

            # Score classes
            if pct >= 65:   sfc, svc = "sf-hi", "sv-hi"
            elif pct >= 55: sfc, svc = "sf-md", "sv-md"
            else:           sfc, svc = "sf-lo", "sv-lo"

            # Badges
            rb = '<span class="b b-ry">✓ Remote</span>' if a["remote_testing"] == "Yes" else '<span class="b b-rn">✗ Remote</span>'
            ab = '<span class="b b-ay">✓ Adaptive</span>' if a["adaptive_irt"] == "Yes" else '<span class="b b-an">✗ Adaptive</span>'
            tb = "".join(f'<span class="b b-t">{t.strip()}</span>' for t in a["test_types"].split(", ") if t.strip())

            st.markdown(f"""
            <div class="a-card">
                <div class="card-row">
                    {rk}
                    <div class="card-body">
                        <a href="{a['url']}" target="_blank" class="card-link">{a['name']} ↗</a>
                        <div class="badges">{rb}{ab}{tb}</div>
                        <div class="score-row">
                            <span class="score-lbl">Relevance</span>
                            <div class="score-track"><div class="score-fill {sfc}" style="width:{pct}%;"></div></div>
                            <span class="score-val {svc}">{pct:.1f}%</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="app-ft">
            Built with FastAPI · Streamlit · FAISS · Gemini Embeddings<br/>
            Data from <a href="https://www.shl.com/solutions/products/product-catalog/" target="_blank">SHL Product Catalog</a>
        </div>
        """, unsafe_allow_html=True)

elif search_clicked:
    st.warning("⚠️ Please enter a query to get recommendations.")