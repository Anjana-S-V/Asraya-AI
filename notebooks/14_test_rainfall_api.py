import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 9.2648,
    "longitude": 76.7870,
    "start_date": "1998-01-01",
    "end_date": "2023-07-23",
    "daily": "precipitation_sum",
    "timezone": "Asia/Kolkata",
    "models": "era5",
}

print("Requesting Pathanamthitta rainfall...")

response = requests.get(
    url,
    params=params,
    timeout=60
)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit

data = response.json()

print("\nAvailable keys:")
print(data.keys())

print("\nDaily keys:")
print(data["daily"].keys())

print("\nFirst 10 rainfall values:")
print(data["daily"]["precipitation_sum"][:10])

print("\nFirst 10 dates:")
print(data["daily"]["time"][:10])