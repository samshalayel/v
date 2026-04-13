import pandas as pd
import json
from datetime import datetime
import re

# Read all data files
df = pd.read_excel('data/sss.xlsx')
person = pd.read_excel('data/person.xlsx')
doses = pd.read_excel('data/vaccine_doses_tb.xlsx')
phc = pd.read_excel('data/phc_center_tb.xlsx')
geo = pd.read_excel('data/geolocation_tb.xlsx')
location_df = pd.read_csv('data/location_point_unified_corrected.csv')

# Create dose ID to name mapping
dose_map = dict(zip(doses['VACCINE_DOSES_ID'], doses['VACCINE_DOSES_NAME']))

# Create PHC to geolocation mapping
phc_geo = dict(zip(phc['PHC_CENTER_ID'], phc['GEOLOCATION_ID']))
phc_name_en = dict(zip(phc['PHC_CENTER_ID'], phc['NAME_EN']))
phc_name_ar = dict(zip(phc['PHC_CENTER_ID'], phc['NAME_AR']))

# Create geolocation to governorate mapping
gov_map = {
    3: 'North Gaza',
    5: 'Gaza',
    6: 'Middle zone',
    7: 'Khan Younis',
    8: 'Rafah'
}

# Normalize function for better matching
def normalize_name(name):
    if pd.isna(name) or not isinstance(name, str):
        return ''
    # Remove extra spaces, convert to lower
    name = re.sub(r'\s+', ' ', name.strip().lower())
    # Remove common prefixes/suffixes
    name = name.replace(' - ', ' ').replace('-', ' ')
    return name

# Create location lookup by facility name (both normalized)
location_lookup = {}
for _, row in location_df.iterrows():
    name_en = str(row['Medical Point - Health Facility Name in English']).strip() if pd.notna(row['Medical Point - Health Facility Name in English']) else ''
    name_ar = str(row['Medical Point - Health Facility Name in Arabic']).strip() if pd.notna(row['Medical Point - Health Facility Name in Arabic']) else ''

    if pd.notna(row['Long']) and pd.notna(row['Lat']):
        coords_data = (row['Long'], row['Lat'], row['Governorate'], row.get('Organization', 'MoH'))
        if name_en:
            location_lookup[normalize_name(name_en)] = coords_data
            location_lookup[name_en] = coords_data
        if name_ar:
            location_lookup[normalize_name(name_ar)] = coords_data
            location_lookup[name_ar] = coords_data

# Merge df with person to get DOB
merged = df.merge(person[['PERSON_ID', 'DOB']], on='PERSON_ID', how='left')

# Calculate age in days
today = datetime(2026, 2, 4)
merged['age_days'] = (today - merged['DOB']).dt.days

# Define age groups
def get_age_group(age_days):
    if pd.isna(age_days):
        return 'Unknown'
    if age_days <= 365:
        return '0-12'
    elif age_days <= 730:
        return '12-24'
    else:
        return '24+'

merged['age_group'] = merged['age_days'].apply(get_age_group)

# Map dose names
merged['VACCINE_NAME'] = merged['VACCINE_DOSES_ID'].map(dose_map)

# Standardize vaccine names for the output
vaccine_name_map = {
    'BCG': 'BCG',
    'Hepatitis B0': 'HepB',
    'IPV 1': 'IPV1',
    'IPV 2': 'IPV2',
    'bOPV 1': 'bOPV1',
    'bOPV 2': 'bOPV2',
    'bOPV 3': 'bOPV3',
    'bOPV 4': 'bOPV4',
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
    'DT': 'DT',
    'DT1': 'DT1'
}

