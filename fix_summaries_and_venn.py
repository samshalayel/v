"""
1. Fix JS summary blocks to use unique-PERSON_ID counts (last-record per person).
2. Regenerate venn_intersection_data.js from the 3 raw Excel files.
"""
import pandas as pd
import json
import re
import warnings
warnings.filterwarnings('ignore')

BASE = 'C:/Users/Administrator/gaza_vaccination'

# ── helpers ──────────────────────────────────────────────────────────────────

def last_record_per_person(df):
    """Return one row per PERSON_ID: the last dose record (latest date, highest id)."""
    return (df
        .sort_values(['VACCINATION_DATE', 'PERSON_VACCINE_ID'], ascending=[False, False])
        .drop_duplicates(subset='PERSON_ID')
        .reset_index(drop=True))

STATUS_MAP = {1: 'ZeroDose', 2: 'Defaulter', 3: 'OnSchedule'}
AGE_MAP    = {1: '0-12',      2: '12-24',      3: '24+'}

def compute_summary(df):
    last = last_record_per_person(df)
    total       = last['PERSON_ID'].nunique()
    on_schedule = (last['CHILD_VACCINATION_STATUS'] == 3).sum()
    defaulter   = (last['CHILD_VACCINATION_STATUS'] == 2).sum()
    zero_dose   = (last['CHILD_VACCINATION_STATUS'] == 1).sum()
    return int(total), int(on_schedule), int(defaulter), int(zero_dose)

def patch_js_summary(js_path, total, on_schedule, defaulter, zero_dose):
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # parse the JS object
    js_obj = json.loads(content.split(' = ', 1)[1].rstrip(';'))
    var_name = content.split(' = ', 1)[0].strip()
    js_obj['summary']['TotalChildren'] = total
    js_obj['summary']['OnSchedule']    = on_schedule
    js_obj['summary']['Defaulter']     = defaulter
    js_obj['summary']['ZeroDose']      = zero_dose
    new_content = var_name + ' = ' + json.dumps(js_obj, ensure_ascii=False, separators=(',', ':')) + ';'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  Patched {js_path.split("/")[-1]}: total={total} OnSchedule={on_schedule} Defaulter={defaulter} ZeroDose={zero_dose}')


# ── load raw Excel files ──────────────────────────────────────────────────────

print('Loading Excel files ...')
r1 = pd.read_excel(BASE + '/data/r1111.xlsx')
r2 = pd.read_excel(BASE + '/data/r2222.xlsx')
r3 = pd.read_excel(BASE + '/data/r3333.xlsx')
print(f'  R1: {len(r1)} rows  |  R2: {len(r2)} rows  |  R3: {len(r3)} rows')

# ── fix summaries ─────────────────────────────────────────────────────────────

print('\nFixing JS summaries ...')
t1, s1, d1, z1 = compute_summary(r1)
patch_js_summary(BASE + '/data/vaccination_r1_data.js',            t1, s1, d1, z1)

t2, s2, d2, z2 = compute_summary(r2)
patch_js_summary(BASE + '/data/vaccination_individual_data.js',    t2, s2, d2, z2)

t3, s3, d3, z3 = compute_summary(r3)
patch_js_summary(BASE + '/data/vaccination_r3_data.js',            t3, s3, d3, z3)

# ── Venn intersection data ─────────────────────────────────────────────────────

print('\nBuilding Venn intersection data ...')

VACCINE_MAP = {
    1:'BCG', 2:'HepB', 3:'IPV1', 4:'IPV2', 5:'bOPV1', 6:'bOPV2', 7:'bOPV3',
    8:'bOPV4', 9:'Rota1', 10:'Rota2', 11:'Rota3', 12:'Penta1', 13:'Penta2',
    14:'Penta3', 15:'PCV1', 16:'PCV2', 17:'PCV3', 18:'MMR1', 19:'MMR2',
    20:'DTP', 21:'DT', 22:'DT', 23:'DT', 27:'bOPV5', 28:'Td'
}

def defaulters(df):
    """Return sub-df with last record per PERSON_ID where status==2."""
    last = last_record_per_person(df)
    return last[last['CHILD_VACCINATION_STATUS'] == 2]

def vaccines_for_person(df, pid):
    rows = df[df['PERSON_ID'] == pid]
    vnames = []
    for vid in rows['VACCINE_DOSES_ID'].dropna().unique():
        v = VACCINE_MAP.get(int(vid))
        if v:
            vnames.append(v)
    return sorted(set(vnames))

def age_label(df, pid):
    row = df[df['PERSON_ID'] == pid].head(1)
    if len(row) == 0:
        return ''
    at = row.iloc[0].get('CHILDREN_AGE_TYPE', None)
    if pd.isna(at):
        return ''
    return AGE_MAP.get(int(at), '')

