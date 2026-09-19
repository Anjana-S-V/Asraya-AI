import pandas as pd


# --------------------------------------------------
# 1. Load cleaned Kerala dataset
# --------------------------------------------------

input_path = "data/kerala_flood_events.csv"

df = pd.read_csv(input_path)

print("Loaded records:", len(df))


# --------------------------------------------------
# 2. Convert dates
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
# 3. Remove records with invalid dates
# --------------------------------------------------

invalid_dates = (
    df["Start Date"].notna()
    & df["End Date"].notna()
    & (df["End Date"] < df["Start Date"])
)

print("Invalid date records:", invalid_dates.sum())

df = df[~invalid_dates].copy()


# --------------------------------------------------
# 4. Remove records without a start date
# --------------------------------------------------

missing_start = df["Start Date"].isna()

print("Missing start-date records:", missing_start.sum())

df = df[~missing_start].copy()


# --------------------------------------------------
# 5. Keep only records with district information
# --------------------------------------------------

missing_district = (
    df["Districts"].isna()
    | (df["Districts"].str.strip() == "")
)

print("Missing district records:", missing_district.sum())

df = df[~missing_district].copy()


# --------------------------------------------------
# 6. Split multi-district events
# --------------------------------------------------

district_events = df.assign(
    District=df["Districts"].str.split(",")
).explode("District")


# --------------------------------------------------
# 7. Clean district names
# --------------------------------------------------

district_events["District"] = (
    district_events["District"]
    .str.strip()
)

# --------------------------------------------------
# 8. Keep only official Kerala districts
# --------------------------------------------------

official_districts = [
    "Alappuzha",
    "Ernakulam",
    "Idukki",
    "Kannur",
    "Kasaragod",
    "Kollam",
    "Kottayam",
    "Kozhikode",
    "Malappuram",
    "Palakkad",
    "Pathanamthitta",
    "Thiruvananthapuram",
    "Thrissur",
    "Wayanad"
]

invalid_district_rows = district_events[
    ~district_events["District"].isin(official_districts)
].copy()

print("\nAmbiguous/non-standard district labels:")
print(
    invalid_district_rows["District"]
    .value_counts()
)

district_events = district_events[
    district_events["District"].isin(official_districts)
].copy()

print(
    "\nValid district-event records:",
    len(district_events)
)

print(
    "Valid districts:",
    district_events["District"].nunique()
)

# --------------------------------------------------
# 8. Select useful columns
# --------------------------------------------------

district_events = district_events[
    [
        "UEI",
        "Start Date",
        "End Date",
        "Duration(Days)",
        "Main Cause",
        "District"
    ]
].copy()


# --------------------------------------------------
# 9. Remove duplicate district-event combinations
# --------------------------------------------------

district_events = district_events.drop_duplicates(
    subset=["UEI", "District"]
)


# --------------------------------------------------
# 10. Display results
# --------------------------------------------------

print("\nDistrict-level event dataset:")
print(district_events.head(20).to_string(index=False))

print("\nNumber of district-event records:")
print(len(district_events))

print("\nNumber of unique districts:")
print(district_events["District"].nunique())

print("\nDistrict frequency:")
print(
    district_events["District"]
    .value_counts()
)


# --------------------------------------------------
# 11. Save
# --------------------------------------------------

output_path = "data/kerala_district_flood_events.csv"

district_events.to_csv(
    output_path,
    index=False
)

print("\nSaved to:")
print(output_path)