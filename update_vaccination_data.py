import pandas as pd
import json

# Read the new summary file
df = pd.read_excel('data/summery.xlsx')

# Read location coordinates
locations = pd.read_csv('data/location_point_unified_corrected.csv')

# Create a mapping of facility names to coordinates
loc_map = {}
for idx, row in locations.iterrows():
    name = row['Medical Point - Health Facility Name in English']
    loc_map[name] = {'lat': row['Lat'], 'lon': row['Long']}

print(f'Total summary records: {len(df)}')
print(f'Total location records: {len(locations)}')

# Convert to GeoJSON format
features = []
matched = 0
for idx, row in df.iterrows():
    facility = str(row['Health Facility']) if pd.notna(row['Health Facility']) else ""

    # Try to find coordinates
    lat, lon = 0, 0
    if facility in loc_map:
        lat = loc_map[facility]['lat']
        lon = loc_map[facility]['lon']
        matched += 1

    feature = {
        "type": "Feature",
        "properties": {
            "ObjectID": int(row['ObjectID']) if pd.notna(row['ObjectID']) else 0,
            "Governorate": str(row['Governorate']) if pd.notna(row['Governorate']) else "",
            "Health_Facility": facility,
            "Report_Date": str(row['Report Date']) if pd.notna(row['Report Date']) else "",
            "Supervisor": str(row['Suppervisor Name']) if pd.notna(row['Suppervisor Name']) else "",
            "all_child": int(row['all_child']) if pd.notna(row['all_child']) else 0,
            "BCG": int(row['BCG']) if pd.notna(row['BCG']) else 0,
            "Hep": int(row['Hep']) if pd.notna(row['Hep']) else 0,
            "IPV1": int(row['IPV1']) if pd.notna(row['IPV1']) else 0,
            "IPV2": int(row['IPV2']) if pd.notna(row['IPV2']) else 0,
            "Penta1": int(row['Penta1']) if pd.notna(row['Penta1']) else 0,
            "Penta2": int(row['Penta2']) if pd.notna(row['Penta2']) else 0,
            "Penta3": int(row['Penta3']) if pd.notna(row['Penta3']) else 0,
            "bOPV1": int(row['bOPV1']) if pd.notna(row['bOPV1']) else 0,
            "bOPV2": int(row['bOPV2']) if pd.notna(row['bOPV2']) else 0,
            "bOPV3": int(row['bOPV3']) if pd.notna(row['bOPV3']) else 0,
            "bOPV4": int(row['bOPV4']) if pd.notna(row['bOPV4']) else 0,
            "bOPV5": int(row['bOPV5']) if pd.notna(row['bOPV5']) else 0,
            "Rota1": int(row['Rota1']) if pd.notna(row['Rota1']) else 0,
            "Rota2": int(row['Rota2']) if pd.notna(row['Rota2']) else 0,
            "Rota3": int(row['Rota3']) if pd.notna(row['Rota3']) else 0,
            "PCV1": int(row['PCV1']) if pd.notna(row['PCV1']) else 0,
            "PCV2": int(row['PCV2']) if pd.notna(row['PCV2']) else 0,
            "PCV3": int(row['PCV3']) if pd.notna(row['PCV3']) else 0,
            "MMR1": int(row['MMR1']) if pd.notna(row['MMR1']) else 0,
            "MMR2": int(row['MMR2']) if pd.notna(row['MMR2']) else 0,
            "DTP": int(row['DTP']) if pd.notna(row['DTP']) else 0,
            "DT": int(row['DT']) if pd.notna(row['DT']) else 0,
            "Td": int(row['Td']) if pd.notna(row['Td']) else 0,
            "Zero_Dose": int(row['Vaccination status of a Child | Zero Dose']) if pd.notna(row['Vaccination status of a Child | Zero Dose']) else 0,
            "Defaulter": int(row['Vaccination status of a Child | Defaulter']) if pd.notna(row['Vaccination status of a Child | Defaulter']) else 0,
            "On_Schedule": int(row['Vaccination status of a Child | On Schedule']) if pd.notna(row['Vaccination status of a Child | On Schedule']) else 0,
            "Age_0_12": int(row['Total Children Vaccinated by Age | 0 to 12']) if pd.notna(row['Total Children Vaccinated by Age | 0 to 12']) else 0,
            "Age_12_24": int(row['Total Children Vaccinated by Age | 12 to 24']) if pd.notna(row['Total Children Vaccinated by Age | 12 to 24']) else 0,
            "Age_above_24": int(row['Total Children Vaccinated by Age | above 24']) if pd.notna(row['Total Children Vaccinated by Age | above 24']) else 0,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print(f'Matched coordinates: {matched}')

# Save as JS file (overwrite old vaccination_data.js)
with open('data/vaccination_data.js', 'w', encoding='utf-8') as f:
    f.write('var vaccinationData = ')
    json.dump(geojson, f, ensure_ascii=False)
    f.write(';')

print('Updated: data/vaccination_data.js')

# Print statistics
print('\n=== Summary Statistics ===')
print(f"Total Records: {len(df)}")
print(f"Total Children: {int(df['all_child'].sum()):,}")
print(f"BCG: {int(df['BCG'].sum()):,}")
print(f"Penta1: {int(df['Penta1'].sum()):,}")
print(f"Penta2: {int(df['Penta2'].sum()):,}")
print(f"Penta3: {int(df['Penta3'].sum()):,}")
print(f"MMR1: {int(df['MMR1'].sum()):,}")
print(f"MMR2: {int(df['MMR2'].sum()):,}")
