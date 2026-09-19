import pandas as pd

# --------------------------------------------------
# 1. Load district-day calendar
# --------------------------------------------------

file_path = "data/kerala_district_daily_calendar.csv"

df = pd.read_csv(file_path)

print("Loaded records:", len(df))

# --------------------------------------------------
# 2. Parse date
# --------------------------------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

# --------------------------------------------------
# 3. Sort correctly
# --------------------------------------------------

df = df.sort_values(
    ["District", "Date"]
).reset_index(drop=True)

# --------------------------------------------------
# 4. Create next-day flood target
# --------------------------------------------------

df["Flood_Tomorrow"] = (
    df.groupby("District")["Flood_Onset"]
    .shift(-1)
)

# --------------------------------------------------
# 5. Remove final day of each district
# --------------------------------------------------

df = df[
    df["Flood_Tomorrow"].notna()
].copy()

df["Flood_Tomorrow"] = (
    df["Flood_Tomorrow"]
    .astype(int)
)

# --------------------------------------------------
# 6. Statistics
# --------------------------------------------------

print("\n==============================")
print("PREDICTION TARGET")
print("==============================")

print(
    "\nTotal observations:",
    len(df)
)

print(
    "Flood tomorrow = 1:",
    df["Flood_Tomorrow"].sum()
)

print(
    "Flood tomorrow = 0:",
    (df["Flood_Tomorrow"] == 0).sum()
)

print(
    "\nFlood tomorrow percentage:",
    round(
        df["Flood_Tomorrow"].mean() * 100,
        3
    ),
    "%"
)

# --------------------------------------------------
# 7. Target distribution by district
# --------------------------------------------------

district_target = (
    df.groupby("District")["Flood_Tomorrow"]
    .agg(
        Total_Days="count",
        Flood_Tomorrow="sum"
    )
)

district_target["Flood_Rate_%"] = (
    district_target["Flood_Tomorrow"]
    / district_target["Total_Days"]
    * 100
)

print("\nTarget distribution by district:")

print(
    district_target
    .sort_values(
        "Flood_Tomorrow",
        ascending=False
    )
    .to_string()
)

# --------------------------------------------------
# 8. Target distribution by year
# --------------------------------------------------

df["Year"] = df["Date"].dt.year

year_target = (
    df.groupby("Year")["Flood_Tomorrow"]
    .agg(
        Total_Days="count",
        Flood_Tomorrow="sum"
    )
)

print("\nTarget distribution by year:")

print(
    year_target.to_string()
)

# --------------------------------------------------
# 9. Check relationship with active flood
# --------------------------------------------------

print(
    "\nObservations where flood is active today"
    " but no new flood begins tomorrow:"
)

condition = (
    (df["Flood_Active"] == 1)
    &
    (df["Flood_Tomorrow"] == 0)
)

print(
    condition.sum()
)

# --------------------------------------------------
# 10. Save
# --------------------------------------------------

df = df.drop(
    columns=["Year"]
)

output_path = (
    "data/kerala_prediction_target.csv"
)

df.to_csv(
    output_path,
    index=False
)

print(
    "\nSaved to:",
    output_path
)

print(
    "Final shape:",
    df.shape
)

# --------------------------------------------------
# 11. Preview positive examples
# --------------------------------------------------

print(
    "\nExamples where flood begins tomorrow:"
)

positive_examples = df[
    df["Flood_Tomorrow"] == 1
]

print(
    positive_examples
    .head(20)
    .to_string(index=False)
)