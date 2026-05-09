"use client";

import { useState, useRef } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EXAMPLES = [
  "sales manager",
  "customer service rep",
  ".NET software developer",
  "nurse leader",
  "bank operations supervisor",
  "retail store manager",
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleSearch() {
    const q = query.trim();
    if (!q) {
      inputRef.current?.focus();
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch(
        `${API_URL}/recommend?query=${encodeURIComponent(q)}&top_k=10`
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || res.statusText);
      }
      const data = await res.json();
      setResults(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSearch();
  }

  function fillQuery(text) {
    setQuery(text);
    inputRef.current?.focus();
  }

  const assessments = results?.assessments || [];
  const topScore = assessments[0]?.score || 0;

  return (
    <div className="container">
      {/* ── Header ── */}
      <header>
        <div className="brand">
          <span className="brand-name" style={{ fontFamily: "var(--font-serif)" }}>
            SHL
          </span>
          <div className="brand-dots">
            <span />
            <span />
            <span />
          </div>
        </div>
        <p className="tagline">
          Find the right assessments for any role. Enter a{" "}
          <strong>job description</strong> and get AI-ranked recommendations from
          SHL&apos;s product catalog.
        </p>
        <nav>
          <button className="active">Recommender</button>
          <a
            href="https://www.shl.com/solutions/products/product-catalog/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Catalog ↗
          </a>
          <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer">
            API Docs ↗
          </a>
        </nav>
      </header>

      {/* ── Search ── */}
      <section className="search-section">
        <div className="search-label">Query</div>
        <div className="search-row">
          <input
            ref={inputRef}
            className="search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Mid-level sales manager with team leadership experience…"
          />
          <button
            className="search-btn"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "Searching…" : "Recommend"}
          </button>
        </div>
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <span key={ex} className="chip" onClick={() => fillQuery(ex)}>
              {ex}
            </span>
          ))}
        </div>
      </section>

      {/* ── Loading ── */}
      {loading && (
        <div className="status">
          <span className="spinner" />
          Analyzing query and searching 153 assessments…
        </div>
      )}

      {/* ── Error ── */}
      {error && (
        <div className="status" style={{ color: "var(--coral)" }}>
          Error: {error}
        </div>
      )}

      {/* ── Results ── */}
      {results && assessments.length === 0 && (
        <div className="status">
          🔍 No matching assessments found. Try a broader query.
        </div>
      )}

      {assessments.length > 0 && (
        <>
          {topScore < 0.6 && (
            <div className="status-note">
              💡 The SHL catalog may not have assessments for this specific
              domain. Showing closest matches.
            </div>
          )}

          <div className="results-header">
            <span
              className="results-title"
              style={{ fontFamily: "var(--font-serif)" }}
            >
              Recommendations
            </span>
            <span className="results-count">
              {assessments.length} results
            </span>
          </div>

          <table className="results-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Assessment</th>
                <th>Test Types</th>
                <th>Remote</th>
                <th>Adaptive</th>
                <th style={{ textAlign: "right" }}>Relevance</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((a, i) => {
                const pct = Math.max(0, Math.min(100, a.score * 100));
                const rankClass =
                  i === 0
                    ? "rank-1"
                    : i === 1
                    ? "rank-2"
                    : i === 2
                    ? "rank-3"
                    : "rank-n";
                const scoreClass =
                  pct >= 65 ? "hi" : pct >= 55 ? "md" : "lo";

                return (
                  <tr
                    key={a.rank}
                    style={{ animationDelay: `${i * 0.04}s` }}
                  >
                    <td className={`rank ${rankClass}`}>
                      {String(a.rank).padStart(2, "0")}
                    </td>
                    <td className="name-cell">
                      <a
                        href={a.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="name-link"
                      >
                        {a.name} ↗
                      </a>
                    </td>
                    <td>
                      <div className="types">
                        {a.test_types.split(", ").map((t) => (
                          <span key={t} className="type-pill">
                            {t.trim()}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="feat">
                        <span
                          className={`dot ${
                            a.remote_testing === "Yes"
                              ? "dot-yes"
                              : "dot-no"
                          }`}
                        />
                        <span className="dot-label">
                          {a.remote_testing === "Yes" ? "Remote" : "—"}
                        </span>
                      </div>
                    </td>
                    <td>
                      <div className="feat">
                        <span
                          className={`dot ${
                            a.adaptive_irt === "Yes"
                              ? "dot-yes"
                              : "dot-no"
                          }`}
                        />
                        <span className="dot-label">
                          {a.adaptive_irt === "Yes" ? "Adaptive" : "—"}
                        </span>
                      </div>
                    </td>
                    <td className="score-cell">
                      <div className="score-bar-wrap">
                        <div className="score-track">
                          <div
                            className={`score-fill sf-${scoreClass}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className={`score-num sn-${scoreClass}`}>
                          {pct.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}

      {/* ── Footer ── */}
      <footer>
        Built with · FastAPI · Uvicorn · Pandas · Numpy · FAISS · Playwright · BGE Embeddings&emsp;·&emsp;Data from{" "}
        <a
          href="https://www.shl.com/solutions/products/product-catalog/"
          target="_blank"
          rel="noopener noreferrer"
        >
          SHL Product Catalog
        </a>
      </footer>
    </div>
  );
}
