import geopandas as gpd
from pathlib import Path


BOUNDARY_PATH = Path(
    "data/kerala_district_boundaries.geojson"
)


print("Loading boundary file...")

gdf = gpd.read_file(BOUNDARY_PATH)

print("CRS reported by GeoPandas:")
print(gdf.crs)

print("\nFirst geometry coordinate sample")
print("===============================")

geometry = gdf.geometry.iloc[0]

# Get the first coordinate from the first polygon
if geometry.geom_type == "MultiPolygon":
    polygon = list(geometry.geoms)[0]
else:
    polygon = geometry

coordinates = list(polygon.exterior.coords)

print("District:", gdf["district"].iloc[0])
print("First 5 coordinates:")

for coordinate in coordinates[:5]:
    print(coordinate)


print("\nReported bounds")
print("===============")

print("Total bounds:")
print(gdf.total_bounds)


print("\nCRS details")
print("===========")

print("CRS:", gdf.crs)
print("CRS name:", gdf.crs.name)

if gdf.crs:
    print("CRS units:", gdf.crs.axis_info[0].unit_name)


print("\nDone.")