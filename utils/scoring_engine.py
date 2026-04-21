import pandas as pd

def calculate_score(df):
    """
    Example scoring logic:
    Modify based on your actual scoring sheet
    """

    total_score = 0
    insights = []

    for _, row in df.iterrows():
        value = str(row).lower()

        # Example rules (customize these)
        if "ni" in value:
            total_score -= 10
            insights.append("⚠️ Negative impact due to NI rating")

        elif "yes" in value or "achieved" in value:
            total_score += 5

        elif "no" in value:
            total_score += 0

    return total_score, insights