"""
Script to create SAMPLE Excel files demonstrating the expected format.
Replace these with your actual Excel files in the /data folder.

File 1: kpi_master.xlsx  → KPI names, max scores, weightages
File 2: parameter_scoring.xlsx → Slab-based scoring logic per parameter
"""

import pandas as pd
import os

def create_sample_files():
    os.makedirs("data", exist_ok=True)

    # ── FILE 1: KPI Master ─────────────────────────────────────────────────────
    kpi_data = {
        "Parameter": [
            "Amendments", "AOF (Account Opening Form)", "CUbe Activations",
            "Branch Audit Rating", "Customer Complaints Resolution",
            "Cross Sell Products", "Digital Transactions", "NPS Score",
            "SB Account Opening", "Loan Disbursement", "FD Booking",
            "Insurance Premium", "Demat Account Opening", "Credit Card Issuance",
            "Staff Training Completion"
        ],
        "Category": [
            "Operations", "New Business", "Digital",
            "Compliance", "Service Quality",
            "Business", "Digital", "Service Quality",
            "New Business", "Business", "Business",
            "Business", "New Business", "Business",
            "HR"
        ],
        "Max Score": [
            10, 15, 10,
            -5, 8,
            12, 10, 8,
            10, 15, 10,
            12, 8, 10,
            7
        ],
        "Weightage (%)": [
            6, 9, 6,
            5, 5,
            8, 6, 5,
            6, 9, 6,
            8, 5, 6,
            5
        ],
        "Target (Full Score)": [
            10, 20, 15,
            "S/A (No Negative)", 5,
            8, 100, 75,
            15, 5, 10,
            500000, 5, 3,
            100
        ],
        "Negative Score Applicable": [
            "No", "No", "No",
            "Yes", "No",
            "No", "No", "No",
            "No", "No", "No",
            "No", "No", "No",
            "No"
        ],
        "Remarks": [
            "Monthly amendments count", "New accounts opened", "CUbe app activations",
            "NI rating gives -5 penalty", "Resolved within TAT",
            "Number of cross-sell products", "% digital txns vs total",
            "Net Promoter Score percentile", "Savings Bank new accounts",
            "Total loan cases", "Fixed Deposit bookings",
            "Total insurance premium collected", "New demat accounts",
            "New credit cards issued", "% staff trained"
        ]
    }
    df_kpi = pd.DataFrame(kpi_data)
    df_kpi.to_excel("data/kpi_master.xlsx", index=False)
    print("✅ Created data/kpi_master.xlsx")

    # ── FILE 2: Parameter Scoring Slabs ───────────────────────────────────────
    scoring_data = {
        "Parameter": [
            # Amendments
            "Amendments", "Amendments", "Amendments", "Amendments", "Amendments",
            # AOF
            "AOF (Account Opening Form)", "AOF (Account Opening Form)", "AOF (Account Opening Form)", "AOF (Account Opening Form)",
            # CUbe
            "CUbe Activations", "CUbe Activations", "CUbe Activations", "CUbe Activations",
            # Branch Audit
            "Branch Audit Rating", "Branch Audit Rating", "Branch Audit Rating",
            # Complaints
            "Customer Complaints Resolution", "Customer Complaints Resolution", "Customer Complaints Resolution",
            # Cross Sell
            "Cross Sell Products", "Cross Sell Products", "Cross Sell Products", "Cross Sell Products",
            # Digital
            "Digital Transactions", "Digital Transactions", "Digital Transactions",
            # NPS
            "NPS Score", "NPS Score", "NPS Score",
            # SB Account
            "SB Account Opening", "SB Account Opening", "SB Account Opening", "SB Account Opening",
            # Loan
            "Loan Disbursement", "Loan Disbursement", "Loan Disbursement", "Loan Disbursement",
            # FD
            "FD Booking", "FD Booking", "FD Booking",
            # Insurance
            "Insurance Premium", "Insurance Premium", "Insurance Premium",
            # Demat
            "Demat Account Opening", "Demat Account Opening", "Demat Account Opening",
            # Credit Card
            "Credit Card Issuance", "Credit Card Issuance", "Credit Card Issuance",
            # Training
            "Staff Training Completion", "Staff Training Completion", "Staff Training Completion",
        ],
        "Slab Min": [
            # Amendments
            0, 1, 3, 6, 10,
            # AOF
            0, 5, 11, 16,
            # CUbe
            0, 3, 8, 12,
            # Branch Audit (NI = negative)
            "NI", "S/A", "S",
            # Complaints
            0, 3, 5,
            # Cross Sell
            0, 2, 5, 8,
            # Digital
            0, 50, 75,
            # NPS
            0, 50, 75,
            # SB Account
            0, 4, 9, 13,
            # Loan
            0, 1, 3, 5,
            # FD
            0, 4, 8,
            # Insurance
            0, 100000, 300000,
            # Demat
            0, 2, 4,
            # Credit Card
            0, 1, 2,
            # Training
            0, 50, 80,
        ],
        "Slab Max": [
            # Amendments
            0, 2, 5, 9, 999,
            # AOF
            4, 10, 15, 999,
            # CUbe
            2, 7, 11, 999,
            # Branch Audit
            "NI", "S/A", "S",
            # Complaints
            2, 4, 999,
            # Cross Sell
            1, 4, 7, 999,
            # Digital
            49, 74, 999,
            # NPS
            49, 74, 999,
            # SB Account
            3, 8, 12, 999,
            # Loan
            0, 2, 4, 999,
            # FD
            3, 7, 999,
            # Insurance
            99999, 299999, 999999999,
            # Demat
            1, 3, 999,
            # Credit Card
            0, 1, 999,
            # Training
            49, 79, 999,
        ],
        "Score": [
            # Amendments
            0, 2, 5, 8, 10,
            # AOF
            0, 5, 10, 15,
            # CUbe
            0, 3, 7, 10,
            # Branch Audit
            -5, 0, 5,
            # Complaints
            0, 4, 8,
            # Cross Sell
            0, 4, 8, 12,
            # Digital
            0, 5, 10,
            # NPS
            0, 4, 8,
            # SB Account
            0, 3, 7, 10,
            # Loan
            0, 5, 10, 15,
            # FD
            0, 5, 10,
            # Insurance
            0, 6, 12,
            # Demat
            0, 4, 8,
            # Credit Card
            0, 5, 10,
            # Training
            0, 3, 7,
        ],
        "Description": [
            # Amendments
            "No amendments done", "1-2 amendments", "3-5 amendments", "6-9 amendments", "10+ amendments – Full score",
            # AOF
            "0-4 AOF – No score", "5-10 AOF – Partial", "11-15 AOF – Good", "16+ AOF – Full score",
            # CUbe
            "0-2 CUbe – No score", "3-7 CUbe – Partial", "8-11 CUbe – Good", "12+ CUbe – Full score",
            # Branch Audit
            "NI rating – Negative impact", "S/A rating – Neutral", "S rating – Positive",
            # Complaints
            "0-2 resolved – No score", "3-4 resolved – Partial", "5+ resolved – Full",
            # Cross Sell
            "0-1 cross sell – No score", "2-4 – Partial", "5-7 – Good", "8+ – Full score",
            # Digital
            "Below 50% – No score", "50-74% – Partial", "75%+ – Full score",
            # NPS
            "Below 50 – No score", "50-74 – Partial", "75+ – Full score",
            # SB Account
            "0-3 accounts – No score", "4-8 accounts – Partial", "9-12 – Good", "13+ – Full score",
            # Loan
            "No disbursement", "1-2 cases – Partial", "3-4 cases – Good", "5+ cases – Full score",
            # FD
            "0-3 FDs – No score", "4-7 FDs – Partial", "8+ FDs – Full score",
            # Insurance
            "Below 1 Lac – No score", "1-3 Lac – Partial", "3 Lac+ – Full score",
            # Demat
            "0-1 Demat – No score", "2-3 Demat – Partial", "4+ Demat – Full score",
            # Credit Card
            "No card issued", "1 card – Partial", "2+ cards – Full score",
            # Training
            "Below 50% – No score", "50-79% trained – Partial", "80%+ – Full score",
        ]
    }
    df_scoring = pd.DataFrame(scoring_data)
    df_scoring.to_excel("data/parameter_scoring.xlsx", index=False)
    print("✅ Created data/parameter_scoring.xlsx")
    print("\n📌 Replace these sample files with your actual Excel files.")
    print("   Keep the same column structure or update excel_loader.py accordingly.")

if __name__ == "__main__":
    create_sample_files()
