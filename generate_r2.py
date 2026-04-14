import pandas as pd
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

BASE = 'C:/Users/Administrator/gaza_vaccination'

# Load all reference data
phc_updated = pd.read_excel(BASE + '/data/phc_center_updated.xlsx')
phc_tb = pd.read_excel(BASE + '/data/phc_center_tb.xlsx')
geo = pd.read_excel(BASE + '/data/geolocation_tb.xlsx')
r2_df = pd.read_excel(BASE + '/data/r2222.xlsx')
loc_csv = pd.read_csv(BASE + '/data/location_point_unified_corrected.csv')

print(f'R2 records loaded: {len(r2_df)}')
print(f'Date range: {r2_df["VACCINATION_DATE"].min()} -> {r2_df["VACCINATION_DATE"].max()}')

# Governorate resolution chain
govs = geo[geo['TYPE_ID'] == 364].set_index('GEOLOCATION_ID')['NAME_EN'].to_dict()
geo_parent = geo.set_index('GEOLOCATION_ID')['PARENT_ID'].to_dict()
geo_to_gov_cache = {}

def find_gov(geo_id):
    if geo_id in geo_to_gov_cache:
        return geo_to_gov_cache[geo_id]
    if geo_id in govs:
        geo_to_gov_cache[geo_id] = govs[geo_id]
        return govs[geo_id]
    parent = geo_parent.get(geo_id)
    if parent is None or parent == 0:
        geo_to_gov_cache[geo_id] = None
        return None
    result = find_gov(int(parent))
    geo_to_gov_cache[geo_id] = result
    return result

# PHC_CENTER_ID -> GEOLOCATION_ID
phc_id_to_geo = {}
for _, row in phc_tb.iterrows():
    pid = int(row['PHC_CENTER_ID'])
    geo_id = row['GEOLOCATION_ID']
    if not pd.isna(geo_id):
        phc_id_to_geo[pid] = int(geo_id)

# Coordinate and org lookup from location CSV
csv_by_name = {}
for _, row in loc_csv.iterrows():
    name = str(row['Medical Point - Health Facility Name in English']).strip()
    gov_val = str(row['Governorate']).strip() if not pd.isna(row['Governorate']) else ''
    org_val = str(row['Organization']).strip() if not pd.isna(row['Organization']) else ''
    if not pd.isna(row['Long']) and not pd.isna(row['Lat']):
        csv_by_name[name] = {'coords': [float(row['Long']), float(row['Lat'])],
                             'gov': gov_val, 'org': org_val}

# Coordinate lookup from existing JS files
with open(BASE + '/data/vaccination_r3_data.js', 'r', encoding='utf-8') as f:
    prev_r3 = json.loads(f.read().replace('var json_vaccination_r3_data = ', '').rstrip(';'))
with open(BASE + '/data/vaccination_individual_data.js', 'r', encoding='utf-8') as f:
    ind_js = json.loads(f.read().replace('var json_vaccination_individual_data = ', '').rstrip(';'))

existing_by_name = {}
for feat in prev_r3['features'] + ind_js['features']:
    p = feat['properties']
    name = p.get('Health Facility', '').strip()
    coords = feat['geometry']['coordinates']
    if name not in existing_by_name:
        existing_by_name[name] = {
            'org': p.get('Organization', ''),
            'gov': p.get('Governorate', ''),
            'coords': coords
        }

GOV_NORM = {
    'Middle': 'Middle zone',
    'Khan younis': 'Khan Younis',
    'Gaza': 'Gaza',
    'North Gaza': 'North Gaza',
    'Rafah': 'Rafah',
}

# Build facility info dict keyed by PHC_CENTER_ID
phc_info = {}
for _, row in phc_updated.iterrows():
    pid = int(row['PHC_CENTER_ID'])
    en = (str(row['en_name']).strip() if not pd.isna(row['en_name']) else '') or \
         (str(row['NAME_EN']).strip() if not pd.isna(row['NAME_EN']) else '')
    ar = (str(row['NAME_AR']).strip() if not pd.isna(row['NAME_AR']) else '') or \
         (str(row['ar_name']).strip() if not pd.isna(row['ar_name']) else '')

    geo_id = phc_id_to_geo.get(pid)
    gov_raw = find_gov(geo_id) if geo_id else None
    gov = GOV_NORM.get(gov_raw, gov_raw) if gov_raw else None

    coords = [0.0, 0.0]
    org = 'MoH'

    if en in existing_by_name:
        existing = existing_by_name[en]
        if existing['coords'] not in ([0.0, 0.0], [0, 0]):
            coords = existing['coords']
        org = existing.get('org', 'MoH') or 'MoH'

    if coords == [0.0, 0.0] and en in csv_by_name:
        coords = csv_by_name[en]['coords']
        if not org or org == 'MoH':
            org = csv_by_name[en].get('org', 'MoH') or 'MoH'

    if not gov:
        if en in existing_by_name and existing_by_name[en].get('gov'):
            gov = existing_by_name[en]['gov']
        elif en in csv_by_name and csv_by_name[en].get('gov'):
            gov = csv_by_name[en]['gov']

    phc_info[pid] = {'en': en, 'ar': ar, 'gov': gov or 'Unknown', 'org': org, 'coords': coords}

