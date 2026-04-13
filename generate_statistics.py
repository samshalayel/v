import json

# Load the new vaccination data
with open(r"C:\Users\Administrator\AppData\Local\Temp\qgis2web\qgis2web_2026_01_22-12_48_37_247602\data\vaccination_data.js", 'r', encoding='utf-8') as f:
    content = f.read()
    json_start = content.find('{')
    json_str = content[json_start:-1]  # Remove trailing semicolon
    vaccination_data = json.loads(json_str)

# Load the old location data
try:
    with open(r"C:\Users\Administrator\AppData\Local\Temp\qgis2web\qgis2web_2026_01_22-12_48_37_247602\data\location_point_unified_corrected_1.js", 'r', encoding='utf-8') as f:
        content = f.read()
        json_start = content.find('{')
        json_str = content[json_start:]
        # Try to find the closing } and ;
        last_brace = json_str.rfind('}')
        if last_brace > 0:
            json_str = json_str[:last_brace+1]
        location_data = json.loads(json_str)
except Exception as e:
    print(f"Warning: Could not load baseline data: {e}")
    location_data = {'features': []}

print("=" * 80)
print("VACCINATION DATA STATISTICS")
print("=" * 80)

# Calculate statistics from new data
total_children = 0
total_on_schedule = 0
total_defaulter = 0
total_zero_dose = 0
total_age_0_12 = 0
total_age_12_24 = 0
total_age_above_24 = 0
total_reports = 0

governorate_stats = {}
vaccine_totals = {}

for feature in vaccination_data['features']:
    props = feature['properties']

    total_children += props['Total Children']
    total_on_schedule += props['On Schedule']
    total_defaulter += props['Defaulter']
    total_zero_dose += props['Zero Dose']
    total_age_0_12 += props['Age 0-12 Months']
    total_age_12_24 += props['Age 12-24 Months']
    total_age_above_24 += props['Age Above 24 Months']
    total_reports += props['Total Reports']

    # Governorate statistics
    gov = props['Governorate']
    if gov not in governorate_stats:
        governorate_stats[gov] = {
            'facilities': 0,
            'children': 0
        }
    governorate_stats[gov]['facilities'] += 1
    governorate_stats[gov]['children'] += props['Total Children']

    # Vaccine totals
    for vaccine, count in props['Vaccine Details'].items():
        if vaccine not in vaccine_totals:
            vaccine_totals[vaccine] = 0
        vaccine_totals[vaccine] += count

print("\n** OVERALL STATISTICS **")
print(f"Total Facilities: {len(vaccination_data['features'])}")
print(f"Total Children Vaccinated: {total_children:,}")
print(f"Total Reports Aggregated: {total_reports}")
print(f"\nAge Distribution:")
print(f"  0-12 Months: {total_age_0_12:,} ({100*total_age_0_12/max(total_children,1):.1f}%)")
print(f"  12-24 Months: {total_age_12_24:,} ({100*total_age_12_24/max(total_children,1):.1f}%)")
print(f"  Above 24 Months: {total_age_above_24:,} ({100*total_age_above_24/max(total_children,1):.1f}%)")
print(f"\nVaccination Status:")
print(f"  On Schedule: {total_on_schedule:,} ({100*total_on_schedule/max(total_children,1):.1f}%)")
print(f"  Defaulter: {total_defaulter:,} ({100*total_defaulter/max(total_children,1):.1f}%)")
print(f"  Zero Dose: {total_zero_dose:,} ({100*total_zero_dose/max(total_children,1):.1f}%)")

print("\n** STATISTICS BY GOVERNORATE **")
for gov, stats in sorted(governorate_stats.items()):
    print(f"\n{gov}:")
    print(f"  Facilities: {stats['facilities']}")
    print(f"  Children: {stats['children']:,}")
    print(f"  Avg per Facility: {stats['children']/stats['facilities']:.1f}")

print("\n** TOP 10 VACCINES ADMINISTERED **")
sorted_vaccines = sorted(vaccine_totals.items(), key=lambda x: x[1], reverse=True)
for i, (vaccine, count) in enumerate(sorted_vaccines[:10], 1):
    print(f"{i:2d}. {vaccine:10s}: {count:,}")

print("\n" + "=" * 80)
print("COMPARISON WITH BASELINE DATA")
print("=" * 80)

# Compare with old data
print(f"\nBaseline Data (location_point):")
print(f"  Total Facilities: {len(location_data['features'])}")

baseline_children = 0
baseline_on_schedule = 0
baseline_age_0_12 = 0
baseline_age_above_24 = 0

for feature in location_data['features']:
    props = feature['properties']
    baseline_children += props.get('Aggregated_all_child', 0)
    baseline_on_schedule += props.get('Aggregated_Vaccination status of a Child | On Schedule', 0)
    baseline_age_0_12 += props.get('Aggregated_Total Children Vaccinated by Age | 0 to 12', 0)
    baseline_age_above_24 += props.get('Aggregated_Total Children Vaccinated by Age | above 24', 0)

print(f"  Total Children: {baseline_children:,}")
print(f"  On Schedule: {baseline_on_schedule:,}")
print(f"  Age 0-12: {baseline_age_0_12:,}")
print(f"  Age Above 24: {baseline_age_above_24:,}")

print(f"\nNew Data (vaccination_data):")
print(f"  Total Facilities: {len(vaccination_data['features'])}")
print(f"  Total Children: {total_children:,}")
print(f"  On Schedule: {total_on_schedule:,}")
print(f"  Age 0-12: {total_age_0_12:,}")
print(f"  Age Above 24: {total_age_above_24:,}")

print(f"\nGrowth/Change:")
print(f"  Facilities: {len(vaccination_data['features']) - len(location_data['features']):+d}")
print(f"  Total Children: {total_children - baseline_children:+,}")
print(f"  On Schedule: {total_on_schedule - baseline_on_schedule:+,}")

print("\n" + "=" * 80)
print("TOP 10 FACILITIES BY CHILDREN VACCINATED")
print("=" * 80)

facilities_sorted = sorted(
    vaccination_data['features'],
    key=lambda x: x['properties']['Total Children'],
    reverse=True
)

for i, feature in enumerate(facilities_sorted[:10], 1):
    props = feature['properties']
    print(f"\n{i}. {props['Medical Point - Health Facility Name']}")
    print(f"   Location: {props['Governorate']}")
    print(f"   Total Children: {props['Total Children']:,}")
    print(f"   On Schedule: {props['On Schedule']} ({100*props['On Schedule']/max(props['Total Children'],1):.1f}%)")
    print(f"   Reports: {props['Total Reports']}")

print("\n" + "=" * 80)
