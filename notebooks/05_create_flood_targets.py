import pandas as pd

# --------------------------------------------------
# 1. Load district-level flood events
# --------------------------------------------------

file_path = "data/kerala_district_flood_events.csv"

df = pd.read_csv(file_path)

print("Loaded records:", len(df))

# --------------------------------------------------
# 2. Parse dates
# --------------------------------------------------

df["Start Date"] = pd.to_datetime(
    df["Start Date"],
    errors="coerce"
)

# --------------------------------------------------
# 3. Keep the rainfall-overlap period
# --------------------------------------------------

df = df[
    (df["Start Date"].dt.year >= 1998) &
    (df["Start Date"].dt.year <= 2023)
].copy()

print(
    "\nRecords from 1998-2023:",
    len(df)
)

# --------------------------------------------------
# 4. Remove records without dates
# --------------------------------------------------

df = df[
    df["Start Date"].notna()
].copy()

# --------------------------------------------------
# 5. Create canonical district-date targets
# --------------------------------------------------

target = (
    df[
        ["District", "Start Date"]
    ]
    .drop_duplicates()
    .copy()
)

target["Flood_Event"] = 1

# --------------------------------------------------
# 6. Sort
# --------------------------------------------------

target = target.sort_values(
    ["District", "Start Date"]
).reset_index(drop=True)

# --------------------------------------------------
# 7. Statistics
# --------------------------------------------------

print(
    "\nUnique district-date flood events:",
    len(target)
)

print(
    "Number of districts:",
    target["District"].nunique()
)

print(
    "Date range:",
    target["Start Date"].min(),
    "to",
    target["Start Date"].max()
)

# --------------------------------------------------
# 8. Events per district
# --------------------------------------------------

print(
    "\nFlood-event observations by district:"
)

print(
    target["District"]
    .value_counts()
    .sort_values(ascending=False)
    .to_string()
)

# --------------------------------------------------
# 9. Events per year
# --------------------------------------------------

target["Year"] = target["Start Date"].dt.year

print(
    "\nFlood-event observations by year:"
)

print(
    target.groupby("Year")
    .size()
    .to_string()
)

# --------------------------------------------------
# 10. Save
# --------------------------------------------------

target = target.drop(
    columns=["Year"]
)

output_path = (
    "data/kerala_flood_targets.csv"
)

target.to_csv(
    output_path,
    index=False
)

print(
    "\nSaved to:",
    output_path
)

print(
    "\nFinal shape:",
    target.shape
)

# --------------------------------------------------
# 11. Preview
# --------------------------------------------------

print("\nSample:")

print(
    target.head(20)
    .to_string(index=False)
)