# Vaccine dose ID -> vaccine name mapping
VACCINE_MAP = {
    1: 'BCG',    2: 'HepB',   3: 'IPV1',   4: 'IPV2',   5: 'bOPV1',
    6: 'bOPV2',  7: 'bOPV3',  8: 'bOPV4',  9: 'Rota1',  10: 'Rota2',
    11: 'Rota3', 12: 'Penta1',13: 'Penta2', 14: 'Penta3',15: 'PCV1',
    16: 'PCV2',  17: 'PCV3',  18: 'MMR1',  19: 'MMR2',  20: 'DTP',
    21: 'DT',    22: 'DT',    23: 'DT',    27: 'bOPV5',  28: 'Td'
}
VACCINE_NAMES = ['BCG', 'HepB', 'IPV1', 'IPV2', 'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4', 'bOPV5',
                 'Rota1', 'Rota2', 'Rota3', 'Penta1', 'Penta2', 'Penta3',
                 'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP']
AGE_MAP = {1: '0-12', 2: '12-24', 3: '24+'}
STATUS_MAP = {1: 'ZeroDose', 2: 'Defaulter', 3: 'OnSchedule', 4: 'NotClassified'}

# Aggregate per facility
fac_children = defaultdict(set)
fac_children_age = defaultdict(dict)
fac_children_status = defaultdict(dict)
fac_vaccines = defaultdict(lambda: defaultdict(int))
fac_vaccinations = defaultdict(int)
fac_person_vaccines = defaultdict(lambda: defaultdict(set))

for _, row in r2_df.iterrows():
    phc_id = row['PHC_ENTRY_ID']
    if pd.isna(phc_id):
        continue
    phc_id = int(phc_id)
    person_id = row['PERSON_ID']
    if pd.isna(person_id):
        continue
    age_type = row['CHILDREN_AGE_TYPE']
    status = row['CHILD_VACCINATION_STATUS']
    vaccine_id = row['VACCINE_DOSES_ID']

    fac_children[phc_id].add(person_id)
    fac_vaccinations[phc_id] += 1
    if not pd.isna(age_type):
        fac_children_age[phc_id][person_id] = int(age_type)
    if not pd.isna(status):
        fac_children_status[phc_id][person_id] = int(status)
    if not pd.isna(vaccine_id):
        vname = VACCINE_MAP.get(int(vaccine_id))
        if vname:
            fac_vaccines[phc_id][vname] += 1
            fac_person_vaccines[phc_id][person_id].add(vname)

# Build GeoJSON features and summary
features = []
summary = {
    'TotalChildren': 0, 'OnSchedule': 0, 'Defaulter': 0, 'ZeroDose': 0,
    'NotClassified': 0,
    'Age012': 0, 'Age1224': 0, 'Age24plus': 0,
    'vaccines': {v: 0 for v in VACCINE_NAMES}
}

MANUAL = {
    43:  {'en': 'Al-Sawarha (Al-Khawaldeh) Center', 'ar': 'عيادة الخوالدة',
          'gov': 'Middle zone', 'org': 'Medecins du Monde', 'coords': [34.3670997, 31.4385752]},
    51:  {'en': 'Jawrat Al-Lut Health Center', 'ar': 'مركز جورة اللوت الصحي',
          'gov': 'Khan Younis', 'org': 'MoH', 'coords': [0.0, 0.0]},
    100: {'en': 'Gaza Town PHC - UNRWA', 'ar': 'عيادة مدينة غزة UN',
          'gov': 'Gaza', 'org': 'UNRWA', 'coords': [34.44350555, 31.51551951]},
    264: {'en': "NGO Emergency - Khan Younis", 'ar': "طوارئ NGO'S خانيونس",
          'gov': 'Khan Younis', 'org': '', 'coords': [0.0, 0.0]},
    265: {'en': 'Al-Hawrani School - Khan Younis', 'ar': 'مدرسة الحوارني - خانيونس',
          'gov': 'Khan Younis', 'org': '', 'coords': [0.0, 0.0]},
    270: {'en': 'Emergency - Rafah', 'ar': 'طوارئ رفح',
          'gov': 'Rafah', 'org': '', 'coords': [0.0, 0.0]},
}

