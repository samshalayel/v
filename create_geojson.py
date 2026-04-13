import csv
import json

# Read CSV file
with open('../qgis2web_2026_01_21-18_29_03_916612/location_point_unified_corrected.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in CSV: {len(rows)}")

# Load aggregated data
with open('aggregated_data.json', 'r', encoding='utf-8') as f:
    aggregated = json.load(f)

print(f"Total facilities in aggregated data: {len(aggregated)}")

# Create GeoJSON features
features = []
matched = 0
unmatched = []

for row in rows:
    facility_name_en = row['Medical Point - Health Facility Name in English'].strip()
    facility_name_ar = row['Medical Point - Health Facility Name in Arabic'].strip()
    lon = float(row['Long'])
    lat = float(row['Lat'])
    org = row['Teams Organization'].strip()

    # Try to match with aggregated data
    agg_data = aggregated.get(facility_name_en)

    if agg_data:
        matched += 1
        # Create feature with aggregated data
        feature = {
            "type": "Feature",
            "properties": {
                "Medical Point - Health Facility Name in English": facility_name_en,
                "Medical Point - Health Facility Name in Arabic": facility_name_ar,
                "Teams Organization": org,
                "Aggregated_all_child": agg_data.get("all_child", 0),
                "Aggregated_Vaccination status of a Child | On Schedule": agg_data.get("Vaccination status of a Child | On Schedule", 0),
                "Aggregated_Total Children Vaccinated by Age | above 24": agg_data.get("Total Children Vaccinated by Age | above 24", 0),
                "Aggregated_Total Children Vaccinated by Age | 0 to 12": agg_data.get("Total Children Vaccinated by Age | 0 to 12", 0)
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        }
        features.append(feature)
    else:
        unmatched.append(facility_name_en)

print(f"\nMatched facilities: {matched}")
print(f"Unmatched facilities: {len(unmatched)}")

if unmatched:
    print("\nUnmatched facilities (first 10):")
    for name in unmatched[:10]:
        print(f"  - {name}")

# Create final GeoJSON
geojson = {
    "type": "FeatureCollection",
    "name": "location_point_unified_corrected_1",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": features
}

# Write to JS file
with open('data/location_point_unified_corrected_1.js', 'w', encoding='utf-8') as f:
    f.write('var json_location_point_unified_corrected_1 = ')
    json.dump(geojson, f, ensure_ascii=False)

print(f"\n✓ Created new GeoJSON file with {len(features)} features")
print("✓ File saved to: data/location_point_unified_corrected_1.js")