def facility_name(df, pid, phc_map):
    row = df[df['PERSON_ID'] == pid].sort_values('VACCINATION_DATE', ascending=False).head(1)
    if len(row) == 0:
        return ''
    phc_id = row.iloc[0].get('PHC_ENTRY_ID', None)
    if pd.isna(phc_id):
        return ''
    return phc_map.get(int(phc_id), str(int(phc_id)))

def last_date(df, pid):
    row = df[df['PERSON_ID'] == pid].sort_values('VACCINATION_DATE', ascending=False).head(1)
    if len(row) == 0:
        return ''
    d = row.iloc[0]['VACCINATION_DATE']
    try:
        return str(d.date())
    except:
        return str(d)[:10]

# Load PHC name maps from the generated JS files
def load_phc_map(js_path):
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    js_obj = json.loads(content.split(' = ', 1)[1].rstrip(';'))
    phc_map = {}
    for feat in js_obj.get('features', []):
        p = feat['properties']
        phc_id_str = str(p.get('PHC_CENTER_ID', ''))
        name = p.get('Health Facility', '')
        if phc_id_str and name:
            phc_map[phc_id_str] = name
    return phc_map

# Build name maps from PHC_ENTRY_ID -> name using r1/r2/r3 themselves + phc_center_updated
phc_updated = pd.read_excel(BASE + '/data/phc_center_updated.xlsx')
phc_id_to_en = {}
for _, row in phc_updated.iterrows():
    pid = int(row['PHC_CENTER_ID'])
    en = (str(row['en_name']).strip() if not pd.isna(row.get('en_name', float('nan'))) else '') or \
         (str(row['NAME_EN']).strip() if not pd.isna(row.get('NAME_EN', float('nan'))) else '')
    phc_id_to_en[pid] = en or f'PHC-{pid}'

d1 = defaulters(r1);  ids1 = set(d1['PERSON_ID'])
d2 = defaulters(r2);  ids2 = set(d2['PERSON_ID'])
d3 = defaulters(r3);  ids3 = set(d3['PERSON_ID'])

print(f'  Defaulters — R1: {len(ids1)}  R2: {len(ids2)}  R3: {len(ids3)}')

def build_records(pids, df_list, round_labels):
    """pids = set of PERSON_IDs; df_list/round_labels parallel lists."""
    records = []
    for pid in sorted(pids):
        rec = {'id': int(pid)}
        # age from first round that has them
        for rdf in df_list:
            al = age_label(rdf, pid)
            if al:
                rec['age'] = al
                break
        if 'age' not in rec:
            rec['age'] = ''

        for rdf, label in zip(df_list, round_labels):
            if pid in set(rdf['PERSON_ID']):
                rec['fac_' + label]  = facility_name(rdf, pid, phc_id_to_en)
                rec['vax_' + label]  = vaccines_for_person(rdf, pid)
                rec['date_' + label] = last_date(rdf, pid)

        records.append(rec)
    return records

# R1 ∩ R2 only
ids_r1r2_only  = ids1 & ids2 - ids3
# R1 ∩ R3 only
ids_r1r3_only  = ids1 & ids3 - ids2
# R2 ∩ R3 only
ids_r2r3_only  = ids2 & ids3 - ids1
# R1 ∩ R2 ∩ R3
ids_r1r2r3     = ids1 & ids2 & ids3

print(f'  R1∩R2 (excl R3): {len(ids_r1r2_only)}')
print(f'  R1∩R3 (excl R2): {len(ids_r1r3_only)}')
print(f'  R2∩R3 (excl R1): {len(ids_r2r3_only)}')
print(f'  R1∩R2∩R3:        {len(ids_r1r2r3)}')

records_r1r2  = build_records(ids_r1r2_only,  [r1, r2],     ['r1', 'r2'])
records_r1r3  = build_records(ids_r1r3_only,  [r1, r3],     ['r1', 'r3'])
records_r2r3  = build_records(ids_r2r3_only,  [r2, r3],     ['r2', 'r3'])
records_r1r2r3= build_records(ids_r1r2r3,     [r1, r2, r3], ['r1', 'r2', 'r3'])

venn_data = {
    'r1r2':   records_r1r2,
    'r1r3':   records_r1r3,
    'r2r3':   records_r2r3,
    'r1r2r3': records_r1r2r3,
}

out_path = BASE + '/data/venn_intersection_data.js'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('var venn_intersection_data = ')
    f.write(json.dumps(venn_data, ensure_ascii=False, separators=(',', ':')))
    f.write(';')

print(f'\nWritten {out_path}')
print('Done.')
