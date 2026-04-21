# import pandas as pd
# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np

# model = SentenceTransformer("all-MiniLM-L6-v2")

# def load_data():
#     kpi_df = pd.read_excel("utils/SrBSOM_Goal_Sheet.xlsx")

#     # ── Read Parameter sheet — preserve all rows including headers ──
#     scoring_df = pd.read_excel(
#         "utils/SrBSOM_Parameter.xlsx",
#         header=None  # ✅ read raw, no auto header parsing
#     )

#     kpi_df["text"] = kpi_df.fillna("").astype(str).apply(
#         lambda row: " | ".join(row.values), axis=1
#     )

#     # ── Convert scoring sheet into meaningful text chunks ──
#     scoring_df = build_scoring_chunks(scoring_df)

#     return kpi_df, scoring_df


# def build_scoring_chunks(raw_df):
#     """
#     Converts raw Excel rows into structured text that preserves
#     slab table context (headers + rows grouped together).
#     """
#     chunks = []
#     current_section = ""
#     current_headers = []
#     buffer_rows = []

#     for _, row in raw_df.iterrows():
#         row_vals = [str(v).strip() for v in row.values if str(v).strip() not in ("", "nan")]

#         if not row_vals:
#             # Empty row = flush buffer
#             if current_section and buffer_rows:
#                 chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
#                 chunks.append(chunk)
#                 buffer_rows = []
#             continue

#         row_text = " | ".join(row_vals)

#         # Detect section header (merged title rows — usually single long cell)
#         if len(row_vals) == 1 or (len(row_vals) <= 3 and any(
#             kw in row_text.lower() for kw in [
#                 "slab", "parameter", "score", "dispatch", "amendment",
#                 "funding", "npc", "received", "discrepancy"
#             ]
#         )):
#             # Flush previous section
#             if current_section and buffer_rows:
#                 chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
#                 chunks.append(chunk)
#                 buffer_rows = []
#                 current_headers = []

#             current_section = row_text
#             continue

#         # Detect column header row (contains "Number of forms" or score range patterns)
#         if "number of forms" in row_text.lower() or any(
#             kw in row_text for kw in ["1 -", "1-<", "31 -", "70 -", "161"]
#         ):
#             current_headers = row_vals
#             continue

#         # Notes/footnotes rows (start with ****)
#         if row_text.startswith("*"):
#             if current_section:
#                 chunks.append(f"NOTE for {current_section}: {row_text}")
#             continue

#         # Regular data row — add to buffer
#         if current_section:
#             buffer_rows.append(row_vals)

#     # Flush last section
#     if current_section and buffer_rows:
#         chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
#         chunks.append(chunk)

#     # Convert to DataFrame
#     result_df = pd.DataFrame({"text": chunks})
#     return result_df


# def _build_chunk_text(section, headers, rows):
#     """Builds a readable text block from a slab table section."""
#     lines = [f"SECTION: {section}"]

#     if headers:
#         lines.append(f"Columns (Number of Forms): {' | '.join(headers)}")

#     for row in rows:
#         if headers and len(row) == len(headers):
#             # Map header to value
#             mapped = ", ".join(
#                 f"{headers[i]}: {row[i]}" for i in range(len(row))
#             )
#             lines.append(f"  - {mapped}")
#         else:
#             lines.append(f"  - {' | '.join(row)}")

#     return "\n".join(lines)


# def create_vector_db(df):
#     embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
#     dimension = embeddings.shape[1]

#     index = faiss.IndexFlatL2(dimension)
#     index.add(np.array(embeddings))

#     return index, embeddings


# def search(query, df, index, top_k=5):
#     # ── Semantic search ───────────────────────────────────
#     query_embedding = model.encode([query])
#     distances, indices = index.search(np.array(query_embedding), top_k)
#     semantic_results = df.iloc[indices[0]]["text"].tolist()

#     # ── Keyword fallback search ───────────────────────────
#     keywords = [w.lower() for w in query.split() if len(w) > 2]
#     mask = df["text"].str.lower().apply(
#         lambda text: any(kw in text for kw in keywords)
#     )
#     keyword_results = df[mask]["text"].tolist()[:top_k]

