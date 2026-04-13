"""
Generate vaccination_individual_data.js from person_vaccine_tb.xlsx
Aggregates individual vaccination records by facility with vaccine counts
"""
import pandas as pd
import json

# Load the data files
print("Loading data files...")
person_vaccine = pd.read_excel('data/202601310406.xlsx')
vaccine_doses = pd.read_excel('data/vaccine_doses_tb.xlsx')
phc_centers = pd.read_excel('data/phc_center_updated.xlsx')
phc_centers_original = pd.read_excel('data/phc_center_tb.xlsx')
locations = pd.read_csv('data/location_point_unified_corrected.csv')

print(f"Total vaccination records: {len(person_vaccine)}")
print(f"Unique children: {person_vaccine['PERSON_ID'].nunique()}")

# Create vaccine name mapping
vaccine_map = dict(zip(vaccine_doses['VACCINE_DOSES_ID'], vaccine_doses['VACCINE_DOSES_NAME']))
print(f"\nVaccine mapping loaded: {len(vaccine_map)} vaccines")

# Create facility name mapping - use multiple sources
facility_map = {}
facility_map_ar = {}

# First from phc_center_updated
for _, row in phc_centers.iterrows():
    fid = row['PHC_CENTER_ID']
    if pd.notna(row['en_name']):
        facility_map[fid] = row['en_name']
    if pd.notna(row['NAME_AR']):
        facility_map_ar[fid] = row['NAME_AR']

# Fill missing from original phc_center_tb
for _, row in phc_centers_original.iterrows():
    fid = row['PHC_CENTER_ID']
    if fid not in facility_map or pd.isna(facility_map.get(fid)):
        if pd.notna(row['NAME_EN']):
            facility_map[fid] = row['NAME_EN']
        elif pd.notna(row['NAME_AR']):
            facility_map[fid] = row['NAME_AR']  # Use Arabic if no English
    if fid not in facility_map_ar or pd.isna(facility_map_ar.get(fid)):
        if pd.notna(row['NAME_AR']):
            facility_map_ar[fid] = row['NAME_AR']

print(f"Facility mapping loaded: {len(facility_map)} facilities")

# Create coordinates mapping from locations file
coord_map = {}
for _, row in locations.iterrows():
    name_en = str(row['Medical Point - Health Facility Name in English']).strip()
    gov = str(row['Governorate']).strip()
    org = str(row['Organization']).strip() if pd.notna(row['Organization']) else 'Unknown'
    if pd.notna(row['Long']) and pd.notna(row['Lat']):
        coord_map[name_en.lower()] = {
            'lat': float(row['Lat']),
            'lng': float(row['Long']),
            'governorate': gov,
            'organization': org
        }
print(f"Coordinates mapping loaded: {len(coord_map)} locations")

# Default coordinates by governorate (center points) for unmatched facilities
default_coords = {
    'Gaza': {'lat': 31.5017, 'lng': 34.4668},
    'North Gaza': {'lat': 31.5472, 'lng': 34.4903},
    'Middle zone': {'lat': 31.4167, 'lng': 34.3500},
    'Khan Younis': {'lat': 31.3462, 'lng': 34.3060},
    'Rafah': {'lat': 31.2969, 'lng': 34.2452}
}

# Try to map facility IDs to governorates from location_tree
location_tree = {}
try:
    for _, row in phc_centers_original.iterrows():
        fid = row['PHC_CENTER_ID']
        tree_id = str(row['LOCATION_TREE_ID']) if pd.notna(row['LOCATION_TREE_ID']) else ''
        # Tree ID format: XX.YY.ZZ where XX indicates governorate
        if tree_id.startswith('1.1'):
            location_tree[fid] = 'North Gaza'
        elif tree_id.startswith('1.2'):
            location_tree[fid] = 'Gaza'
        elif tree_id.startswith('1.3'):
            location_tree[fid] = 'Middle zone'
        elif tree_id.startswith('1.4'):
            location_tree[fid] = 'Khan Younis'
        elif tree_id.startswith('1.5'):
            location_tree[fid] = 'Rafah'
        else:
            location_tree[fid] = 'Gaza'  # Default
except Exception as e:
    print(f"Warning: Could not parse location tree: {e}")

