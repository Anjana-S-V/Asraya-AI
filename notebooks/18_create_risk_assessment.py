
from pathlib import Path
import pandas as pd


# ==========================================
# PATHS
# ==========================================

INPUT_PATH = Path("models/test_predictions.csv")
OUTPUT_PATH = Path("models/risk_assessment.csv")


# ==========================================
# LOAD PREDICTIONS
# ==========================================

print("Loading model predictions...")

df = pd.read_csv(INPUT_PATH)

print(f"Loaded {len(df)} test predictions")

print("\nColumns:")
print(df.columns.tolist())


# ==========================================
# CHECK REQUIRED COLUMNS
# ==========================================

required_columns = [
    "Date",
    "District",
    "Flood_Tomorrow",
    "Logistic_Probability",
    "RandomForest_Probability"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ==========================================
# USE RANDOM FOREST FOR PRIMARY RISK SCORE
# ==========================================

df["Risk_Probability"] = df["RandomForest_Probability"]


# ==========================================
# RISK CATEGORY
# ==========================================
# These are temporary presentation thresholds.
# They are NOT official flood-risk thresholds.

def classify_risk(probability):

    if probability < 0.10:
        return "LOW"

    elif probability < 0.30:
        return "MODERATE"

    elif probability < 0.60:
        return "HIGH"

    else:
        return "VERY HIGH"


df["Risk_Category"] = df["Risk_Probability"].apply(
    classify_risk
)


# ==========================================
# DISPLAY RISK DISTRIBUTION
# ==========================================

print("\n======================================")
print("RISK CATEGORY DISTRIBUTION")
print("======================================")

print(
    df["Risk_Category"]
    .value_counts()
    .sort_index()
)


# ==========================================
# PROBABILITY SUMMARY
# ==========================================

print("\n======================================")
print("RANDOM FOREST PROBABILITY SUMMARY")
print("======================================")

print(
    df["Risk_Probability"].describe()
)


# ==========================================
# ACTUAL FLOOD CASES
# ==========================================

print("\n======================================")
print("PROBABILITY FOR ACTUAL FLOOD CASES")
print("======================================")

flood_cases = df[df["Flood_Tomorrow"] == 1]

print(f"Actual flood cases: {len(flood_cases)}")

if len(flood_cases) > 0:

    print(
        flood_cases["Risk_Probability"]
        .describe()
    )


# ==========================================
# HIGHEST-RISK OBSERVATIONS
# ==========================================

print("\n======================================")
print("TOP 10 HIGHEST-RISK OBSERVATIONS")
print("======================================")

top_risk = (
    df[
        [
            "Date",
            "District",
            "Flood_Tomorrow",
            "Logistic_Probability",
            "RandomForest_Probability",
            "Risk_Category"
        ]
    ]
    .sort_values(
        "RandomForest_Probability",
        ascending=False
    )
    .head(10)
)

print(top_risk.to_string(index=False))


# ==========================================
# SAVE
# ==========================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ==========================================
# COMPLETE
# ==========================================

print("\n======================================")
print("RISK ASSESSMENT CREATED")
print("======================================")

print(f"Saved to: {OUTPUT_PATH}")

