import pandas as pd


# --------------------------------------------------
# 1. Load the original dataset
# --------------------------------------------------

file_path = "data/India_Flood_Inventory_v3.csv"

df = pd.read_csv(file_path)

print("Original dataset:", df.shape)


# --------------------------------------------------
# 2. Clean column names
# --------------------------------------------------

df.columns = df.columns.str.strip()

print("\nColumns:")
print(df.columns.tolist())


# --------------------------------------------------
# 3. Keep only Kerala records
# --------------------------------------------------

kerala = df[
    df["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "kerala"
].copy()

print("\nKerala records:", kerala.shape)


# --------------------------------------------------
# 4. Remove unnecessary column
# --------------------------------------------------

kerala = kerala.drop(
    columns=["Unnamed: 0"],
    errors="ignore"
)


# --------------------------------------------------
# 5. Convert dates
# --------------------------------------------------

kerala["Start Date"] = pd.to_datetime(
    kerala["Start Date"],
    errors="coerce",
    dayfirst=True
)

kerala["End Date"] = pd.to_datetime(
    kerala["End Date"],
    errors="coerce",
    dayfirst=True
)


# --------------------------------------------------
# 6. Clean text fields
# --------------------------------------------------

text_columns = [
    "Main Cause",
    "Districts",
    "State",
    "Description of Casualties/injured",
    "Extent of damage",
    "Event Source"
]

for column in text_columns:
    if column in kerala.columns:
        kerala[column] = (
            kerala[column]
            .astype(str)
            .str.strip()
        )


# --------------------------------------------------
# 7. Check whether any event ends before it starts
# --------------------------------------------------

invalid_dates = kerala[
    (kerala["Start Date"].notna()) &
    (kerala["End Date"].notna()) &
    (kerala["End Date"] < kerala["Start Date"])
]

print("\nEvents where End Date is before Start Date:")
print("Count:", len(invalid_dates))

if len(invalid_dates) > 0:

    columns_to_show = [
        "UEI",
        "Start Date",
        "End Date",
        "Duration(Days)",
        "Main Cause",
        "Districts"
    ]

    print(
        invalid_dates[columns_to_show]
        .to_string(index=False)
    )


# --------------------------------------------------
# 8. Check missing values
# --------------------------------------------------

print("\nMissing values in Kerala dataset:")

missing = kerala.isnull().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
)


# --------------------------------------------------
# 9. Display sample Kerala records
# --------------------------------------------------

print("\nSample Kerala records:")

sample_columns = [
    "Start Date",
    "End Date",
    "Main Cause",
    "Districts",
    "Latitude",
    "Longitude",
    "Area Affected",
    "Human fatality",
    "Human injured",
    "Human Displaced"
]

print(
    kerala[sample_columns]
    .head(10)
    .to_string(index=False)
)


# --------------------------------------------------
# 10. Save cleaned Kerala dataset
# --------------------------------------------------

output_path = "data/kerala_flood_events.csv"

kerala.to_csv(
    output_path,
    index=False
)

print("\nCleaned dataset saved to:")
print(output_path)

print("\nFinal shape:", kerala.shape)