#     # ── Merge + deduplicate ───────────────────────────────
#     combined = list(dict.fromkeys(semantic_results + keyword_results))
#     return combined if combined else semantic_results




#New code#
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Role to file mapping ──────────────────────────────────
ROLE_FILES = {
    "SR_BSOM": {
        "goal_sheet": "utils/SrBSOM_Goal_Sheet.xlsx",
        "parameter": "utils/SrBSOM_Parameter.xlsx"
    },
    "BSOM": {
        "goal_sheet": "utils/BSOM_Goal_Sheet.xlsx",
        "parameter": "utils/BSOM_Parameter.xlsx"
    },
    "ABSOM_TSE": {
        "goal_sheet": "utils/ABSOM_TSE_GS.xlsx",
        "parameter": "utils/ABSOM_TSE_PARAMETER.xlsx"
    }
}


def load_data(role: str):
    """Load goal sheet + parameter for the selected role."""
    files = ROLE_FILES[role]

    kpi_df = pd.read_excel(files["goal_sheet"])
    scoring_raw = pd.read_excel(files["parameter"], header=None)

    kpi_df["text"] = kpi_df.fillna("").astype(str).apply(
        lambda row: " | ".join(row.values), axis=1
    )

    scoring_df = build_scoring_chunks(scoring_raw)

    return kpi_df, scoring_df


def build_scoring_chunks(raw_df):
    """
    Converts raw Excel rows into structured text that preserves
    slab table context (headers + rows grouped together).
    """
    chunks = []
    current_section = ""
    current_headers = []
    buffer_rows = []

    for _, row in raw_df.iterrows():
        row_vals = [str(v).strip() for v in row.values if str(v).strip() not in ("", "nan")]

        if not row_vals:
            if current_section and buffer_rows:
                chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
                chunks.append(chunk)
                buffer_rows = []
            continue

        row_text = " | ".join(row_vals)

        # Detect section header
        if len(row_vals) == 1 or (len(row_vals) <= 3 and any(
            kw in row_text.lower() for kw in [
                "slab", "parameter", "score", "dispatch", "amendment",
                "funding", "npc", "received", "discrepancy", "overall",
                "target", "incentive", "penalty", "quality", "productivity"
            ]
        )):
            if current_section and buffer_rows:
                chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
                chunks.append(chunk)
                buffer_rows = []
                current_headers = []

            current_section = row_text
            continue

        # Detect column header row
        if "number of forms" in row_text.lower() or any(
            kw in row_text for kw in ["1 -", "1-<", "31 -", "70 -", "161", ">="]
        ):
            current_headers = row_vals
            continue

        # Notes/footnotes
        if row_text.startswith("*"):
            if current_section:
                chunks.append(f"NOTE for {current_section}: {row_text}")
            continue

        # Regular data row
        if current_section:
            buffer_rows.append(row_vals)

    # Flush last section
    if current_section and buffer_rows:
        chunk = _build_chunk_text(current_section, current_headers, buffer_rows)
        chunks.append(chunk)

    return pd.DataFrame({"text": chunks})


def _build_chunk_text(section, headers, rows):
    """Builds a readable text block from a slab table section."""
    lines = [f"SECTION: {section}"]

    if headers:
        lines.append(f"Columns (Number of Forms): {' | '.join(headers)}")

    for row in rows:
        if headers and len(row) == len(headers):
            mapped = ", ".join(f"{headers[i]}: {row[i]}" for i in range(len(row)))
            lines.append(f"  - {mapped}")
        else:
            lines.append(f"  - {' | '.join(row)}")

    return "\n".join(lines)


def create_vector_db(df):
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return index, embeddings


def search(query, df, index, top_k=5):
    # ── Semantic search ───────────────────────────────────
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    semantic_results = df.iloc[indices[0]]["text"].tolist()

    # ── Keyword fallback ──────────────────────────────────
    keywords = [w.lower() for w in query.split() if len(w) > 2]
    mask = df["text"].str.lower().apply(
        lambda text: any(kw in text for kw in keywords)
    )
    keyword_results = df[mask]["text"].tolist()[:top_k]

    # ── Merge + deduplicate ───────────────────────────────
    combined = list(dict.fromkeys(semantic_results + keyword_results))
    return combined if combined else semantic_results