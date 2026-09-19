import pandas as pd

# --------------------------------------------------
# 1. Load flood event data
# --------------------------------------------------

file_path = "data/kerala_district_flood_events.csv"

df = pd.read_csv(file_path)

print("Loaded district-event records:", len(df))

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

# Remove records without valid start/end dates
df = df[
    df["Start Date"].notna() &
    df["End Date"].notna()
].copy()

# Keep the rainfall-overlap period
df = df[
    (df["Start Date"].dt.year >= 1998) &
    (df["Start Date"].dt.year <= 2023)
].copy()

# --------------------------------------------------
# 3. Create list of official districts
# --------------------------------------------------

districts = sorted(
    df["District"].dropna().unique()
)

print("\nDistricts:", len(districts))
print(districts)

# --------------------------------------------------
# 4. Create complete date range
# --------------------------------------------------

start_date = pd.Timestamp("1998-01-01")
end_date = pd.Timestamp("2023-12-31")

dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)

print("\nNumber of calendar days:", len(dates))

# --------------------------------------------------
# 5. Create district × date combinations
# --------------------------------------------------

calendar = pd.MultiIndex.from_product(
    [districts, dates],
    names=["District", "Date"]
).to_frame(index=False)

print(
    "\nTotal district-day observations:",
    len(calendar)
)

# --------------------------------------------------
# 6. Create event onset table
# --------------------------------------------------

onsets = (
    df[
        ["District", "Start Date"]
    ]
    .drop_duplicates()
    .rename(
        columns={
            "Start Date": "Date"
        }
    )
)

onsets["Flood_Onset"] = 1

# --------------------------------------------------
# 7. Create active flood periods
# --------------------------------------------------

active_periods = []

for _, row in df.iterrows():

    dates_active = pd.date_range(
        start=row["Start Date"],
        end=row["End Date"],
        freq="D"
    )

    for date in dates_active:

        active_periods.append(
            {
                "District": row["District"],
                "Date": date
            }
        )

active = pd.DataFrame(active_periods)

if len(active) > 0:

    active = (
        active
        .drop_duplicates()
    )

    active["Flood_Active"] = 1

# --------------------------------------------------
# 8. Merge onset information
# --------------------------------------------------

calendar = calendar.merge(
    onsets,
    on=["District", "Date"],
    how="left"
)

calendar["Flood_Onset"] = (
    calendar["Flood_Onset"]
    .fillna(0)
    .astype(int)
)

# --------------------------------------------------
# 9. Merge active-period information
# --------------------------------------------------

if len(active) > 0:

    calendar = calendar.merge(
        active,
        on=["District", "Date"],
        how="left"
    )

else:

    calendar["Flood_Active"] = 0

calendar["Flood_Active"] = (
    calendar["Flood_Active"]
    .fillna(0)
    .astype(int)
)

# --------------------------------------------------
# 10. Create clean non-flood indicator
# --------------------------------------------------

calendar["Clean_NonFlood"] = (
    (
        calendar["Flood_Onset"] == 0
    )
    &
    (
        calendar["Flood_Active"] == 0
    )
).astype(int)

# --------------------------------------------------
# 11. Basic statistics
# --------------------------------------------------

print("\n==============================")
print("CALENDAR STATISTICS")
print("==============================")

print(
    "\nTotal district-days:",
    len(calendar)
)

print(
    "Flood onset days:",
    calendar["Flood_Onset"].sum()
)

print(
    "Flood active days:",
    calendar["Flood_Active"].sum()
)

print(
    "Clean non-flood days:",
    calendar["Clean_NonFlood"].sum()
)

print(
    "\nFlood onset percentage:",
    round(
        calendar["Flood_Onset"].mean() * 100,
        3
    ),
    "%"
)

# --------------------------------------------------
# 12. Check relationship between onset and active
# --------------------------------------------------

print("\nOnset days that are also active:")

print(
    (
        (calendar["Flood_Onset"] == 1)
        &
        (calendar["Flood_Active"] == 1)
    ).sum()
)

# --------------------------------------------------
# 13. District-level statistics
# --------------------------------------------------

district_stats = (
    calendar
    .groupby("District")
    .agg(
        Total_Days=("Date", "count"),
        Flood_Onsets=("Flood_Onset", "sum"),
        Flood_Active_Days=("Flood_Active", "sum"),
        Clean_NonFlood_Days=("Clean_NonFlood", "sum")
    )
    .sort_values(
        "Flood_Onsets",
        ascending=False
    )
)

print("\nDistrict statistics:")

print(
    district_stats.to_string()
)

# --------------------------------------------------
# 14. Save complete calendar
# --------------------------------------------------

output_path = (
    "data/kerala_district_daily_calendar.csv"
)

calendar.to_csv(
    output_path,
    index=False
)

print(
    "\nSaved to:",
    output_path
)

print(
    "\nFinal shape:",
    calendar.shape
)

# --------------------------------------------------
# 15. Preview
# --------------------------------------------------

print("\nSample rows:")

print(
    calendar.head(20)
    .to_string(index=False)
)