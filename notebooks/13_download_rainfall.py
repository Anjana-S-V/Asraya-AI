import pandas as pd
import requests
from pathlib import Path
import time

# --------------------------------------------------
# Configuration
# --------------------------------------------------

OUTPUT_PATH = Path("data/kerala_district_rainfall.csv")

START_DATE = "1998-01-01"
END_DATE = "2023-07-23"

# Approximate coordinates for the 14 Kerala districts.
# These are used as representative points for the MVP.
DISTRICTS = {
    "Alappuzha": (9.4981, 76.3388),
    "Ernakulam": (9.9816, 76.2999),
    "Idukki": (9.9189, 76.9440),
    "Kannur": (11.8745, 75.3704),
    "Kasaragod": (12.5102, 74.9852),
    "Kollam": (8.8932, 76.6141),
    "Kottayam": (9.5916, 76.5222),
    "Kozhikode": (11.2588, 75.7804),
    "Malappuram": (11.0510, 76.0711),
    "Palakkad": (10.7867, 76.6548),
    "Pathanamthitta": (9.2648, 76.7870),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Thrissur": (10.5276, 76.2144),
    "Wayanad": (11.6854, 76.1320),
}

API_URL = "https://archive-api.open-meteo.com/v1/archive"

# --------------------------------------------------
# Download rainfall
# --------------------------------------------------

all_data = []

for district, (lat, lon) in DISTRICTS.items():

    print(f"\nDownloading rainfall for {district}...")

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
        "models": "era5_land",
    }

    response = requests.get(API_URL, params=params, timeout=60)

    if response.status_code != 200:
        print(f"[ERROR] {district}: {response.status_code}")
        print(response.text[:500])
        continue

    data = response.json()

    dates = data["daily"]["time"]
    rainfall = data["daily"]["precipitation_sum"]

    district_df = pd.DataFrame({
        "Date": dates,
        "District": district,
        "Rainfall_mm": rainfall,
    })

    all_data.append(district_df)

    print(f"[OK] {district}: {len(district_df)} days")

    time.sleep(1)


# --------------------------------------------------
# Combine
# --------------------------------------------------

if not all_data:
    raise RuntimeError("No rainfall data was downloaded.")

rainfall_df = pd.concat(all_data, ignore_index=True)

rainfall_df["Date"] = pd.to_datetime(rainfall_df["Date"])

rainfall_df = rainfall_df.sort_values(
    ["District", "Date"]
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

rainfall_df.to_csv(OUTPUT_PATH, index=False)

print("\n--------------------------------------")
print("Rainfall download completed")
print("--------------------------------------")

print("Shape:", rainfall_df.shape)
print("Date range:", rainfall_df["Date"].min(), "to", rainfall_df["Date"].max())
print("Districts:", rainfall_df["District"].nunique())

print("\nMissing rainfall:")
print(rainfall_df["Rainfall_mm"].isna().sum())

print("\nSample:")
print(rainfall_df.head(10))

print(f"\nSaved to: {OUTPUT_PATH}")