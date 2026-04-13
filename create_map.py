import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Read location data with real coordinates
locations = pd.read_csv('data/location_point_unified_corrected.csv')

# Read vaccination data for statistics
vaccinations = pd.read_excel('data/person_vaccine_tb.xlsx')

# Read PHC center names
phc = pd.read_excel('data/phc_center_updated.xlsx')

# Read person data for DOB
person = pd.read_excel('data/person.xlsx')

# Calculate statistics
num_centers = len(locations)
num_children = vaccinations['PERSON_ID'].nunique()
num_vaccinations = len(vaccinations)

# Calculate BCG by age
bcg = vaccinations[vaccinations['VACCINE_DOSES_ID'] == 1]
bcg_with_dob = bcg.merge(person[['PERSON_ID', 'DOB']], on='PERSON_ID', how='left')
bcg_with_dob['VACCINATION_DATE'] = pd.to_datetime(bcg_with_dob['VACCINATION_DATE'])
bcg_with_dob['DOB'] = pd.to_datetime(bcg_with_dob['DOB'])
bcg_with_dob['age_days'] = (bcg_with_dob['VACCINATION_DATE'] - bcg_with_dob['DOB']).dt.days
bcg_under_1_month = len(bcg_with_dob[bcg_with_dob['age_days'] <= 30])
bcg_over_1_month = len(bcg_with_dob[bcg_with_dob['age_days'] > 30])
bcg_total = len(bcg_with_dob)

# Calculate Top 10 and Low 10 centers
center_counts = vaccinations.groupby('PHC_SERVICE_PROVIDER_ID').size().reset_index(name='vaccination_count')
center_counts = center_counts.merge(
    phc[['PHC_CENTER_ID', 'en_name', 'NAME_AR']],
    left_on='PHC_SERVICE_PROVIDER_ID',
    right_on='PHC_CENTER_ID',
    how='left'
)
center_counts['en_name'] = center_counts['en_name'].fillna(center_counts['NAME_AR'])
center_counts['en_name'] = center_counts['en_name'].fillna('ID: ' + center_counts['PHC_SERVICE_PROVIDER_ID'].astype(str))
center_counts = center_counts.sort_values('vaccination_count', ascending=False)

top_10 = center_counts.head(10)
low_10 = center_counts.tail(10)

# Create map centered on Gaza
m = folium.Map(location=[31.4, 34.38], zoom_start=11, tiles='OpenStreetMap')

# Colors for organizations
org_colors = {
    'UNRWA': 'blue',
    'MOH': 'green',
    'MoH': 'green',
    'PRCS': 'red',
    'PCRS': 'red',
    'MSF Belgium': 'purple',
    'MSF Spain': 'orange',
    'MSF SPAIN': 'orange',
    'MSF': 'purple',
    'MDM': 'darkblue',
    'IMC': 'darkgreen',
    'UK MED': 'lightblue',
    'UK-MED': 'lightblue',
    'ICRC': 'pink',
    'Juzoor': 'lightgreen',
    'JUZOOR': 'lightgreen',
}

# Add markers
for idx, row in locations.iterrows():
    lat = row['Lat']
    lon = row['Long']
    name_en = row['Medical Point - Health Facility Name in English']
    name_ar = row['Medical Point - Health Facility Name in Arabic']
    org = row['Organization']
    gov = row['Governorate']

    color = org_colors.get(org, 'gray')

    popup_html = '<div style="direction: rtl; text-align: right;">'
    popup_html += '<b>' + str(name_en) + '</b><br>'
    popup_html += '<b>' + str(name_ar) + '</b><br><hr>'
    popup_html += 'Organization: ' + str(org) + '<br>'
    popup_html += 'Governorate: ' + str(gov) + '<br>'
    popup_html += 'Coordinates: ' + str(lat) + ', ' + str(lon)
    popup_html += '</div>'

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(color=color, icon='plus-sign'),
        tooltip=name_en
    ).add_to(m)

# Add title header
title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 15px 40px; border-radius: 15px; color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center;">
    <div style="font-size: 24px; font-weight: bold;">Catch-Up Vaccination Daily Summary Sheet</div>
    <div style="font-size: 14px; color: #aaa; margin-top: 5px;">Round 2 | 18 Jan - 29 Jan 2026</div>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add statistics cards at top
