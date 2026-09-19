from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

RISK_PATH = Path("models/risk_assessment_explained.csv")
RAG_CHUNKS_PATH = Path("models/rag/chunks.npy")

OUTPUT_PATH = Path("models/ai_guidance_context.csv")


# ============================================================
# LOAD DATA
# ============================================================

print("Loading risk assessment data...")

risk_df = pd.read_csv(RISK_PATH)

print("Risk data shape:", risk_df.shape)
print("Risk columns:")
print(risk_df.columns.tolist())


print("\nLoading RAG chunks...")

rag_chunks = np.load(
    RAG_CHUNKS_PATH,
    allow_pickle=True
)

print("RAG chunks:", len(rag_chunks))


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Date",
    "District",
    "Flood_Tomorrow",
    "Risk_Probability",
    "Risk_Category",
    "Rainfall_1d",
    "Rainfall_3d",
    "Rainfall_7d",
    "Rainfall_30d",
    "Rainfall_3d_max",
    "Rainfall_7d_max",
    "Risk_Explanation_Text"
]

missing_columns = [
    col for col in required_columns
    if col not in risk_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# CLEAN DATE
# ============================================================

risk_df["Date"] = pd.to_datetime(
    risk_df["Date"],
    errors="coerce"
)

risk_df["District"] = (
    risk_df["District"]
    .astype(str)
    .str.strip()
)


# ============================================================
# BUILD AI CONTEXT
# ============================================================

def build_risk_context(row):

    context = f"""
Flood risk assessment context:

District: {row['District']}
Date: {row['Date'].date()}

Model-derived risk score:
{row['Risk_Probability']:.3f}

Risk category:
{row['Risk_Category']}

Rainfall indicators available up to this date:

Rainfall in previous 1 day:
{row['Rainfall_1d']:.1f} mm

Rainfall accumulated over previous 3 days:
{row['Rainfall_3d']:.1f} mm

Rainfall accumulated over previous 7 days:
{row['Rainfall_7d']:.1f} mm

Rainfall accumulated over previous 30 days:
{row['Rainfall_30d']:.1f} mm

Maximum daily rainfall within previous 3 days:
{row['Rainfall_3d_max']:.1f} mm

Maximum daily rainfall within previous 7 days:
{row['Rainfall_7d_max']:.1f} mm

Rainfall-based contextual explanation:
{row['Risk_Explanation_Text']}
""".strip()

    return context


risk_df["AI_Risk_Context"] = risk_df.apply(
    build_risk_context,
    axis=1
)


# ============================================================
# SAVE
# ============================================================

context_df = risk_df[
    [
        "Date",
        "District",
        "Risk_Probability",
        "Risk_Category",
        "AI_Risk_Context"
    ]
].copy()


context_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# TEST
# ============================================================

print("\n" + "=" * 60)
print("AI GUIDANCE CONTEXT CREATED")
print("=" * 60)

print("Rows:", len(context_df))
print("Columns:", context_df.columns.tolist())
print("Saved to:", OUTPUT_PATH)


print("\nSample AI risk context:")
print("-" * 60)
print(context_df.iloc[0]["AI_Risk_Context"])


# ============================================================
# DEMONSTRATE A HIGH-RISK CASE
# ============================================================

high_risk = context_df.sort_values(
    "Risk_Probability",
    ascending=False
).iloc[0]

print("\n" + "=" * 60)
print("HIGHEST MODEL-DERIVED RISK EXAMPLE")
print("=" * 60)

print("District:", high_risk["District"])
print("Date:", high_risk["Date"])
print("Risk score:", high_risk["Risk_Probability"])
print("Risk category:", high_risk["Risk_Category"])

print("\nContext that will be given to the AI:")
print("-" * 60)
print(high_risk["AI_Risk_Context"])