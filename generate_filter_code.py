import json

# Read the data file to get min/max values and unique options
with open('data/location_point_unified_corrected_1.js', 'r', encoding='utf-8') as f:
    content = f.read()
    # Extract JSON from JavaScript variable
    json_str = content.replace('var json_location_point_unified_corrected_1 = ', '').rstrip(';')
    data = json.loads(json_str)

# Analyze data
features = data['features']

# Define filters
filters = {
    "Vaccination status of a Child | On Schedule": {"type": "int"},
    "Vaccination status of a Child | Defaulter": {"type": "int"},
    "Vaccination status of a Child | Zero Dose": {"type": "int"},
    "Total Children Vaccinated by Age | above 24": {"type": "int"},
    "Total Children Vaccinated by Age | 0 to 12": {"type": "int"},
    "Total Children Vaccinated by Age | 12 to 24": {"type": "int"},
    "Governorate": {"type": "str"},
    "Health Facility": {"type": "str"},
    "Suppervisor Name": {"type": "str"},
    "all_child": {"type": "int"}
}

# Calculate min/max for int fields and unique values for str fields
for filter_name, filter_info in filters.items():
    values = []
    for feature in features:
        if filter_name in feature['properties']:
            val = feature['properties'][filter_name]
            if val not in [None, '', 'None']:
                values.append(val)

    if filter_info['type'] == 'int':
        if values:
            numeric_values = [int(float(v)) if v else 0 for v in values]
            filter_info['min'] = min(numeric_values)
            filter_info['max'] = max(numeric_values)
        else:
            filter_info['min'] = 0
            filter_info['max'] = 100
    elif filter_info['type'] == 'str':
        filter_info['unique_values'] = sorted(list(set([str(v) for v in values if v])))

# Save filter info
with open('filter_info.json', 'w', encoding='utf-8') as f:
    json.dump(filters, f, ensure_ascii=False, indent=2)

print("Filter analysis complete!")
print("\n" + "=" * 80)
for filter_name, filter_info in filters.items():
    print(f"\n{filter_name}:")
    print(f"  Type: {filter_info['type']}")
    if filter_info['type'] == 'int':
        print(f"  Min: {filter_info['min']}")
        print(f"  Max: {filter_info['max']}")
    else:
        print(f"  Unique values ({len(filter_info['unique_values'])}):")
        for val in filter_info['unique_values'][:10]:  # Show first 10
            print(f"    - {val}")
        if len(filter_info['unique_values']) > 10:
            print(f"    ... and {len(filter_info['unique_values']) - 10} more")