for phc_id in sorted(fac_children.keys()):
    info = phc_info.get(phc_id)

    if phc_id in MANUAL and (info is None or not info['en'] or info['coords'] == [0.0, 0.0]):
        m = MANUAL[phc_id]
        if info is None:
            info = m
        else:
            if not info['en']: info['en'] = m['en']
            if not info['ar']: info['ar'] = m['ar']
            if info['coords'] == [0.0, 0.0]: info['coords'] = m['coords']
            if not info['gov'] or info['gov'] == 'Unknown': info['gov'] = m['gov']
            if not info['org']: info['org'] = m['org']

    if info is None:
        tb_row = phc_tb[phc_tb['PHC_CENTER_ID'] == phc_id]
        if len(tb_row) > 0:
            tb = tb_row.iloc[0]
            en_fallback = str(tb['NAME_EN']).strip() if not pd.isna(tb['NAME_EN']) else ''
            ar_fallback = str(tb['NAME_AR']).strip() if not pd.isna(tb['NAME_AR']) else ''
            geo_id = phc_id_to_geo.get(phc_id)
            gov_raw = find_gov(geo_id) if geo_id else None
            gov_fallback = GOV_NORM.get(gov_raw, gov_raw) if gov_raw else 'Unknown'
            info = {'en': en_fallback or 'PHC-' + str(phc_id),
                    'ar': ar_fallback, 'gov': gov_fallback,
                    'org': 'MoH', 'coords': [0.0, 0.0]}
        else:
            info = {'en': 'PHC-' + str(phc_id), 'ar': '', 'gov': 'Unknown',
                    'org': '', 'coords': [0.0, 0.0]}

    total_children = len(fac_children[phc_id])
    total_vaccinations = fac_vaccinations[phc_id]

    age_counts = defaultdict(int)
    for p, a in fac_children_age[phc_id].items():
        age_counts[AGE_MAP.get(a, '24+')] += 1

    status_counts = defaultdict(int)
    for p, s in fac_children_status[phc_id].items():
        sname = STATUS_MAP.get(s, 'NotClassified')
        status_counts[sname] += 1

    classified = status_counts.get('OnSchedule', 0) + status_counts.get('Defaulter', 0) + status_counts.get('ZeroDose', 0)
    not_classified = total_children - classified

    vaccine_counts = {v: fac_vaccines[phc_id].get(v, 0) for v in VACCINE_NAMES}

    # Per-status vaccine breakdown
    vax_by_status = {}
    person_status = fac_children_status[phc_id]
    person_vaxes = fac_person_vaccines[phc_id]
    for vname in VACCINE_NAMES:
        d = s = z = nc = 0
        for p, vaxes in person_vaxes.items():
            if vname in vaxes:
                st = person_status.get(p)
                if st is None:
                    nc += 1
                else:
                    sname = STATUS_MAP.get(st)
                    if sname == 'Defaulter':    d += 1
                    elif sname == 'OnSchedule': s += 1
                    elif sname == 'ZeroDose':   z += 1
                    else:                       nc += 1
        vax_by_status[vname + '_D']  = d
        vax_by_status[vname + '_S']  = s
        vax_by_status[vname + '_Z']  = z
        vax_by_status[vname + '_NC'] = nc

    props = {
        'Health Facility': info['en'],
        'Health Facility AR': info['ar'],
        'Governorate': info['gov'],
        'Organization': info['org'],
        'TotalChildren': total_children,
        'TotalVaccinations': total_vaccinations,
        'Age 0-12': age_counts.get('0-12', 0),
        'Age 12-24': age_counts.get('12-24', 0),
        'Age 24+': age_counts.get('24+', 0),
        'OnSchedule': status_counts.get('OnSchedule', 0),
        'Defaulter': status_counts.get('Defaulter', 0),
        'ZeroDose': status_counts.get('ZeroDose', 0),
        'NotClassified': not_classified,
        'Round': 'Round 2'
    }
    props.update(vaccine_counts)
    props.update(vax_by_status)

    features.append({
        'type': 'Feature',
        'properties': props,
        'geometry': {'type': 'Point', 'coordinates': info['coords']}
    })

    summary['TotalChildren'] += total_children
    summary['OnSchedule'] += status_counts.get('OnSchedule', 0)
    summary['Defaulter'] += status_counts.get('Defaulter', 0)
    summary['ZeroDose'] += status_counts.get('ZeroDose', 0)
    summary['NotClassified'] += not_classified
    summary['Age012'] += age_counts.get('0-12', 0)
    summary['Age1224'] += age_counts.get('12-24', 0)
    summary['Age24plus'] += age_counts.get('24+', 0)
    for v in VACCINE_NAMES:
        summary['vaccines'][v] += vaccine_counts[v]

output = {'type': 'FeatureCollection', 'features': features, 'summary': summary}
js_content = ('var json_vaccination_individual_data = ' +
              json.dumps(output, ensure_ascii=False, separators=(',', ':')) + ';')

with open(BASE + '/data/vaccination_individual_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f'\nWritten {len(features)} features')
print(f'TotalChildren: {summary["TotalChildren"]}')
print(f'OnSchedule: {summary["OnSchedule"]} | Defaulter: {summary["Defaulter"]} | ZeroDose: {summary["ZeroDose"]}')
print(f'Ages: 0-12: {summary["Age012"]} | 12-24: {summary["Age1224"]} | 24+: {summary["Age24plus"]}')
print(f'MMR1: {summary["vaccines"]["MMR1"]} | BCG: {summary["vaccines"]["BCG"]} | Penta1: {summary["vaccines"]["Penta1"]}')
print('\nFacilities:')
for feat in features[:20]:
    p = feat['properties']
    print('  {:40s} | {:15s} | {:3d} children | {}'.format(
        p['Health Facility'][:40], p['Governorate'][:15],
        p['TotalChildren'], feat['geometry']['coordinates']
    ))
if len(features) > 20:
    print(f'  ... and {len(features)-20} more')