# Manual mapping for known facilities
manual_mapping = {
    # PHC_CENTER_ID: (Long, Lat, Governorate, Organization)
    # North Gaza
    308: (34.255361, 31.337389, 'Rafah', 'MoH'),  # regional / الاقليمي -> AL EQLEMI
    313: (34.469722, 31.543056, 'North Gaza', 'MSF'),  # MSF Belgium
    314: (34.478056, 31.543333, 'North Gaza', 'NGO'),  # Al Fursan Medical Center
    315: (34.485000, 31.537500, 'North Gaza', 'NGO'),  # Civil Defense Medical Root Point
    316: (34.494167, 31.541111, 'North Gaza', 'MoH'),  # Haider Abdel Shafi Medical Center
    317: (34.500556, 31.544444, 'North Gaza', 'NGO'),  # Insan Medical Center
    318: (34.470556, 31.535556, 'North Gaza', 'NGO'),  # Al-Mustafa Medical Point
    319: (34.496111, 31.536944, 'North Gaza', 'NGO'),  # Anwar Aziz Medical Roots Point
    320: (34.483611, 31.551389, 'North Gaza', 'NGO'),  # roots of the medicinal herbs / Al-Atatreh
    321: (34.466389, 31.540556, 'North Gaza', 'PRCS'),  # Red Crescent Medical Point

    # Khan Younis
    90: (34.294914, 31.362098, 'Khan Younis', 'UNRWA'),  # Japanese HC
    206: (34.448430, 31.528658, 'Gaza', 'UNRWA'),  # Asmaa Preparatory School
    103: (34.389554, 31.448438, 'Middle zone', 'UNRWA'),  # Nusairat
    217: (34.343242, 31.422712, 'Middle zone', 'PRCS'),  # Red Crescent Dr. Fathi Arafat
    292: (34.270385, 31.361199, 'Khan Younis', 'UNRWA'),  # Al-Mawasi Clinic
    112: (34.338754, 31.424086, 'Middle zone', 'UNRWA'),  # Deir el balah
    240: (34.455794, 31.521171, 'Gaza', 'UNRWA'),  # Salah al-Din
    51: (34.400375, 31.439331, 'Middle zone', 'MoH'),  # مركز جورة اللوت -> Bureij
    237: (34.460410, 31.516160, 'Gaza', 'PRCS'),  # Al Sahaba Clinic
    229: (34.302078, 31.392643, 'Khan Younis', 'UNRWA'),  # Hanin
    139: (34.279500, 31.347417, 'Khan Younis', 'MSF'),  # MSF-ASP-ELATTAR
    223: (34.293417, 31.385778, 'Khan Younis', 'MSF'),  # Mawasi Khan Younis MSF Belgium
    306: (34.306698, 31.394863, 'Khan Younis', 'UNRWA'),  # Hamad UN Health Center
    130: (34.298306, 31.352056, 'Khan Younis', 'PRCS'),  # الهلال الأحمر-الأمل -> Al-Amal Hospital
    221: (34.256200, 31.352339, 'Khan Younis', 'UNRWA'),  # Zaarab Health Center
    41: (34.405607, 31.438834, 'Middle zone', 'MoH'),  # عيادة البريج الجديده -> Burij
    258: (34.476944, 31.531111, 'North Gaza', 'UNRWA'),  # مدرسة حليمة السعدية
    19: (34.453219, 31.539423, 'Gaza', 'MoH'),  # عيادة شهداء الشاطئ -> Al Shati
    277: (34.453056, 31.539167, 'Gaza', 'MDM'),  # عيادة MDM النادي -> MDM North Beach
    219: (34.242750, 31.342222, 'Rafah', 'ICRC'),  # Red Cross field hospital

    # Gaza
    20: (34.438056, 31.523056, 'Gaza', 'MoH'),  # Al Moustafa PHC
    28: (34.470047, 31.532889, 'Gaza', 'MoH'),  # Al Shaeikh Radwan
    25: (34.459201, 31.512722, 'Gaza', 'MoH'),  # Al-Daraj
    44: (34.451310, 31.506673, 'Gaza', 'MoH'),  # Masqat Al Sabra
    46: (34.459040, 31.499240, 'Gaza', 'PRCS'),  # Al-Zaytoun Clinic
    137: (34.443056, 31.496944, 'Gaza', 'MSF'),  # MSF Spain-Al-Zaytoun
    128: (34.441111, 31.523056, 'Gaza', 'MSF'),  # MSF Belgium - Al-Shifa
    212: (34.465570, 31.507300, 'Gaza', 'UNRWA'),  # Al Daraj MP

    # Rafah
    305: (34.248667, 31.346194, 'Rafah', 'UK-MED'),  # UK-MED

    # Additional mappings
    233: (34.450556, 31.513611, 'Gaza', 'NGO'),  # Kuwaiti Clinic -> Al-Kuwaiti Hospital
    129: (34.274041, 31.368285, 'Khan Younis', 'PRCS'),  # الهلال الأحمر - المواصي -> PRCS Mawasi
    134: (34.357917, 31.443733, 'Middle zone', 'IMC'),  # IMC -Zawida
    18: (34.484444, 31.527500, 'North Gaza', 'MoH'),  # مركز شهداء جباليا -> Jabalia Medical Clinic
    100: (34.438056, 31.523056, 'Gaza', 'UNRWA'),  # Gaza Town
    295: (34.453056, 31.539167, 'Gaza', 'MDM'),  # MDM-F Clinic
    141: (34.292088, 31.385153, 'Khan Younis', 'PRCS'),  # الهلال الأحمر-خانيونس-القرارة -> PRCS Mawasi Alqarara
    264: (34.307611, 31.394194, 'Khan Younis', 'NGO'),  # طوارئ NGO'S خانيونس -> Emergency NGO
    263: (34.306698, 31.394863, 'Khan Younis', 'UNRWA'),  # عيادة حمد -> Hamad HC
    215: (34.312583, 31.394500, 'Khan Younis', 'NGO'),  # Palm Al-Qarara Center -> PAL MED Shalet
    260: (34.268966, 31.352249, 'Khan Younis', 'NGO'),  # جمعية بيتنا -> Giving Without Borders
    252: (34.449970, 31.508970, 'Gaza', 'PRCS'),  # الهلال الأحمر - السرايا -> Al-Sabra PRCS
    307: (34.294914, 31.362098, 'Khan Younis', 'UNRWA'),  # Mobile team Japanese
    105: (34.389693, 31.460235, 'Middle zone', 'UNRWA'),  # west nusirat
    213: (34.346268, 31.432989, 'Middle zone', 'IMC'),  # IMC- Deir al-Balah
    135: (34.459040, 31.499240, 'Gaza', 'PRCS'),  # الهلال الأحمر-غزة-الزيتون
    231: (34.294998, 31.351730, 'Khan Younis', 'MoH'),  # Al-Majayda Clinic -> Almajada MP
    228: (34.260452, 31.343415, 'Khan Younis', 'UNRWA'),  # Bir 19
    256: (34.261119, 31.357610, 'Khan Younis', 'NGO'),  # نقطة طبية حلاوة -> El-Najar MP
    265: (34.291953, 31.348591, 'Khan Younis', 'UNRWA'),  # مدرسة الحوارني -> Kh/Younis Prep Boys

    # More facilities
    108: (34.367100, 31.438575, 'Middle zone', 'MoH'),  # Al-Sawarha
    207: (34.465570, 31.507300, 'Gaza', 'UNRWA'),  # Al Daraj
    236: (34.391550, 31.449410, 'Middle zone', 'PRCS'),  # Nuseirat Clinic PRCS

    # Final batch
    225: (34.320301, 31.408829, 'Middle zone', 'MDM'),  # Sea Center -> Al-Bahr PHC MdM F
    276: (34.453056, 31.539167, 'Gaza', 'MDM'),  # عيادة MDM روني
    259: (34.484444, 31.527500, 'North Gaza', 'UNRWA'),  # مدرسة تل الزعتر
    304: (34.241429, 31.338187, 'Rafah', 'UNRWA'),  # Muawiya Health Center UN
    234: (34.449970, 31.508970, 'Gaza', 'PRCS'),  # Al-Sabra Red Crescent
    230: (34.269278, 31.344611, 'Rafah', 'NGO'),  # Heroic Hearts Well 19
    138: (34.246861, 31.344222, 'Rafah', 'MSF'),  # MSF-ASP -> Mawasi MSF-Spain
    21: (34.428889, 31.509444, 'Gaza', 'MoH'),  # عيادة الفلاح -> Al-Falah Health Center
    322: (34.450000, 31.520000, 'Gaza', 'MoH'),  # Mobile Vehicle1
    328: (34.380000, 31.430000, 'Middle zone', 'MoH'),  # Mobile Vehicle2
    270: (34.250222, 31.341444, 'Rafah', 'MoH'),  # طوارئ رفح -> Emergency Rafah
    312: (34.480000, 31.540000, 'North Gaza', 'MoH'),  # Mobile Vehicle1
    222: (34.389693, 31.460235, 'Middle zone', 'UNRWA'),  # West Nuseirat
    246: (34.438056, 31.523056, 'Gaza', 'NGO'),  # Jasmine point -> Heroic Hearts Al-Yasmin
    216: (34.300000, 31.370000, 'Khan Younis', 'NGO'),  # Relief Association Abu Aref
    323: (34.260000, 31.340000, 'Rafah', 'MoH'),  # Mobile car1
    248: (34.417500, 31.500278, 'Gaza', 'MoH'),  # Sheikh Ajlin
    203: (34.375121, 31.443758, 'Middle zone', 'PRCS'),  # Al-Sawarha Red Crescent
    214: (34.391550, 31.449410, 'Middle zone', 'PRCS'),  # Red Crescent Nuseirat
    249: (34.395231, 31.453332, 'Middle zone', 'MoH'),  # Al-Mufti School -> El Mofte MP

    # Last few
    201: (34.400605, 31.442877, 'Middle zone', 'PRCS'),  # Al-Bureij Red Crescent -> Burij PRCS
    261: (34.300083, 31.393500, 'Khan Younis', 'MoH'),  # طب الأسرة-خانيونس -> Teb Alosra
    64: (34.270385, 31.361199, 'Khan Younis', 'MoH'),  # عيادة المواصي
    50: (34.333160, 31.380468, 'Khan Younis', 'MoH'),  # عيادة مسقط القرارة -> QARRARA MP
    255: (34.466389, 31.540556, 'North Gaza', 'PRCS'),  # الهلال الاحمر الامن العام
    269: (34.318611, 31.397444, 'Khan Younis', 'NGO'),  # نقطة شموخ -> Shumukh
    125: (34.484444, 31.527500, 'North Gaza', 'UNRWA'),  # Fakhoura -> Jabalia
    290: (34.346268, 31.432989, 'Middle zone', 'MoH'),  # Mobile Team Deir al-Balah
    302: (34.268966, 31.352249, 'Khan Younis', 'NGO'),  # Hope project
    132: (34.484444, 31.527500, 'North Gaza', 'PRCS'),  # الهلال الأحمر-جباليا
    272: (34.242750, 31.342222, 'Rafah', 'ICRC'),  # مستشفى الميداني - الصليب الاحمر
    12: (34.483611, 31.551389, 'North Gaza', 'MoH'),  # مركز شهداء العطاطرة والسيفا
    26: (34.451310, 31.506673, 'Gaza', 'MoH'),  # مركز صبحه الحرازين
    131: (34.459040, 31.499240, 'Gaza', 'PRCS'),  # الهلال الأحمر-غزة
}

