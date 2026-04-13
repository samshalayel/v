import pandas as pd
import json

# Read data
df = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/310120250933.xlsx')
with open('C:/Users/Administrator/gaza_vaccination/facility_coordinates.json', 'r', encoding='utf-8') as f:
    coords = json.load(f)

# Aggregate
sum_cols = ['all_child', 'Total Children Vaccinated by Age | 0 to 12',
            'Total Children Vaccinated by Age | 12 to 24', 'Total Children Vaccinated by Age | above 24',
            'Vaccination status of a Child | Zero Dose', 'Vaccination status of a Child | Defaulter',
            'Vaccination status of a Child | On Schedule',
            'Hep', 'BCG', 'IPV1', 'IPV2', 'Penta1', 'Penta2', 'Penta3',
            'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4', 'bOPV5',
            'Rota1', 'Rota2', 'Rota3', 'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP', 'DT', 'Td']

agg_dict = {col: 'sum' for col in sum_cols if col in df.columns}
agg_dict['Governorate'] = 'first'
grouped = df.groupby(['Health Facility']).agg(agg_dict).reset_index()

vaccine_cols = ['Hep', 'BCG', 'IPV1', 'IPV2', 'Penta1', 'Penta2', 'Penta3',
                'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4', 'bOPV5',
                'Rota1', 'Rota2', 'Rota3', 'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP', 'DT', 'Td']

grouped['total_vax'] = sum(grouped[col] for col in vaccine_cols if col in grouped.columns)

# Stats
total_facilities = len(grouped)
total_children = int(grouped['all_child'].sum())
total_vaccinations = int(grouped['total_vax'].sum())
total_bcg = int(grouped['BCG'].sum())

# Top/Low 10
top10 = grouped.nlargest(10, 'total_vax')[['Health Facility', 'total_vax']].values.tolist()
low10 = grouped.nsmallest(10, 'total_vax')[['Health Facility', 'total_vax']].values.tolist()

# Generate Top 10 HTML
top10_html = ""
for i, (name, vax) in enumerate(top10, 1):
    short = name[:28] + "..." if len(name) > 28 else name
    top10_html += f'<div class="rank-item"><span class="rank-num">{i}</span><span class="rank-name">{short}</span><span class="rank-value top">{int(vax):,}</span></div>\n'

# Generate Low 10 HTML
low10_html = ""
for i, (name, vax) in enumerate(low10, 1):
    short = name[:28] + "..." if len(name) > 28 else name
    low10_html += f'<div class="rank-item"><span class="rank-num">{i}</span><span class="rank-name">{short}</span><span class="rank-value low">{int(vax):,}</span></div>\n'