# Map vaccine names to standard short names for properties
vaccine_short_names = {
    'BCG': 'BCG',
    'Hepatitis B0': 'HepB',
    'IPV 1': 'IPV1',
    'IPV 2': 'IPV2',
    'bOPV 1': 'bOPV1',
    'bOPV 2': 'bOPV2',
    'bOPV 3': 'bOPV3',
    'bOPV 4': 'bOPV4',
    'bOPV 5': 'bOPV5',
    'Rota 1': 'Rota1',
    'Rota 2': 'Rota2',
    'Rota 3': 'Rota3',
    'Penta (DPT, Hib, Hep.B) 1': 'Penta1',
    'Penta (DPT, Hib, Hep.B) 2': 'Penta2',
    'Penta (DPT, Hib, Hep.B) 3': 'Penta3',
    'PCV 1': 'PCV1',
    'PCV 2': 'PCV2',
    'PCV 3': 'PCV3',
    'MMR 1': 'MMR1',
    'MMR 2': 'MMR2',
    'DPT': 'DTP',
    'DPT 1': 'DTP',
    'DT 1': 'DT1',
    'DT 2': 'DT2',
    'DT 3': 'DT3'
}

# Age type mapping (from CHILDREN_AGE_TYPE)
age_type_map = {
    1: 'Age 0-12',      # 0-12 months
    2: 'Age 12-24',     # 12-24 months
    3: 'Age 24+'        # 24+ months
}

# Vaccination status mapping
status_map = {
    1: 'ZeroDose',
    2: 'Defaulter',
    3: 'OnSchedule',
    4: 'Completed'
}

# Aggregate data by facility
print("\nAggregating data by facility...")
facility_data = {}

# First, get the last status for each child (to avoid double counting)
child_last_status = person_vaccine.groupby('PERSON_ID')['CHILD_VACCINATION_STATUS'].last().to_dict()
child_last_age = person_vaccine.groupby('PERSON_ID')['CHILDREN_AGE_TYPE'].last().to_dict()

for _, row in person_vaccine.iterrows():
    fac_id = row['PHC_SERVICE_PROVIDER_ID']
    vaccine_id = row['VACCINE_DOSES_ID']
    person_id = row['PERSON_ID']

    # Get facility name
    fac_name = facility_map.get(fac_id, f"Facility {fac_id}")

    if fac_id not in facility_data:
        facility_data[fac_id] = {
            'name': fac_name,
            'name_ar': facility_map_ar.get(fac_id, ''),
            'children': set(),
            'children_status': {},  # person_id -> status
            'children_age': {},     # person_id -> age_group
            'total_vaccinations': 0,
            'vaccines': {},
        }

    # Add child to unique children set
    facility_data[fac_id]['children'].add(person_id)
    facility_data[fac_id]['total_vaccinations'] += 1

    # Store the child's status and age (will be overwritten but that's ok - we use last)
    facility_data[fac_id]['children_status'][person_id] = child_last_status.get(person_id, 3)
    facility_data[fac_id]['children_age'][person_id] = child_last_age.get(person_id, 1)

    # Count vaccines
    vaccine_name = vaccine_map.get(vaccine_id, f"Vaccine {vaccine_id}")
    short_name = vaccine_short_names.get(vaccine_name, vaccine_name.replace(' ', ''))
    if short_name not in facility_data[fac_id]['vaccines']:
        facility_data[fac_id]['vaccines'][short_name] = 0
    facility_data[fac_id]['vaccines'][short_name] += 1

# Now calculate status and age counts per facility (each child counted once)
for fac_id, data in facility_data.items():
    data['status'] = {'ZeroDose': 0, 'Defaulter': 0, 'OnSchedule': 0, 'Completed': 0}
    data['age_groups'] = {'Age 0-12': 0, 'Age 12-24': 0, 'Age 24+': 0}

    for person_id in data['children']:
        # Status
        status_code = data['children_status'].get(person_id, 3)
        status = status_map.get(status_code, 'OnSchedule')
        if status in data['status']:
            data['status'][status] += 1

        # Age
        age_code = data['children_age'].get(person_id, 1)
        age_group = age_type_map.get(age_code, 'Age 0-12')
        if age_group in data['age_groups']:
            data['age_groups'][age_group] += 1

