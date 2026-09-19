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

API_URL = "https://archive-api.open-meteo.com/v1/archive"

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

# --------------------------------------------------
# Download one district
# --------------------------------------------------

def download_district(district, lat, lon, max_retries=5):

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
        "models": "era5",
    }

    for attempt in range(1, max_retries + 1):

        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=120
            )

            # Rate limit
            if response.status_code == 429:

                wait_time = 60 * attempt

                print(
                    f"[RATE LIMIT] {district} "
                    f"-> waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)
                continue

            # Other API errors
            if response.status_code != 200:

                print(
                    f"[ERROR] {district}: "
                    f"HTTP {response.status_code}"
                )

                print(response.text[:500])

                return None

            data = response.json()

            dates = data["daily"]["time"]
            rainfall = data["daily"]["precipitation_sum"]

            # Check that rainfall exists
            if rainfall is None:
                print(f"[ERROR] {district}: rainfall data is None")
                return None

            # Check that rainfall isn't entirely missing
            valid_values = sum(
                value is not None for value in rainfall
            )

            if valid_values == 0:

                print(
                    f"[ERROR] {district}: "
                    "all rainfall values are missing"
                )

                return None

            district_df = pd.DataFrame({
                "Date": dates,
                "District": district,
                "Rainfall_mm": rainfall,
            })

            district_df["Date"] = pd.to_datetime(
                district_df["Date"]
            )

            print(
                f"[OK] {district}: "
                f"{len(district_df)} days, "
                f"{valid_values} valid rainfall values"
            )

            return district_df

        except requests.RequestException as e:

            print(
                f"[NETWORK ERROR] {district}: {e}"
            )

            if attempt < max_retries:
                wait_time = 10 * attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print(f"[FAILED] {district} after {max_retries} attempts")

    return None


# --------------------------------------------------
# Main
# --------------------------------------------------

all_data = []

for district, (lat, lon) in DISTRICTS.items():

    print(f"\nDownloading {district}...")

    result = download_district(
        district,
        lat,
        lon
    )

    if result is not None:
        all_data.append(result)

    # Prevent API rate limiting
    print("Waiting 5 seconds before next district...")
    time.sleep(5)


# --------------------------------------------------
# Combine
# --------------------------------------------------

if len(all_data) == 0:

    raise RuntimeError(
        "No rainfall data was successfully downloaded."
    )

rainfall_df = pd.concat(
    all_data,
    ignore_index=True
)

rainfall_df = rainfall_df.sort_values(
    ["District", "Date"]
).reset_index(drop=True)


# --------------------------------------------------
# Remove missing rainfall values
# --------------------------------------------------

missing_before = rainfall_df["Rainfall_mm"].isna().sum()

print(
    f"\nMissing rainfall values before cleaning: "
    f"{missing_before}"
)

rainfall_df = rainfall_df.dropna(
    subset=["Rainfall_mm"]
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

rainfall_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# Final verification
# --------------------------------------------------

print("\n======================================")
print("RAINFALL DOWNLOAD COMPLETED")
print("======================================")

print("Shape:", rainfall_df.shape)

print(
    "Date range:",
    rainfall_df["Date"].min(),
    "to",
    rainfall_df["Date"].max()
)

print(
    "Districts:",
    rainfall_df["District"].nunique()
)

print("\nDistrict counts:")
print(
    rainfall_df["District"]
    .value_counts()
    .sort_index()
)

print("\nMissing rainfall:")
print(
    rainfall_df["Rainfall_mm"].isna().sum()
)

print("\nRainfall statistics:")
print(
    rainfall_df["Rainfall_mm"].describe()
)

print("\nSample:")
print(rainfall_df.head(10))

print(f"\nSaved to: {OUTPUT_PATH}")