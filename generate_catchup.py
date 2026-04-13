import pandas as pd
import re
import json

df = pd.read_excel('C:/Users/Administrator/Desktop/unicef/Health Facilities_Catch Up_IIIRound_31Mar26.xlsx')

def dms_to_dd(dms_str):
    s = str(dms_str).strip()
    pattern = r'(\d+)[^\d\s]\s*(\d+)[^\d\s]\s*([\d.]+)[^\d\s]?\s*([NSEWnsew])?'
    m = re.search(pattern, s)
    if m:
        deg, mn, sec, direction = m.groups()
        dd = float(deg) + float(mn)/60 + float(sec)/3600
        if direction and direction.upper() in ['S', 'W']:
            dd = -dd
        return dd, direction.upper() if direction else None
    return None, None

def parse_coord(val):
    if pd.isna(val):
        return None, None
    s = str(val).strip().rstrip(',')
    try:
        return float(s), None
    except:
        pass
    dd, direction = dms_to_dd(s)
    if dd is not None:
        return dd, direction
    return None, None

GAZA_LAT = (31.2, 31.7)
GAZA_LON = (34.1, 34.6)

def is_lat(v): return GAZA_LAT[0] <= v <= GAZA_LAT[1]
def is_lon(v): return GAZA_LON[0] <= v <= GAZA_LON[1]

def fix_truncated(v):
    s = str(int(v))
    if len(s) >= 8 and s.startswith('31'):
        candidate = float(s[:2] + '.' + s[2:])
        if is_lat(candidate):
            return candidate
    return None

features = []
for i, row in df.iterrows():
    raw_long = row['Long']
    raw_lat = row['Lat']
    v_long, dir_long = parse_coord(raw_long)
    v_lat, dir_lat = parse_coord(raw_lat)

    if v_long is not None and v_long > 1000:
        v_long = fix_truncated(v_long)
    if v_lat is not None and v_lat > 1000:
        v_lat = fix_truncated(v_lat)
    if v_long is not None and v_long < 0:
        v_long = abs(v_long)
    if v_lat is not None and v_lat < 0:
        v_lat = abs(v_lat)

    final_lat = None
    final_lon = None

    if v_long is not None and v_lat is not None:
        if dir_long == 'N' and dir_lat == 'E':
            final_lat, final_lon = v_long, v_lat
        elif dir_long == 'E' and dir_lat == 'N':
            final_lat, final_lon = v_lat, v_long
        elif dir_long is None and dir_lat is None:
            if is_lon(v_long) and is_lat(v_lat):
                final_lat, final_lon = v_lat, v_long
            elif is_lat(v_long) and is_lon(v_lat):
                final_lat, final_lon = v_long, v_lat
        elif dir_long == 'N' and dir_lat is None:
            final_lat, final_lon = v_long, v_lat
        elif dir_long == 'E' and dir_lat is None:
            final_lat, final_lon = v_lat, v_long

    if final_lat is not None and final_lon is not None:
        if is_lat(final_lat) and is_lon(final_lon):
            name_en = str(row['Medical Point - Health Facility Name in English']) if pd.notna(row['Medical Point - Health Facility Name in English']) else ''
            name_ar = str(row['Medical Point - Health Facility Name in Arabic']) if pd.notna(row['Medical Point - Health Facility Name in Arabic']) else ''
            gov = str(row['Governorate']) if pd.notna(row['Governorate']) else ''
            addr = str(row['Site Address']) if pd.notna(row['Site Address']) else ''
            org = str(row['Organization']) if pd.notna(row['Organization']) else ''
            teams = str(row['Teams Organization']) if pd.notna(row['Teams Organization']) else ''
            features.append({
                'type': 'Feature',
                'properties': {
                    'name_en': name_en,
                    'name_ar': name_ar,
                    'Governorate': gov,
                    'address': addr,
                    'Organization': org,
                    'teams_org': teams,
                },
                'geometry': {'type': 'Point', 'coordinates': [round(final_lon, 7), round(final_lat, 7)]}
            })
        else:
            print(f'Row {i+2} out of range: lat={final_lat}, lon={final_lon}')
    else:
        print(f'Row {i+2} failed: Long={raw_long}, Lat={raw_lat}')

geojson = {'type': 'FeatureCollection', 'features': features}
js_content = 'var json_catchup_facilities = ' + json.dumps(geojson, ensure_ascii=False) + ';'

with open('C:/Users/Administrator/gaza_vaccination/data/catchup_facilities.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f'Written {len(features)} features to catchup_facilities.js')
