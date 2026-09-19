
import json
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

# Change this filename if your downloaded file has a different name.
INPUT_PATH = Path("data/district_nwic.GeoJSON")

# Kerala-only output
OUTPUT_PATH = Path(
    "data/kerala_district_boundaries.geojson"
)


# These are the 14 official Kerala districts
EXPECTED_DISTRICTS = {
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
    "Wayanad",
}


# ============================================================
# Step 1 — Check input file
# ============================================================

print("Checking input file...")

if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"\nBoundary file not found:\n{INPUT_PATH}\n\n"
        "Make sure the downloaded GeoJSON file is inside "
        "the data/ folder and has the correct filename."
    )

print("Found:")
print(INPUT_PATH)


# ============================================================
# Step 2 — Load GeoJSON
# ============================================================

print("\nLoading GeoJSON...")

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

print("GeoJSON loaded successfully.")


# ============================================================
# Step 3 — Validate GeoJSON structure
# ============================================================

print("\nChecking GeoJSON structure...")

if data.get("type") != "FeatureCollection":
    raise ValueError(
        "The file is not a GeoJSON FeatureCollection."
    )

features = data.get("features", [])

if not features:
    raise ValueError(
        "The GeoJSON file contains no features."
    )

print("GeoJSON type: FeatureCollection")
print("Total features:", len(features))


# ============================================================
# Step 4 — Inspect available properties
# ============================================================

print("\nAvailable property fields:")

properties = features[0].get("properties", {})

if not properties:
    raise ValueError(
        "The first feature does not contain properties."
    )

for field in properties.keys():
    print("-", field)


# ============================================================
# Step 5 — Find district-name field
# ============================================================

possible_district_fields = [
    "DISTRICT",
    "District",
    "district",
    "DTNAME",
    "dtname",
    "NAME",
    "Name",
    "name",
    "NAME_2",
    "DIST_NAME",
    "district_name",
]


district_field = None

for field in possible_district_fields:
    if field in properties:
        district_field = field
        break


if district_field is None:
    raise ValueError(
        "\nCould not automatically identify the "
        "district-name field.\n\n"
        "Look at the 'Available property fields' "
        "printed above and tell me the appropriate "
        "district field."
    )


print("\nDistrict-name field detected:")
print(district_field)


# ============================================================
# Step 6 — Extract district names
# ============================================================

print("\nReading district names...")

all_districts = set()

for feature in features:

    properties = feature.get("properties", {})

    district = properties.get(district_field)

    if district is None:
        continue

    district = str(district).strip()

    if district:
        all_districts.add(district)


print("\nUnique district names found:")
print("Count:", len(all_districts))

for district in sorted(all_districts):
    print("-", district)


# ============================================================
# Step 7 — Find Kerala districts
# ============================================================

print("\nSearching for the 14 Kerala districts...")

kerala_features = []

for feature in features:

    properties = feature.get("properties", {})

    district = properties.get(district_field)

    if district is None:
        continue

    district = str(district).strip()

    if district in EXPECTED_DISTRICTS:
        kerala_features.append(feature)


found_districts = {
    str(
        feature["properties"][district_field]
    ).strip()
    for feature in kerala_features
}


# ============================================================
# Step 8 — Validate districts
# ============================================================

print("\nValidation")
print("==========")

print(
    "Expected Kerala districts:",
    len(EXPECTED_DISTRICTS)
)

print(
    "Found Kerala districts:",
    len(found_districts)
)

print(
    "Kerala polygon features:",
    len(kerala_features)
)


# ------------------------------------------------------------
# Missing districts
# ------------------------------------------------------------

missing_districts = (
    EXPECTED_DISTRICTS - found_districts
)

if missing_districts:

    print("\nMISSING DISTRICTS:")

    for district in sorted(missing_districts):
        print("-", district)


# ------------------------------------------------------------
# Unexpected possible Kerala names
# ------------------------------------------------------------

unexpected_districts = (
    found_districts - EXPECTED_DISTRICTS
)

if unexpected_districts:

    print("\nUnexpected district names:")

    for district in sorted(unexpected_districts):
        print("-", district)


# ------------------------------------------------------------
# Stop if validation failed
# ------------------------------------------------------------

if missing_districts:

    raise ValueError(
        "\nDistrict validation failed.\n"
        "One or more expected Kerala districts "
        "could not be matched."
    )


if len(kerala_features) != 14:

    raise ValueError(
        "\nExpected exactly 14 Kerala polygons, "
        f"but found {len(kerala_features)}."
    )


# ============================================================
# Step 9 — Print successful district list
# ============================================================

print("\nAll expected districts found:")

for district in sorted(found_districts):
    print("[OK]", district)


# ============================================================
# Step 10 — Create Kerala-only GeoJSON
# ============================================================

kerala_geojson = {
    "type": "FeatureCollection",
    "features": kerala_features
}


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        kerala_geojson,
        file,
        ensure_ascii=False
    )


# ============================================================
# Step 11 — Final verification
# ============================================================

print("\nFinal verification...")

with open(
    OUTPUT_PATH,
    "r",
    encoding="utf-8"
) as file:

    saved_data = json.load(file)


saved_features = saved_data.get(
    "features",
    []
)


if len(saved_features) != 14:

    raise ValueError(
        "Final GeoJSON verification failed."
    )


print("[OK] GeoJSON is valid")
print("[OK] 14 Kerala districts found")
print("[OK] 14 district polygons extracted")
print("[OK] Kerala-only GeoJSON saved")


# ============================================================
# Done
# ============================================================

print("\nSUCCESS")
print("=======")

print(
    "Output file:"
)

print(OUTPUT_PATH)

print(
    "\nWe are ready for the next step:"
)

print(
    "Rainfall data -> district-level rainfall features"
)

