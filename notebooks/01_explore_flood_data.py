import pandas as pd

# --------------------------------------------------
# 1. Load the dataset
# --------------------------------------------------

file_path = "data/India_Flood_Inventory_v3.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Shape:", df.shape)

# --------------------------------------------------
# 2. Look at the columns
# --------------------------------------------------

print("\nColumns:")
for column in df.columns:
    print("-", column)

# --------------------------------------------------
# 3. Look at the first 5 records
# --------------------------------------------------

print("\nFirst 5 records:")
print(df.head())

# --------------------------------------------------
# 4. Basic information
# --------------------------------------------------

print("\nDataset information:")
print(df.info())

# --------------------------------------------------
# 5. Missing values
# --------------------------------------------------

print("\nMissing values:")
print(df.isnull().sum())

# --------------------------------------------------
# 6. Filter Kerala
# --------------------------------------------------

kerala = df[
    df["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "kerala"
].copy()

print("\nKerala records:", len(kerala))

# --------------------------------------------------
# 7. Kerala event dates
# --------------------------------------------------

kerala["Start Date"] = pd.to_datetime(
    kerala["Start Date"],
    errors="coerce"
)

print("\nKerala date range:")
print("From:", kerala["Start Date"].min())
print("To:", kerala["Start Date"].max())

# --------------------------------------------------
# 8. Main causes
# --------------------------------------------------

print("\nMain causes in Kerala:")
print(
    kerala["Main Cause"]
    .value_counts(dropna=False)
    .head(20)
)

# --------------------------------------------------
# 9. Districts
# --------------------------------------------------

print("\nDistrict information:")
print(
    kerala["Districts"]
    .value_counts(dropna=False)
    .head(30)
)