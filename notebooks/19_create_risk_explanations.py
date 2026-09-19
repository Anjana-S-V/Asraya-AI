
from pathlib import Path
import pandas as pd


# ==========================================
# PATHS
# ==========================================

ML_DATA_PATH = Path("data/kerala_ml_dataset.csv")
RISK_PATH = Path("models/risk_assessment.csv")
OUTPUT_PATH = Path("models/risk_assessment_explained.csv")


# ==========================================
# LOAD DATA
# ==========================================

print("Loading ML dataset...")
ml_df = pd.read_csv(ML_DATA_PATH)

print("Loading risk assessment...")
risk_df = pd.read_csv(RISK_PATH)


# ==========================================
# PREPARE DATES
# ==========================================

ml_df["Date"] = pd.to_datetime(ml_df["Date"])
risk_df["Date"] = pd.to_datetime(risk_df["Date"])


# ==========================================
# RAINFALL FEATURES
# ==========================================

rainfall_features = [
    "Rainfall_1d",
    "Rainfall_3d",
    "Rainfall_7d",
    "Rainfall_30d",
    "Rainfall_3d_max",
    "Rainfall_7d_max"
]


# ==========================================
# CALCULATE HISTORICAL PERCENTILES
# ==========================================

print("\nCalculating historical rainfall thresholds...")

percentiles = {}

for feature in rainfall_features:

    percentiles[feature] = {
        "p75": ml_df[feature].quantile(0.75),
        "p90": ml_df[feature].quantile(0.90),
        "p95": ml_df[feature].quantile(0.95)
    }

    print(
        f"{feature}: "
        f"P75={percentiles[feature]['p75']:.2f}, "
        f"P90={percentiles[feature]['p90']:.2f}, "
        f"P95={percentiles[feature]['p95']:.2f}"
    )


# ==========================================
# EXPLANATION FUNCTION
# ==========================================

def generate_explanation(row):

    explanations = []

    # --------------------------------------
    # 1-DAY RAINFALL
    # --------------------------------------

    value = row["Rainfall_1d"]

    if value >= percentiles["Rainfall_1d"]["p95"]:
        explanations.append(
            f"Very high rainfall over the last 1 day "
            f"({value:.1f} mm)"
        )

    elif value >= percentiles["Rainfall_1d"]["p90"]:
        explanations.append(
            f"High rainfall over the last 1 day "
            f"({value:.1f} mm)"
        )

    # --------------------------------------
    # 3-DAY RAINFALL
    # --------------------------------------

    value = row["Rainfall_3d"]

    if value >= percentiles["Rainfall_3d"]["p95"]:
        explanations.append(
            f"Very high accumulated rainfall over "
            f"the last 3 days ({value:.1f} mm)"
        )

    elif value >= percentiles["Rainfall_3d"]["p90"]:
        explanations.append(
            f"High accumulated rainfall over "
            f"the last 3 days ({value:.1f} mm)"
        )

    # --------------------------------------
    # 7-DAY RAINFALL
    # --------------------------------------

    value = row["Rainfall_7d"]

    if value >= percentiles["Rainfall_7d"]["p95"]:
        explanations.append(
            f"Very high accumulated rainfall over "
            f"the last 7 days ({value:.1f} mm)"
        )

    elif value >= percentiles["Rainfall_7d"]["p90"]:
        explanations.append(
            f"High accumulated rainfall over "
            f"the last 7 days ({value:.1f} mm)"
        )

    # --------------------------------------
    # 30-DAY RAINFALL
    # --------------------------------------

    value = row["Rainfall_30d"]

    if value >= percentiles["Rainfall_30d"]["p95"]:
        explanations.append(
            f"Very high rainfall accumulation over "
            f"the last 30 days ({value:.1f} mm)"
        )

    elif value >= percentiles["Rainfall_30d"]["p90"]:
        explanations.append(
            f"High rainfall accumulation over "
            f"the last 30 days ({value:.1f} mm)"
        )

    # --------------------------------------
    # 3-DAY MAXIMUM
    # --------------------------------------

    value = row["Rainfall_3d_max"]

    if value >= percentiles["Rainfall_3d_max"]["p95"]:
        explanations.append(
            f"An extreme daily rainfall value occurred "
            f"within the last 3 days ({value:.1f} mm)"
        )

    # --------------------------------------
    # 7-DAY MAXIMUM
    # --------------------------------------

    value = row["Rainfall_7d_max"]

    if value >= percentiles["Rainfall_7d_max"]["p95"]:
        explanations.append(
            f"An extreme daily rainfall value occurred "
            f"within the last 7 days ({value:.1f} mm)"
        )

    # --------------------------------------
    # FALLBACK
    # --------------------------------------

    if not explanations:

        explanations.append(
            "Recent rainfall indicators are not "
            "unusually high compared with the "
            "historical dataset."
        )

    return explanations


# ==========================================
# CREATE EXPLANATIONS
# ==========================================

print("\nGenerating explanations...")

# Merge rainfall features into risk dataset

risk_df = risk_df.merge(
    ml_df[
        ["Date", "District"] + rainfall_features
    ],
    on=["Date", "District"],
    how="left"
)


risk_df["Risk_Explanation"] = risk_df.apply(
    generate_explanation,
    axis=1
)


# ==========================================
# CREATE DISPLAY TEXT
# ==========================================

risk_df["Risk_Explanation_Text"] = (
    risk_df["Risk_Explanation"]
    .apply(lambda x: " | ".join(x))
)


# ==========================================
# DISPLAY EXAMPLES
# ==========================================

print("\n======================================")
print("EXAMPLE RISK ASSESSMENTS")
print("======================================")

example_columns = [
    "Date",
    "District",
    "Risk_Probability",
    "Risk_Category",
    "Risk_Explanation_Text"
]

print(
    risk_df[
        example_columns
    ]
    .sort_values(
        "Risk_Probability",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ==========================================
# CHECK MISSING VALUES
# ==========================================

print("\n======================================")
print("DATA QUALITY CHECK")
print("======================================")

for feature in rainfall_features:

    missing = risk_df[feature].isna().sum()

    print(
        f"{feature}: {missing} missing"
    )


# ==========================================
# SAVE
# ==========================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

risk_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ==========================================
# COMPLETE
# ==========================================

print("\n======================================")
print("RISK EXPLANATION LAYER CREATED")
print("======================================")

print(
    f"Saved to: {OUTPUT_PATH}"
)

print(
    f"Rows: {len(risk_df)}"
)

print(
    f"Columns: {len(risk_df.columns)}"
)