# Try to find more matches using fuzzy matching
def find_best_match(name_en, name_ar):
    # Try exact matches first
    if name_en and isinstance(name_en, str):
        if name_en in location_lookup:
            return location_lookup[name_en]
        norm_en = normalize_name(name_en)
        if norm_en in location_lookup:
            return location_lookup[norm_en]

    if name_ar and isinstance(name_ar, str):
        if name_ar in location_lookup:
            return location_lookup[name_ar]
        norm_ar = normalize_name(name_ar)
        if norm_ar in location_lookup:
            return location_lookup[norm_ar]

    # Try partial matches
    if name_en and isinstance(name_en, str):
        norm_en = normalize_name(name_en)
        for key, val in location_lookup.items():
            if isinstance(key, str) and (norm_en in key or key in norm_en):
                return val

    if name_ar and isinstance(name_ar, str):
        norm_ar = normalize_name(name_ar)
        for key, val in location_lookup.items():
            if isinstance(key, str) and (norm_ar in key or key in norm_ar):
                return val

    return None

# Group by PHC_SERVICE_PROVIDER_ID
features = []
unmatched = []

for phc_id, group in merged.groupby('PHC_SERVICE_PROVIDER_ID'):
    if pd.isna(phc_id):
        continue
    phc_id = int(phc_id)

    # Get facility info
    facility_name_en = phc_name_en.get(phc_id, f'Facility {phc_id}')
    facility_name_ar = phc_name_ar.get(phc_id, '')
    geo_id = phc_geo.get(phc_id)
    governorate = gov_map.get(geo_id, 'Unknown') if pd.notna(geo_id) else 'Unknown'

    # Try to find coordinates
    coords = None
    org = 'MoH'

    # Check manual mapping first
    if phc_id in manual_mapping:
        manual = manual_mapping[phc_id]
        coords = (manual[0], manual[1])
        governorate = manual[2]
        org = manual[3]
    else:
        # Try automated matching
        match = find_best_match(facility_name_en, facility_name_ar)
        if match:
            coords = (match[0], match[1])
            if match[2]:
                governorate = match[2]
            if len(match) > 3 and match[3]:
                org = match[3]

    if coords is None:
        unmatched.append({
            'phc_id': phc_id,
            'name_en': facility_name_en,
            'name_ar': facility_name_ar,
            'count': len(group['PERSON_ID'].unique())
        })
        continue

    # Count unique children
    children = group.groupby('PERSON_ID').agg({
        'age_group': 'first',
        'CHILD_VACCINATION_STATUS': 'max'
    }).reset_index()

    total_children = len(children)
    on_schedule = len(children[children['CHILD_VACCINATION_STATUS'] == 1])
    defaulter = len(children[children['CHILD_VACCINATION_STATUS'] == 2])
    zero_dose = len(children[children['CHILD_VACCINATION_STATUS'] == 3])

    # Age groups
    age_012 = len(children[children['age_group'] == '0-12'])
    age_1224 = len(children[children['age_group'] == '12-24'])
    age_24plus = len(children[children['age_group'] == '24+'])

    # Count vaccines
    vaccine_counts = {}
    for vax_name in group['VACCINE_NAME'].dropna():
        std_name = vaccine_name_map.get(vax_name, vax_name.replace(' ', ''))
        vaccine_counts[std_name] = vaccine_counts.get(std_name, 0) + 1

    # Build properties
    props = {
        'Health Facility': facility_name_en if isinstance(facility_name_en, str) else f'Facility {phc_id}',
        'Health Facility AR': facility_name_ar if isinstance(facility_name_ar, str) else '',
        'Governorate': governorate,
        'Organization': org,
        'TotalChildren': total_children,
        'TotalVaccinations': len(group),
        'Age 0-12': age_012,
        'Age 12-24': age_1224,
        'Age 24+': age_24plus,
        'OnSchedule': on_schedule,
        'Defaulter': defaulter,
        'ZeroDose': zero_dose
    }

    # Add vaccine counts
    for vax in ['BCG', 'HepB', 'IPV1', 'IPV2', 'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4',
                'Rota1', 'Rota2', 'Rota3', 'Penta1', 'Penta2', 'Penta3',
                'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP', 'DT']:
        props[vax] = vaccine_counts.get(vax, 0)

    feature = {
        'type': 'Feature',
        'properties': props,
        'geometry': {
            'type': 'Point',
            'coordinates': [float(coords[0]), float(coords[1])]
        }
    }
    features.append(feature)

