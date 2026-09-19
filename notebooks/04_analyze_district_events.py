import pandas as pd

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

file_path = "data/kerala_district_flood_events.csv"

df = pd.read_csv(file_path)

print("Dataset shape:", df.shape)

# --------------------------------------------------
# 2. Parse dates
# --------------------------------------------------

df["Start Date"] = pd.to_datetime(
    df["Start Date"],
    errors="coerce"
)

df["End Date"] = pd.to_datetime(
    df["End Date"],
    errors="coerce"
)

# --------------------------------------------------
# 3. Basic information
# --------------------------------------------------

print("\nDate range:")
print("Start:", df["Start Date"].min())
print("End:", df["Start Date"].max())

print("\nNumber of unique flood events:")
print(df["UEI"].nunique())

print("\nNumber of districts:")
print(df["District"].nunique())

# --------------------------------------------------
# 4. Events by year
# --------------------------------------------------

df["Year"] = df["Start Date"].dt.year

events_by_year = (
    df.groupby("Year")["UEI"]
    .nunique()
)

print("\nUnique flood events by year:")
print(events_by_year.to_string())

# --------------------------------------------------
# 5. District-event records by year
# --------------------------------------------------

district_events_by_year = (
    df.groupby("Year")
    .size()
)

print("\nDistrict-event records by year:")
print(district_events_by_year.to_string())

# --------------------------------------------------
# 6. Flood events by district
# --------------------------------------------------

events_by_district = (
    df.groupby("District")["UEI"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nUnique flood events by district:")
print(events_by_district.to_string())

# --------------------------------------------------
# 7. Main causes
# --------------------------------------------------

print("\nMain causes:")

causes = (
    df["Main Cause"]
    .value_counts(dropna=False)
)

print(causes.to_string())

# --------------------------------------------------
# 8. Event duration statistics
# --------------------------------------------------

print("\nEvent duration statistics:")

print(
    df["Duration(Days)"]
    .describe()
)

# --------------------------------------------------
# 9. District-date duplicates
# --------------------------------------------------

district_date_duplicates = (
    df.groupby(
        ["District", "Start Date"]
    )
    .size()
    .sort_values(ascending=False)
)

print("\nLargest district/date groups:")

print(
    district_date_duplicates
    .head(20)
    .to_string()
)

# --------------------------------------------------
# 10. Multiple events affecting same district
# --------------------------------------------------

multiple_events = (
    df.groupby(
        ["District", "Start Date"]
    )["UEI"]
    .nunique()
)

print(
    "\nDistrict/date combinations with multiple unique events:"
)

print(
    (multiple_events > 1)
    .sum()
)

# --------------------------------------------------
# 11. Missing values
# --------------------------------------------------

print("\nMissing values:")

missing = df.isnull().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
    .to_string()
)

# --------------------------------------------------
# 12. Sample
# --------------------------------------------------

print("\nSample records:")

print(
    df.head(20).to_string(index=False)
)