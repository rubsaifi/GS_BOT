"""
RAG Engine with token optimization and caching for multi-user Streamlit deployment.
"""
import pandas as pd
import numpy as np
import faiss
import hashlib
import streamlit as st
from functools import lru_cache
from typing import Optional, Dict, Tuple, List

# ── Role to file mapping ──────────────────────────────────
ROLE_FILES = {
    "SR_BSOM": {
        "goal_sheet": "utils/SrBSOM_Goal_Sheet.xlsx",
        "parameter": "utils/SrBSOM_Parameter.xlsx"
    },
    "BSOM": {
        "goal_sheet": "utils/BSOM_Goal_Sheet.xlsx",
        "parameter": "utils/BSOM_PARAMETER.xlsx"
    },
    "ABSOM_TSE": {
        "goal_sheet": "utils/ABSOM_TSE_GS.xlsx",
        "parameter": "utils/ABSOM_TSE_Parameter.xlsx"
    }
}

# ── Lazy model loading ─────────────────────────────────────
_model = None

def get_model():
    """Lazy load SentenceTransformer model with caching."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


@st.cache_data(ttl=3600, show_spinner=False)
def load_data(role: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load goal sheet + parameter for the selected role.
    Cached for 1 hour to reduce memory/token usage across users.
    """
    files = ROLE_FILES[role]

    # Read only necessary columns to reduce memory
    kpi_df = pd.read_excel(files["goal_sheet"])
    scoring_raw = pd.read_excel(files["parameter"], header=None)

    # Token-efficient text: compact format
    kpi_df["text"] = kpi_df.fillna("").astype(str).apply(
        lambda row: " | ".join(filter(None, [str(v).strip() for v in row.values if v])),
        axis=1
    )

    scoring_df = build_scoring_chunks(scoring_raw)

    return kpi_df, scoring_df


def build_scoring_chunks(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw Excel rows into compact, token-efficient chunks.
    Optimized for RAG: minimal tokens, maximum information density.
    """
    chunks = []
    current_section = ""
    current_headers = []
    buffer_rows = []

    for _, row in raw_df.iterrows():
        row_vals = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip() not in ("", "nan")]

        if not row_vals:
            if current_section and buffer_rows:
                chunks.append(_build_compact_chunk(current_section, current_headers, buffer_rows))
                buffer_rows = []
            continue

        row_text = " | ".join(row_vals)

        # Section header detection
        if len(row_vals) <= 3 and any(kw in row_text.lower() for kw in [
            "slab", "parameter", "score", "dispatch", "amendment",
            "funding", "npc", "received", "discrepancy", "overall",
            "target", "incentive", "penalty", "quality", "productivity"
        ]):
            if current_section and buffer_rows:
                chunks.append(_build_compact_chunk(current_section, current_headers, buffer_rows))
                buffer_rows = []
                current_headers = []
            current_section = row_text
            continue

        # Column headers
        if "number of forms" in row_text.lower() or any(kw in row_text for kw in ["1 -", "1-<", "31 -", ">="]):
            current_headers = row_vals
            continue

        # Notes
        if row_text.startswith("*"):
            if current_section:
                chunks.append(f"{current_section}: {row_text}")
            continue

        if current_section:
            buffer_rows.append(row_vals)

    # Flush remaining
    if current_section and buffer_rows:
        chunks.append(_build_compact_chunk(current_section, current_headers, buffer_rows))

    return pd.DataFrame({"text": chunks})


def _build_compact_chunk(section: str, headers: List[str], rows: List[List[str]]) -> str:
    """Build token-efficient chunk: compact format without verbose labels."""
    lines = [section]

    for row in rows:
        if headers and len(row) == len(headers):
            # Compact key:value pairs
            pairs = ", ".join(f"{h}:{r}" for h, r in zip(headers, row))
            lines.append(pairs)
        else:
            lines.append(" | ".join(row))

    return "; ".join(lines)


@st.cache_resource(show_spinner=False)
def create_vector_db(role: str) -> Tuple[Optional[faiss.Index], pd.DataFrame]:
    """
    Create and cache vector DB for a role.
    Cached as a resource to share across sessions.
    """
    kpi_df, scoring_df = load_data(role)

    # Combine dataframes
    combined_df = pd.concat([
        kpi_df[["text"]],
        scoring_df
    ], ignore_index=True)

    # Remove duplicates to save tokens
    combined_df = combined_df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    if combined_df.empty:
        return None, combined_df

    model = get_model()

    # Batch encode with smaller batches to manage memory
    texts = combined_df["text"].tolist()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    # Normalize embeddings for cosine similarity (more efficient search)
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product = cosine for normalized vectors
    index.add(embeddings)

    return index, combined_df


@st.cache_data(ttl=300, show_spinner=False)
def search_cached(query: str, role: str, top_k: int = 5) -> List[str]:
    """
    Cached search results for identical queries.
    TTL=5min to balance freshness with token savings.
    """
    index, df = create_vector_db(role)

    if index is None or df.empty:
        return []

    model = get_model()
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    # Search
    scores, indices = index.search(np.array(query_embedding), top_k * 2)

    # Get semantic results
    semantic_results = []
    for idx in indices[0]:
        if 0 <= idx < len(df):
            semantic_results.append(df.iloc[idx]["text"])

    # Keyword fallback (on cached subset for efficiency)
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    if keywords:
        mask = df["text"].str.lower().str.contains("|".join(keywords), na=False, regex=True)
        keyword_results = df[mask]["text"].tolist()[:top_k]
    else:
        keyword_results = []

    # Merge and deduplicate while preserving order
    seen = set()
    combined = []
    for text in semantic_results + keyword_results:
        if text not in seen:
            combined.append(text)
            seen.add(text)
        if len(combined) >= top_k:
            break

    return combined[:top_k]


def search(query: str, role: str, top_k: int = 5) -> List[str]:
    """Public search interface with caching."""
    # Normalize query for better cache hits
    normalized_query = " ".join(query.lower().split())
    return search_cached(normalized_query, role, top_k)


# ── Session state helpers for Streamlit ─────────────────────
def get_cached_result(key: str, compute_func, *args, **kwargs):
    """Session-level cache for user-specific computations."""
    cache_key = f"cache_{key}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = compute_func(*args, **kwargs)
    return st.session_state[cache_key]


def clear_role_cache(role: str):
    """Clear cache when switching roles."""
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("cache_")]
    for k in keys_to_clear:
        del st.session_state[k]
    # Clear Streamlit cache for this role
    create_vector_db.clear()