# Generate markers
markers_js = ""
for _, row in grouped.iterrows():
    name = row['Health Facility']
    gov = row['Governorate']
    children = int(row['all_child'])
    vax = int(row['total_vax'])

    if name in coords:
        lon, lat = coords[name]
    else:
        continue

    # Color by organization
    if 'UNRWA' in name:
        color = '#3498db'
    elif 'PRCS' in name or 'Red Crescent' in name:
        color = '#e74c3c'
    elif 'MSF' in name and 'Belgium' in name:
        color = '#9b59b6'
    elif 'MSF' in name and 'Spain' in name:
        color = '#f39c12'
    elif 'MDM' in name or 'MdM' in name:
        color = '#2c3e50'
    elif 'UK' in name:
        color = '#1abc9c'
    else:
        color = '#27ae60'

    popup = f"<b>{name}</b><br>Governorate: {gov}<br>Children: {children:,}<br>Vaccinations: {vax:,}"
    popup = popup.replace("'", "\\'")
    radius = min(18, max(6, children // 40))
    markers_js += f"    L.circleMarker([{lat}, {lon}], {{radius: {radius}, fillColor: '{color}', color: '#fff', weight: 2, fillOpacity: 0.8}}).addTo(map).bindPopup('{popup}');\n"

html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catch-Up Vaccination Summary - Gaza</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
        #map {{ position: absolute; top: 0; bottom: 0; left: 0; right: 0; z-index: 1; }}

        .header {{
            position: fixed; top: 12px; left: 50%; transform: translateX(-50%); z-index: 1000;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 10px 25px; border-radius: 10px; color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); text-align: center;
        }}
        .header h1 {{ font-size: 18px; font-weight: 600; }}
        .header p {{ font-size: 11px; color: #aaa; margin-top: 3px; }}

        .stats-row {{
            position: fixed; top: 75px; left: 12px; z-index: 1000;
            display: flex; flex-direction: column; gap: 8px;
        }}
        .stat-card {{
            padding: 12px 16px; border-radius: 10px; color: white;
            box-shadow: 0 3px 12px rgba(0,0,0,0.2); text-align: center; min-width: 110px;
        }}
        .stat-card.purple {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .stat-card.green {{ background: linear-gradient(135deg, #11998e, #38ef7d); }}
        .stat-card.red {{ background: linear-gradient(135deg, #eb3349, #f45c43); }}
        .stat-card .num {{ font-size: 24px; font-weight: 700; }}
        .stat-card .label {{ font-size: 10px; margin-top: 2px; opacity: 0.95; }}
        .stat-card .label-ar {{ font-size: 9px; opacity: 0.7; }}

        .panel {{
            position: fixed; z-index: 1000;
            background: white; padding: 10px; border-radius: 8px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.12); font-size: 11px;
            width: 220px;
        }}
        .panel h4 {{
            margin: 0 0 8px 0; padding-bottom: 6px;
            border-bottom: 2px solid; font-size: 12px; font-weight: 600;
        }}
        .panel h4.top {{ color: #11998e; border-color: #11998e; }}
        .panel h4.low {{ color: #eb3349; border-color: #eb3349; }}

        .rank-list {{ max-height: 240px; overflow-y: auto; }}
        .rank-item {{
            display: flex; align-items: center; padding: 5px 0;
            border-bottom: 1px solid #f5f5f5;
        }}
        .rank-num {{
            width: 18px; height: 18px; border-radius: 50%;
            background: #f0f0f0; text-align: center; line-height: 18px;
            font-size: 9px; font-weight: 600; margin-right: 6px; flex-shrink: 0;
        }}
        .rank-name {{ flex: 1; font-size: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .rank-value {{ font-weight: 600; font-size: 11px; margin-left: 5px; }}
        .rank-value.top {{ color: #11998e; }}
        .rank-value.low {{ color: #eb3349; }}

        .top-panel {{ top: 75px; right: 12px; }}
        .low-panel {{ top: 380px; right: 12px; }}

        .legend {{
            position: fixed; bottom: 20px; left: 12px; z-index: 1000;
            background: white; padding: 10px; border-radius: 8px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.12);
        }}
        .legend h4 {{ margin: 0 0 6px 0; font-size: 11px; font-weight: 600; }}
        .legend-item {{ display: flex; align-items: center; margin: 3px 0; font-size: 10px; }}
        .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}

        .bcg-panel {{
            position: fixed; bottom: 20px; right: 12px; z-index: 1000;
            background: white; padding: 12px; border-radius: 8px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.12); width: 140px; text-align: center;
        }}
        .bcg-panel h4 {{ margin: 0 0 6px 0; font-size: 11px; color: #4a90d9; font-weight: 600; }}
        .bcg-total {{ font-size: 22px; font-weight: 700; color: #4a90d9; }}
    </style>
</head>
<body>
    <div id="map"></div>

    <div class="header">
        <h1><i class="fas fa-syringe"></i> Catch-Up Vaccination Daily Summary</h1>
        <p>Round 2 | 18 Jan - 29 Jan 2026</p>
    </div>

    <div class="stats-row">
        <div class="stat-card purple">
            <div class="num">{total_facilities}</div>
            <div class="label">Health Centers</div>
            <div class="label-ar">المراكز الصحية</div>
        </div>
        <div class="stat-card green">
            <div class="num">{total_children:,}</div>
            <div class="label">Children</div>
            <div class="label-ar">الأطفال</div>
        </div>
        <div class="stat-card red">
            <div class="num">{total_vaccinations:,}</div>
            <div class="label">Vaccinations</div>
            <div class="label-ar">التطعيمات</div>
        </div>
    </div>

    <div class="panel top-panel">
        <h4 class="top">🏆 Top 10 Centers</h4>
        <div class="rank-list">
            {top10_html}
        </div>
    </div>

    <div class="panel low-panel">
        <h4 class="low">📉 Low 10 Centers</h4>
        <div class="rank-list">
            {low10_html}
        </div>
    </div>

    <div class="legend">
        <h4>Organizations</h4>
        <div class="legend-item"><div class="legend-dot" style="background: #3498db;"></div> UNRWA</div>
        <div class="legend-item"><div class="legend-dot" style="background: #27ae60;"></div> MOH</div>
        <div class="legend-item"><div class="legend-dot" style="background: #e74c3c;"></div> PRCS</div>
        <div class="legend-item"><div class="legend-dot" style="background: #9b59b6;"></div> MSF Belgium</div>
        <div class="legend-item"><div class="legend-dot" style="background: #f39c12;"></div> MSF Spain</div>
        <div class="legend-item"><div class="legend-dot" style="background: #2c3e50;"></div> MDM</div>
        <div class="legend-item"><div class="legend-dot" style="background: #1abc9c;"></div> UK MED</div>
    </div>

    <div class="bcg-panel">
        <h4><i class="fas fa-syringe"></i> Total BCG</h4>
        <div class="bcg-total">{total_bcg:,}</div>
    </div>

    <script>
        var map = L.map('map').setView([31.4, 34.35], 10);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap'
        }}).addTo(map);

{markers_js}
    </script>
</body>
</html>
'''

with open('C:/Users/Administrator/gaza_vaccination/health_facilities_map.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ health_facilities_map.html regenerated!")
print(f"   - {total_facilities} facilities")
print(f"   - {total_children:,} children")
print(f"   - {total_vaccinations:,} vaccinations")
print(f"   - {total_bcg:,} BCG")
