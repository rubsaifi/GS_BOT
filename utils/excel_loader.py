"""
excel_loader.py
Reads both Excel files and converts them into structured text chunks for RAG.
"""

import pandas as pd
import os
from typing import Tuple

# ── Column name maps (update if your actual columns differ) ───────────────────
KPI_COLS = {
    "parameter":   "Parameter",
    "category":    "Category",
    "max_score":   "Max Score",
    "weightage":   "Weightage (%)",
    "target":      "Target (Full Score)",
    "negative":    "Negative Score Applicable",
    "remarks":     "Remarks",
}

SCORING_COLS = {
    "parameter":   "Parameter",
    "slab_min":    "Slab Min",
    "slab_max":    "Slab Max",
    "score":       "Score",
    "description": "Description",
}


def load_kpi_master(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    return df


def load_parameter_scoring(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    return df


def build_knowledge_chunks(kpi_df: pd.DataFrame, scoring_df: pd.DataFrame) -> list[dict]:
    """
    Convert both DataFrames into a list of text chunks with metadata.
    Each chunk is a dict: {"text": str, "metadata": dict}
    """
    chunks = []

    # ── 1. Overall KPI summary chunk ─────────────────────────────────────────
    total_max = kpi_df[KPI_COLS["max_score"]].apply(
        lambda x: x if isinstance(x, (int, float)) and x > 0 else 0
    ).sum()
    param_names = kpi_df[KPI_COLS["parameter"]].tolist()
    summary = (
        f"SRBSOM Goal Sheet Overview: There are {len(param_names)} KPI parameters "
        f"in the goal sheet. The total maximum achievable positive score is {total_max}. "
        f"Parameters are: {', '.join(str(p) for p in param_names)}. "
        "Each parameter has defined slabs with corresponding scores. "
        "To achieve a score of 100 (or maximum), an employee must perform at the highest slab for every parameter."
    )
    chunks.append({"text": summary, "metadata": {"type": "summary", "parameter": "all"}})

    # ── 2. Per-parameter chunks (KPI info + scoring slabs merged) ────────────
    for _, kpi_row in kpi_df.iterrows():
        param = str(kpi_row.get(KPI_COLS["parameter"], "")).strip()
        if not param:
            continue

        category   = kpi_row.get(KPI_COLS["category"], "N/A")
        max_score  = kpi_row.get(KPI_COLS["max_score"], "N/A")
        weightage  = kpi_row.get(KPI_COLS["weightage"], "N/A")
        target     = kpi_row.get(KPI_COLS["target"], "N/A")
        negative   = kpi_row.get(KPI_COLS["negative"], "No")
        remarks    = kpi_row.get(KPI_COLS["remarks"], "")

        # Get slabs for this parameter
        param_slabs = scoring_df[
            scoring_df[SCORING_COLS["parameter"]].astype(str).str.strip() == param
        ]

        slab_lines = []
        highest_slab_action = ""
        for _, slab in param_slabs.iterrows():
            s_min  = slab.get(SCORING_COLS["slab_min"], "")
            s_max  = slab.get(SCORING_COLS["slab_max"], "")
            score  = slab.get(SCORING_COLS["score"], 0)
            desc   = slab.get(SCORING_COLS["description"], "")
            line   = f"  - Slab [{s_min} to {s_max}]: Score = {score}. {desc}"
            slab_lines.append(line)
            # Track highest positive score slab
            try:
                if float(str(score)) == float(str(max_score)):
                    highest_slab_action = f"To get full score ({max_score}) for {param}, achieve: {desc}"
            except Exception:
                pass

        slab_text = "\n".join(slab_lines) if slab_lines else "  - No slab data available."

        negative_note = ""
        if str(negative).strip().lower() == "yes":
            negative_note = (
                f"⚠️ IMPORTANT: {param} has NEGATIVE SCORING. "
                "Poor performance will DEDUCT points from your total score. "
            )

        chunk_text = (
            f"Parameter: {param}\n"
            f"Category: {category}\n"
            f"Maximum Score: {max_score}\n"
            f"Weightage: {weightage}%\n"
            f"Target for Full Score: {target}\n"
            f"Negative Score Applicable: {negative}\n"
            f"Remarks: {remarks}\n"
            f"{negative_note}"
            f"Scoring Slabs:\n{slab_text}\n"
            f"{highest_slab_action}"
        )

        chunks.append({
            "text": chunk_text,
            "metadata": {
                "type": "parameter",
                "parameter": param,
                "category": str(category),
                "max_score": str(max_score),
            }
        })

    # ── 3. Score-100 strategy chunk ───────────────────────────────────────────
    strategy_lines = [
        "HOW TO ACHIEVE MAXIMUM SCORE (Score 100 Guide for SRBSOM):",
        "To maximise your goal sheet score, you must hit the highest slab for EVERY parameter.",
        "Here is what you need to do for each parameter:\n",
    ]

    for _, kpi_row in kpi_df.iterrows():
        param     = str(kpi_row.get(KPI_COLS["parameter"], "")).strip()
        max_score = kpi_row.get(KPI_COLS["max_score"], 0)
        target    = kpi_row.get(KPI_COLS["target"], "")
        if not param:
            continue
        strategy_lines.append(f"• {param}: Target = {target} to earn {max_score} points.")

    strategy_lines.append(
        "\nADDITIONALLY: Avoid NI Branch Audit Rating — it will DEDUCT points from your score."
    )
    strategy_lines.append(
        "Focus on parameters with higher weightage/max scores first for maximum impact."
    )

    chunks.append({
        "text": "\n".join(strategy_lines),
        "metadata": {"type": "strategy", "parameter": "all"}
    })

    # ── 4. Negative parameters warning chunk ─────────────────────────────────
    neg_params = kpi_df[
        kpi_df[KPI_COLS["negative"]].astype(str).str.strip().str.lower() == "yes"
    ][KPI_COLS["parameter"]].tolist()

    if neg_params:
        neg_chunk = (
            "NEGATIVE SCORING PARAMETERS — These parameters can DEDUCT points from your total score:\n"
            + "\n".join(f"• {p}" for p in neg_params)
            + "\nMake sure you perform well on these to avoid losing points you earned elsewhere."
        )
        chunks.append({"text": neg_chunk, "metadata": {"type": "negative_warning", "parameter": "all"}})

    # ── 5. Category-wise chunks ───────────────────────────────────────────────
    if KPI_COLS["category"] in kpi_df.columns:
        for cat, group in kpi_df.groupby(KPI_COLS["category"]):
            params_in_cat = group[KPI_COLS["parameter"]].tolist()
            cat_max = group[KPI_COLS["max_score"]].apply(
                lambda x: x if isinstance(x, (int, float)) and x > 0 else 0
            ).sum()
            cat_chunk = (
                f"Category: {cat}\n"
                f"Parameters in this category: {', '.join(str(p) for p in params_in_cat)}\n"
                f"Total max score for {cat} category: {cat_max} points.\n"
                "Focusing on this category well will significantly boost your overall score."
            )
            chunks.append({
                "text": cat_chunk,
                "metadata": {"type": "category", "parameter": str(cat)}
            })

    return chunks


def get_score_gap_advice(kpi_df: pd.DataFrame, scoring_df: pd.DataFrame, current_scores: dict) -> str:
    """
    Given a dict of {parameter: current_value}, return advice on what to improve.
    current_scores = {"Amendments": 3, "AOF (Account Opening Form)": 8, ...}
    """
    advice_lines = ["📊 PERSONALISED SCORE GAP ANALYSIS:\n"]
    total_current = 0
    total_max = 0

    for _, kpi_row in kpi_df.iterrows():
        param     = str(kpi_row.get(KPI_COLS["parameter"], "")).strip()
        max_score = kpi_row.get(KPI_COLS["max_score"], 0)
        try:
            max_score = float(max_score)
        except Exception:
            continue

        if max_score <= 0:
            continue

        total_max += max_score
        current_val = current_scores.get(param)

        if current_val is None:
            advice_lines.append(f"• {param}: No data provided. Max possible = {max_score} pts.")
            continue

        # Find current score from slab
        param_slabs = scoring_df[
            scoring_df[SCORING_COLS["parameter"]].astype(str).str.strip() == param
        ]
        current_score = 0
        full_score_target = None

        for _, slab in param_slabs.iterrows():
            try:
                s_min = float(str(slab[SCORING_COLS["slab_min"]]).replace(",", ""))
                s_max_raw = str(slab[SCORING_COLS["slab_max"]]).replace(",", "")
                s_max = float(s_max_raw) if s_max_raw not in ["999", "999999999"] else float("inf")
                sc = float(slab[SCORING_COLS["score"]])
                if s_min <= float(current_val) <= s_max:
                    current_score = sc
                if sc == max_score and full_score_target is None:
                    full_score_target = slab[SCORING_COLS["description"]]
            except Exception:
                continue

        total_current += current_score
        gap = max_score - current_score

        if gap <= 0:
            advice_lines.append(f"✅ {param}: Full score achieved! ({current_score}/{max_score} pts)")
        else:
            action = full_score_target if full_score_target else f"reach target for {param}"
            advice_lines.append(
                f"🔺 {param}: Current = {current_score}/{max_score} pts. "
                f"Gap = {gap} pts. Action: {action}"
            )

    advice_lines.append(f"\n📈 Estimated Total: {total_current:.0f} / {total_max:.0f} pts")
    advice_lines.append(f"💡 Score Gap to Maximum: {total_max - total_current:.0f} pts")
    return "\n".join(advice_lines)
