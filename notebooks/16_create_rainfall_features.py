import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_RAINFALL = Path(
    "data/kerala_district_rainfall.csv"
)

INPUT_TARGET = Path(
    "data/kerala_prediction_target_final.csv"
)

OUTPUT_PATH = Path(
    "data/kerala_ml_dataset.csv"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("Loading rainfall data...")
rainfall = pd.read_csv(INPUT_RAINFALL)

print("Loading flood target data...")
target = pd.read_csv(INPUT_TARGET)


# --------------------------------------------------
# Prepare dates
# --------------------------------------------------

rainfall["Date"] = pd.to_datetime(rainfall["Date"])
target["Date"] = pd.to_datetime(target["Date"])


# --------------------------------------------------
# Sort correctly
# --------------------------------------------------

rainfall = rainfall.sort_values(
    ["District", "Date"]
).reset_index(drop=True)


# --------------------------------------------------
# Create rainfall features
# --------------------------------------------------

grouped = rainfall.groupby("District")["Rainfall_mm"]

rainfall["Rainfall_1d"] = rainfall["Rainfall_mm"]

rainfall["Rainfall_3d"] = grouped.transform(
    lambda x: x.rolling(3, min_periods=1).sum()
)

rainfall["Rainfall_7d"] = grouped.transform(
    lambda x: x.rolling(7, min_periods=1).sum()
)

rainfall["Rainfall_30d"] = grouped.transform(
    lambda x: x.rolling(30, min_periods=1).sum()
)

rainfall["Rainfall_3d_max"] = grouped.transform(
    lambda x: x.rolling(3, min_periods=1).max()
)

rainfall["Rainfall_7d_max"] = grouped.transform(
    lambda x: x.rolling(7, min_periods=1).max()
)


# --------------------------------------------------
# Select required columns
# --------------------------------------------------

rainfall_features = rainfall[
    [
        "Date",
        "District",
        "Rainfall_1d",
        "Rainfall_3d",
        "Rainfall_7d",
        "Rainfall_30d",
        "Rainfall_3d_max",
        "Rainfall_7d_max",
    ]
]


# --------------------------------------------------
# Merge with flood target
# --------------------------------------------------

ml_dataset = target.merge(
    rainfall_features,
    on=["Date", "District"],
    how="left"
)


# --------------------------------------------------
# Check merge
# --------------------------------------------------

print("\n--------------------------------------")
print("MERGE CHECK")
print("--------------------------------------")

print("Target rows:", len(target))
print("ML rows:", len(ml_dataset))

print(
    "Missing rainfall feature rows:",
    ml_dataset[
        [
            "Rainfall_1d",
            "Rainfall_3d",
            "Rainfall_7d",
            "Rainfall_30d",
            "Rainfall_3d_max",
            "Rainfall_7d_max",
        ]
    ].isna().any(axis=1).sum()
)


# --------------------------------------------------
# Remove rows with missing features
# --------------------------------------------------

feature_columns = [
    "Rainfall_1d",
    "Rainfall_3d",
    "Rainfall_7d",
    "Rainfall_30d",
    "Rainfall_3d_max",
    "Rainfall_7d_max",
]

ml_dataset = ml_dataset.dropna(
    subset=feature_columns
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

ml_dataset.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# Final report
# --------------------------------------------------

print("\n======================================")
print("ML DATASET CREATED")
print("======================================")

print("Shape:", ml_dataset.shape)

print(
    "Date range:",
    ml_dataset["Date"].min(),
    "to",
    ml_dataset["Date"].max()
)

print(
    "Districts:",
    ml_dataset["District"].nunique()
)

print("\nTarget distribution:")

print(
    ml_dataset["Flood_Tomorrow"]
    .value_counts()
)

print("\nTarget percentage:")

print(
    ml_dataset["Flood_Tomorrow"]
    .value_counts(normalize=True) * 100
)

print("\nFeature statistics:")

print(
    ml_dataset[feature_columns].describe()
)

print("\nSample:")
print(
    ml_dataset.head(10)
)

print(
    f"\nSaved to: {OUTPUT_PATH}"
)