# Create GeoJSON features
print("\nCreating GeoJSON features...")
features = []
matched_count = 0
unmatched_facilities = []

for fac_id, data in facility_data.items():
    fac_name = data['name']

    # Try to find coordinates
    coords = None
    fac_name_lower = str(fac_name).lower().strip() if fac_name else ''

    # Try exact match first
    if fac_name_lower in coord_map:
        coords = coord_map[fac_name_lower]
    else:
        # Try partial match
        for loc_name, loc_coords in coord_map.items():
            if fac_name_lower and (fac_name_lower in loc_name or loc_name in fac_name_lower):
                coords = loc_coords
                break

    # If no coords found, use default based on governorate
    if not coords:
        gov = location_tree.get(fac_id, 'Gaza')
        default = default_coords.get(gov, default_coords['Gaza'])
        # Add small random offset to avoid overlapping
        import random
        coords = {
            'lat': default['lat'] + random.uniform(-0.02, 0.02),
            'lng': default['lng'] + random.uniform(-0.02, 0.02),
            'governorate': gov,
            'organization': 'Unknown'
        }
        unmatched_facilities.append(fac_name)
    else:
        matched_count += 1

    # Always create feature now
    if coords:
        # Build properties
        props = {
            'Health Facility': fac_name,
            'Health Facility AR': data['name_ar'],
            'Governorate': coords['governorate'],
            'Organization': coords['organization'],
            'TotalChildren': len(data['children']),
            'TotalVaccinations': data['total_vaccinations'],
            'Age 0-12': data['age_groups']['Age 0-12'],
            'Age 12-24': data['age_groups']['Age 12-24'],
            'Age 24+': data['age_groups']['Age 24+'],
            'OnSchedule': data['status']['OnSchedule'],
            'Defaulter': data['status']['Defaulter'],
            'ZeroDose': data['status']['ZeroDose']
        }

        # Add vaccine counts
        for vax_name, count in data['vaccines'].items():
            props[vax_name] = count

        feature = {
            'type': 'Feature',
            'properties': props,
            'geometry': {
                'type': 'Point',
                'coordinates': [coords['lng'], coords['lat']]
            }
        }
        features.append(feature)

print(f"\nMatched facilities: {matched_count}")
print(f"Unmatched facilities: {len(unmatched_facilities)}")
if unmatched_facilities[:10]:
    print("Sample unmatched:", unmatched_facilities[:10])

# Create GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': features
}

# Save to JS file
output_path = 'data/vaccination_individual_data.js'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('var json_vaccination_individual_data = ')
    json.dump(geojson, f, ensure_ascii=False, indent=2)
    f.write(';')

print(f"\nSaved to {output_path}")
print(f"Total features: {len(features)}")

# Print summary statistics
total_children = sum(len(d['children']) for d in facility_data.values())
total_vax = sum(d['total_vaccinations'] for d in facility_data.values())
print(f"\nTotal unique children: {total_children}")
print(f"Total vaccinations: {total_vax}")

# Print vaccine totals
print("\nVaccine totals:")
vaccine_totals = {}
for d in facility_data.values():
    for vax, count in d['vaccines'].items():
        vaccine_totals[vax] = vaccine_totals.get(vax, 0) + count

for vax, count in sorted(vaccine_totals.items(), key=lambda x: -x[1]):
    print(f"  {vax}: {count}")

# Also calculate max values for slider ranges
print("\n\nMax values per facility (for slider ranges):")
max_values = {
    'TotalChildren': 0,
    'TotalVaccinations': 0,
    'OnSchedule': 0,
    'Defaulter': 0,
    'ZeroDose': 0
}

for f in features:
    p = f['properties']
    for key in max_values:
        if key in p and p[key] > max_values[key]:
            max_values[key] = p[key]
    # Also track vaccine maxes
    for vax in vaccine_totals.keys():
        if vax not in max_values:
            max_values[vax] = 0
        if vax in p and p[vax] > max_values[vax]:
            max_values[vax] = p[vax]

for key, val in sorted(max_values.items()):
    print(f"  {key}: {val}")