# Calculate CORRECT totals (unique children across all facilities)
all_children = merged.groupby('PERSON_ID').agg({
    'age_group': 'first',
    'CHILD_VACCINATION_STATUS': 'max'
}).reset_index()

correct_totals = {
    'TotalChildren': len(all_children),
    'OnSchedule': len(all_children[all_children['CHILD_VACCINATION_STATUS'] == 1]),
    'Defaulter': len(all_children[all_children['CHILD_VACCINATION_STATUS'] == 2]),
    'ZeroDose': len(all_children[all_children['CHILD_VACCINATION_STATUS'] == 3]),
    'Age012': len(all_children[all_children['age_group'] == '0-12']),
    'Age1224': len(all_children[all_children['age_group'] == '12-24']),
    'Age24plus': len(all_children[all_children['age_group'] == '24+'])
}

# Calculate correct vaccine totals
all_vaccine_counts = {}
for vax_name in merged['VACCINE_NAME'].dropna():
    std_name = vaccine_name_map.get(vax_name, vax_name.replace(' ', ''))
    all_vaccine_counts[std_name] = all_vaccine_counts.get(std_name, 0) + 1

# Create GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': features,
    'summary': {
        'TotalChildren': correct_totals['TotalChildren'],
        'OnSchedule': correct_totals['OnSchedule'],
        'Defaulter': correct_totals['Defaulter'],
        'ZeroDose': correct_totals['ZeroDose'],
        'Age012': correct_totals['Age012'],
        'Age1224': correct_totals['Age1224'],
        'Age24plus': correct_totals['Age24plus'],
        'vaccines': all_vaccine_counts
    }
}

# Write to JS file
with open('data/vaccination_individual_data.js', 'w', encoding='utf-8') as f:
    f.write('var json_vaccination_individual_data = ')
    json.dump(geojson, f, indent=2, ensure_ascii=False)
    f.write(';')

print(f'Created {len(features)} facility features')
print(f'Unmatched facilities: {len(unmatched)}')

if unmatched:
    print('\nUnmatched facilities (top 20 by count):')
    unmatched_sorted = sorted(unmatched, key=lambda x: x['count'], reverse=True)[:20]
    for u in unmatched_sorted:
        print(f"  {u['phc_id']}: {u['name_en']} | {u['name_ar']} ({u['count']} children)")

# Summary statistics (CORRECT - unique children)
print(f'\nSummary (CORRECT totals):')
print(f'Total Children: {correct_totals["TotalChildren"]}')
print(f'On Schedule: {correct_totals["OnSchedule"]}')
print(f'Defaulter: {correct_totals["Defaulter"]}')
print(f'Zero Dose: {correct_totals["ZeroDose"]}')
