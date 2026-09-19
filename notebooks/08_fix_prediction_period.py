import pandas as pd

input_path = "data/kerala_prediction_target.csv"
output_path = "data/kerala_prediction_target_final.csv"

df = pd.read_csv(input_path)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

print("Original shape:", df.shape)
print("Original date range:", df["Date"].min(), "to", df["Date"].max())

# The flood inventory ends on July 23, 2023.
SOURCE_END_DATE = pd.Timestamp("2023-07-23")

# Keep only dates covered by the flood inventory.
df = df[df["Date"] <= SOURCE_END_DATE].copy()

print("\nAfter applying source coverage limit:")
print("Shape:", df.shape)
print("Date range:", df["Date"].min(), "to", df["Date"].max())

print("\nFlood_Tomorrow distribution:")
print(df["Flood_Tomorrow"].value_counts())

print("\nFlood_Tomorrow percentage:")
print(
    (df["Flood_Tomorrow"].mean() * 100),
    "%"
)

print("\nObservations by district:")
print(
    df.groupby("District")
      .size()
      .sort_values(ascending=False)
)

df.to_csv(output_path, index=False)

print("\nFinal dataset saved to:")
print(output_path)