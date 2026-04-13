import pandas as pd
import csv
import json

# 1. Read PHC centers
phc_df = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/phc_center_updated.xlsx')
phc_names = {}
for _, row in phc_df.iterrows():
    phc_id = int(row['PHC_CENTER_ID'])
    en_name = ''
    if pd.notna(row['en_name']) and str(row['en_name']).strip():
        en_name = str(row['en_name']).strip()
    elif pd.notna(row['NAME_EN']) and str(row['NAME_EN']).strip():
        en_name = str(row['NAME_EN']).strip()

    ar_name = ''
    if pd.notna(row['ar_name']) and str(row['ar_name']).strip():
        ar_name = str(row['ar_name']).strip()
    elif pd.notna(row['NAME_AR']) and str(row['NAME_AR']).strip():
        ar_name = str(row['NAME_AR']).strip()

    phc_names[phc_id] = {'en_name': en_name, 'ar_name': ar_name}

print(f"PHC Centers loaded: {len(phc_names)}")

# 2. Read location file
locations_en = {}
locations_ar = {}
with open('C:/Users/Administrator/gaza_vaccination/data/location_point_unified_corrected.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name_en = row['Medical Point - Health Facility Name in English'].strip()
        name_ar = row['Medical Point - Health Facility Name in Arabic'].strip()
        gov = row['Governorate'].strip()
        org = row['Organization'].strip()
        lon = float(row['Long']) if row['Long'] else 0
        lat = float(row['Lat']) if row['Lat'] else 0

        if lon > 0 and lat > 0:
            loc_data = {'lon': lon, 'lat': lat, 'gov': gov, 'org': org, 'name_en': name_en, 'name_ar': name_ar}
            locations_en[name_en] = loc_data
            locations_en[name_en.lower()] = loc_data
            locations_ar[name_ar] = loc_data

print(f"Locations loaded: {len(locations_en)}")

# 3. Manual mappings
manual_map = {
    12: 'Juzoor of Al-Atatreh',
    18: 'Jabalia Medical Clinic',
    26: 'Masqat Al Sabra PHC',
    51: 'Al-Baraka Medical Center',
    100: 'Gaza Town',
    101: 'Rimal MP-Rimal Elem. Co-ed "A" & "B"',
    104: 'Burij Health Center',
    105: 'West Nusairat Health Center',
    125: 'Jabalia Medical Clinic',
    131: 'Al-Kuwaiti Hospital - Palestinian Red Crescent Society',
    132: 'Red Crescent Medical Point -Alamin Aleamu',
    205: 'UK MED FIXED PHC',
    219: 'ICRC Fiel Hospital',
    225: 'Al-Bahr Primary Health Care Center /MdM F',
    252: 'Al-Kuwaiti Hospital - Palestinian Red Crescent Society',
    256: 'Al Awda Medical Center',
    258: 'Juzoor Halima Al-Saadia',
    259: 'Tal Al Rabie School (MSF) point',
    260: 'Al Forsan Medical Center',
    263: 'Hamad HC - UNRWA',
    264: 'Emergency NGO - PHC Clinic Al Qarara - Khan Yunis',
    265: 'Kh/Younis Prep. Boys "A"',
    269: 'Emargancy Rafah',
    270: 'Emargancy Rafah',
    290: 'IMC field hospital - Middle Area',
    302: 'Tayara Clinic',
    307: 'Japanese HC - UNRWA',
    312: 'Al Aqsa Hospital',
    322: 'Khanyounis Martyrs Primary Healthcare Center',
    323: 'Nuseirat Martyrs Center',
    328: 'Emargancy Rafah',
    257: 'Al Awda Hospital - Nuseirat',
}

# 4. Read vaccination data
vax_df = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/sss.xlsx')
print(f"Vaccination records: {len(vax_df)}")

# 5. Vaccine and status mappings
vaccine_map = {
    1: 'BCG', 2: 'HepB', 3: 'IPV1', 4: 'IPV2',
    5: 'bOPV1', 6: 'bOPV2', 7: 'bOPV3', 8: 'bOPV4', 21: 'bOPV5',
    9: 'Rota1', 10: 'Rota2', 11: 'Rota3',
    12: 'Penta1', 13: 'Penta2', 14: 'Penta3',
    15: 'PCV1', 16: 'PCV2', 17: 'PCV3',
    18: 'MMR1', 19: 'MMR2', 20: 'DTP',
}

age_map = {1: 'Age 0-12', 2: 'Age 12-24', 3: 'Age 24+'}
status_map = {1: 'ZeroDose', 2: 'Defaulter', 3: 'OnSchedule'}

# 6. Aggregate by facility - COUNT UNIQUE CHILDREN for status
facilities = {}
for _, row in vax_df.iterrows():
    fid = int(row['PHC_ENTRY_ID'])
    person_id = row['PERSON_ID']

    if fid not in facilities:
        facilities[fid] = {
            'children': {},  # person_id -> {status, age}
            'vaccines': {},
        }

    # Track child with their status and age (use first occurrence)
    if person_id not in facilities[fid]['children']:
        status_type = row['CHILD_VACCINATION_STATUS']
        age_type = row['CHILDREN_AGE_TYPE']
        facilities[fid]['children'][person_id] = {
            'status': status_map.get(status_type, 'OnSchedule'),
            'age': age_map.get(age_type, 'Age 0-12')
        }

    # Count vaccines
    vax_id = int(row['VACCINE_DOSES_ID'])
    vax_name = vaccine_map.get(vax_id, 'Other')
    facilities[fid]['vaccines'][vax_name] = facilities[fid]['vaccines'].get(vax_name, 0) + 1

print(f"Facilities in data: {len(facilities)}")

# 7. Calculate GLOBAL summary from ALL data (not just matched facilities)
global_children = {}
for _, row in vax_df.iterrows():
    person_id = row['PERSON_ID']
    if person_id not in global_children:
        status_type = row['CHILD_VACCINATION_STATUS']
        age_type = row['CHILDREN_AGE_TYPE']
        global_children[person_id] = {
            'status': status_map.get(status_type, 'OnSchedule'),
            'age': age_map.get(age_type, 'Age 0-12')
        }

global_summary = {
    'TotalChildren': len(global_children),
    'OnSchedule': sum(1 for c in global_children.values() if c['status'] == 'OnSchedule'),
    'Defaulter': sum(1 for c in global_children.values() if c['status'] == 'Defaulter'),
    'ZeroDose': sum(1 for c in global_children.values() if c['status'] == 'ZeroDose'),
    'Age012': sum(1 for c in global_children.values() if c['age'] == 'Age 0-12'),
    'Age1224': sum(1 for c in global_children.values() if c['age'] == 'Age 12-24'),
    'Age24plus': sum(1 for c in global_children.values() if c['age'] == 'Age 24+'),
}

# Count vaccines from ALL records
global_vaccines = {}
for _, row in vax_df.iterrows():
    vax_id = int(row['VACCINE_DOSES_ID'])
    vax_name = vaccine_map.get(vax_id, 'Other')
    global_vaccines[vax_name] = global_vaccines.get(vax_name, 0) + 1

global_summary['vaccines'] = global_vaccines

# 8. Build GeoJSON
features = []
summary = global_summary.copy()

matched = 0

for fid, data in facilities.items():
    if fid not in phc_names:
        continue

    en_name = phc_names[fid]['en_name']
    ar_name = phc_names[fid]['ar_name']

    loc = None
    if fid in manual_map:
        map_name = manual_map[fid]
        if map_name in locations_en:
            loc = locations_en[map_name]
    if not loc and en_name and en_name in locations_en:
        loc = locations_en[en_name]
    if not loc and en_name and en_name.lower() in locations_en:
        loc = locations_en[en_name.lower()]
    if not loc and ar_name and ar_name in locations_ar:
        loc = locations_ar[ar_name]
    if not loc:
        for loc_ar, loc_data in locations_ar.items():
            if ar_name and len(ar_name) > 5 and (ar_name in loc_ar or loc_ar in ar_name):
                loc = loc_data
                break

    if not loc:
        continue

    matched += 1

    # Calculate counts from unique children
    total_children = len(data['children'])
    on_schedule = sum(1 for c in data['children'].values() if c['status'] == 'OnSchedule')
    defaulter = sum(1 for c in data['children'].values() if c['status'] == 'Defaulter')
    zero_dose = sum(1 for c in data['children'].values() if c['status'] == 'ZeroDose')
    age_012 = sum(1 for c in data['children'].values() if c['age'] == 'Age 0-12')
    age_1224 = sum(1 for c in data['children'].values() if c['age'] == 'Age 12-24')
    age_24plus = sum(1 for c in data['children'].values() if c['age'] == 'Age 24+')

    display_name = en_name if en_name else loc['name_en']
    display_ar = ar_name if ar_name else loc['name_ar']

    props = {
        'Health Facility': display_name,
        'Health Facility AR': display_ar,
        'Governorate': loc['gov'],
        'Organization': loc['org'],
        'TotalChildren': total_children,
        'TotalVaccinations': sum(data['vaccines'].values()),
        'Age 0-12': age_012,
        'Age 12-24': age_1224,
        'Age 24+': age_24plus,
        'OnSchedule': on_schedule,
        'Defaulter': defaulter,
        'ZeroDose': zero_dose,
    }

    for vax in ['BCG', 'HepB', 'IPV1', 'IPV2', 'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4', 'bOPV5',
                'Rota1', 'Rota2', 'Rota3', 'Penta1', 'Penta2', 'Penta3',
                'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP']:
        props[vax] = data['vaccines'].get(vax, 0)

    feature = {
        'type': 'Feature',
        'properties': props,
        'geometry': {'type': 'Point', 'coordinates': [loc['lon'], loc['lat']]}
    }
    features.append(feature)

print(f"\nMatched: {matched}")
print(f"\nSummary:")
print(f"  TotalChildren: {summary['TotalChildren']}")
print(f"  OnSchedule: {summary['OnSchedule']}")
print(f"  Defaulter: {summary['Defaulter']}")
print(f"  ZeroDose: {summary['ZeroDose']}")

# Save
geojson = {'type': 'FeatureCollection', 'features': features, 'summary': summary}
output = 'var json_vaccination_individual_data = ' + json.dumps(geojson, ensure_ascii=False) + ';'

with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_individual_data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nDone! {len(features)} features saved")
