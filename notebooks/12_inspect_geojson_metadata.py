import json
from pathlib import Path


FILE_PATH = Path(
    "data/district_nwic.GeoJSON"
)


print("Loading raw GeoJSON...")
print(FILE_PATH)

with open(
    FILE_PATH,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


print("\nTop-level GeoJSON keys")
print("======================")

for key in data.keys():
    print("-", key)


print("\nCRS metadata")
print("============")

if "crs" in data:
    print(json.dumps(
        data["crs"],
        indent=2
    ))
else:
    print("No CRS metadata found.")


print("\nFirst feature properties")
print("========================")

features = data.get(
    "features",
    []
)

if features:
    print(
        json.dumps(
            features[0].get("properties", {}),
            indent=2
        )
    )


print("\nFirst coordinate")
print("================")

if features:

    geometry = features[0].get(
        "geometry",
        {}
    )

    print(
        "Geometry type:",
        geometry.get("type")
    )

    coordinates = geometry.get(
        "coordinates"
    )

    print(
        "Coordinate structure found:",
        coordinates is not None
    )

    # Print a small portion only
    print(
        "First coordinate data:"
    )
    print(
        str(coordinates)[:1000]
    )


print("\nDone.")