stats_html = '''
<div style="position: fixed; top: 90px; left: 50px; z-index: 1000; display: flex; gap: 15px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px 30px; border-radius: 15px; color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; min-width: 150px;">
        <div style="font-size: 36px; font-weight: bold;">''' + str(num_centers) + '''</div>
        <div style="font-size: 14px; margin-top: 5px;">Health Centers</div>
        <div style="font-size: 12px; color: #ddd;">المراكز الصحية</div>
    </div>
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 20px 30px; border-radius: 15px; color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; min-width: 150px;">
        <div style="font-size: 36px; font-weight: bold;">''' + f"{num_children:,}" + '''</div>
        <div style="font-size: 14px; margin-top: 5px;">Children</div>
        <div style="font-size: 12px; color: #ddd;">الأطفال</div>
    </div>
    <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
                padding: 20px 30px; border-radius: 15px; color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center; min-width: 150px;">
        <div style="font-size: 36px; font-weight: bold;">''' + f"{num_vaccinations:,}" + '''</div>
        <div style="font-size: 14px; margin-top: 5px;">Vaccinations</div>
        <div style="font-size: 12px; color: #ddd;">التطعيمات</div>
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(stats_html))

# Build Top 10 list HTML
top_10_items = ''
for i, (idx, row) in enumerate(top_10.iterrows(), 1):
    name = str(row['en_name'])[:30] + ('...' if len(str(row['en_name'])) > 30 else '')
    count = f"{int(row['vaccination_count']):,}"
    top_10_items += f'<div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;"><span>{i}. {name}</span><span style="font-weight: bold; color: #11998e;">{count}</span></div>'

# Build Low 10 list HTML
low_10_items = ''
for i, (idx, row) in enumerate(low_10.iterrows(), 1):
    name = str(row['en_name'])[:30] + ('...' if len(str(row['en_name'])) > 30 else '')
    count = f"{int(row['vaccination_count']):,}"
    low_10_items += f'<div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;"><span>{i}. {name}</span><span style="font-weight: bold; color: #eb3349;">{count}</span></div>'

# Add Top 10 and Low 10 cards side by side on the right
top10_html = '''
<div style="position: fixed; top: 100px; right: 350px; z-index: 1000;
            background-color: white; padding: 15px; border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 300px; max-height: 380px; overflow-y: auto;">
    <h4 style="margin: 0 0 15px 0; color: #11998e; border-bottom: 2px solid #11998e; padding-bottom: 10px;">
        🏆 Top 10 Centers
    </h4>
    ''' + top_10_items + '''
</div>
'''
m.get_root().html.add_child(folium.Element(top10_html))

# Add Low 10 card on the right (next to Top 10)
low10_html = '''
<div style="position: fixed; top: 100px; right: 10px; z-index: 1000;
            background-color: white; padding: 15px; border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 300px; max-height: 380px; overflow-y: auto;">
    <h4 style="margin: 0 0 15px 0; color: #eb3349; border-bottom: 2px solid #eb3349; padding-bottom: 10px;">
        📉 Low 10 Centers
    </h4>
    ''' + low_10_items + '''
</div>
'''
m.get_root().html.add_child(folium.Element(low10_html))

# Add BCG card
bcg_html = '''
<div style="position: fixed; bottom: 50px; right: 10px; z-index: 1000;
            background-color: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 280px;">
    <h4 style="margin: 0 0 15px 0; color: #4a90d9; border-bottom: 2px solid #4a90d9; padding-bottom: 10px;">
        💉 BCG Vaccination by Age
    </h4>
    <div style="display: flex; justify-content: space-around; text-align: center;">
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 15px; border-radius: 10px; color: white; min-width: 100px;">
            <div style="font-size: 28px; font-weight: bold;">''' + f"{bcg_under_1_month:,}" + '''</div>
            <div style="font-size: 11px; margin-top: 5px;">Under 1 Month</div>
            <div style="font-size: 10px; color: #ddd;">أقل من شهر</div>
        </div>
        <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
                    padding: 15px; border-radius: 10px; color: white; min-width: 100px;">
            <div style="font-size: 28px; font-weight: bold;">''' + f"{bcg_over_1_month:,}" + '''</div>
            <div style="font-size: 11px; margin-top: 5px;">Over 1 Month</div>
            <div style="font-size: 10px; color: #ddd;">أكبر من شهر</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee;">
        <span style="font-size: 14px; color: #666;">Total BCG: </span>
        <span style="font-size: 18px; font-weight: bold; color: #4a90d9;">''' + f"{bcg_total:,}" + '''</span>
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(bcg_html))

# Add legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
            background-color: white; padding: 15px; border: 2px solid grey;
            border-radius: 5px; font-size: 12px;">
<h4 style="margin: 0 0 10px 0;">Organizations</h4>
<p><span style="color:blue;">&#9679;</span> UNRWA</p>
<p><span style="color:green;">&#9679;</span> MOH</p>
<p><span style="color:red;">&#9679;</span> PRCS</p>
<p><span style="color:purple;">&#9679;</span> MSF Belgium</p>
<p><span style="color:orange;">&#9679;</span> MSF Spain</p>
<p><span style="color:darkblue;">&#9679;</span> MDM</p>
<p><span style="color:lightblue;">&#9679;</span> UK MED</p>
<p><span style="color:gray;">&#9679;</span> Other</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save map
m.save('health_facilities_map.html')
print('Map saved to: health_facilities_map.html')
print('Total facilities mapped:', num_centers)
print('Total children:', num_children)
print('Total vaccinations:', num_vaccinations)
