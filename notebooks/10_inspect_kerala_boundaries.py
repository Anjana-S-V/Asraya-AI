import geopandas as gpd
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

BOUNDARY_PATH = Path(
    "data/kerala_district_boundaries.geojson"
)


# ============================================================
# Step 1 — Check file
# ============================================================

print("Checking boundary file...")

if not BOUNDARY_PATH.exists():
    raise FileNotFoundError(
        f"Boundary file not found:\n{BOUNDARY_PATH}"
    )

print("Found:")
print(BOUNDARY_PATH)


# ============================================================
# Step 2 — Load GeoJSON
# ============================================================

print("\nLoading district boundaries...")

gdf = gpd.read_file(BOUNDARY_PATH)

print("Loaded successfully.")


# ============================================================
# Step 3 — Basic information
# ============================================================

print("\nDataset information")
print("===================")

print("Number of districts:", len(gdf))

print("\nColumns:")
for column in gdf.columns:
    print("-", column)


# ============================================================
# Step 4 — Check CRS
# ============================================================

print("\nCoordinate Reference System")
print("===========================")

print(gdf.crs)


# ============================================================
# Step 5 — District names
# ============================================================

print("\nDistrict names")
print("==============")

if "district" not in gdf.columns:
    raise ValueError(
        "Expected 'district' column was not found."
    )

districts = sorted(
    gdf["district"]
    .astype(str)
    .str.strip()
    .unique()
)

print("Count:", len(districts))

for district in districts:
    print("-", district)


# ============================================================
# Step 6 — Geometry types
# ============================================================

print("\nGeometry types")
print("==============")

print(
    gdf.geometry.geom_type.value_counts()
)


# ============================================================
# Step 7 — Geometry validity
# ============================================================

print("\nGeometry validity")
print("=================")

valid_count = gdf.geometry.is_valid.sum()
invalid_count = (~gdf.geometry.is_valid).sum()

print("Valid geometries:", valid_count)
print("Invalid geometries:", invalid_count)


# ============================================================
# Step 8 — Geographic bounds
# ============================================================

print("\nGeographic bounds")
print("=================")

minx, miny, maxx, maxy = gdf.total_bounds

print("Minimum longitude:", minx)
print("Minimum latitude :", miny)
print("Maximum longitude:", maxx)
print("Maximum latitude :", maxy)


# ============================================================
# Step 9 — Missing geometry check
# ============================================================

print("\nMissing geometry")
print("================")

missing_geometry = gdf.geometry.isna().sum()

print(
    "Districts without geometry:",
    missing_geometry
)


# ============================================================
# Step 10 — Final summary
# ============================================================

print("\nFINAL SUMMARY")
print("=============")

print("[OK] Boundary file loaded")
print("[OK] District count:", len(gdf))
print("[OK] CRS:", gdf.crs)
print("[OK] Valid geometries:", valid_count)
print("[OK] Invalid geometries:", invalid_count)
print("[OK] Missing geometries:", missing_geometry)

print("\nBoundary inspection complete.")