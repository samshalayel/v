import json
import csv

# Coordinate mappings from location file
coord_map = {
    "AL EQLEMI": [34.255361, 31.337389],
    "ALNAHR ALBARED": [34.2885, 31.343694],
    "Al Shati PHC": [34.4532194, 31.5394234],
    "Free thoughts": [34.34816435, 31.41741518],
    "Juzoor of Civil defense": [34.485, 31.5375],
    "Kh/Younis Prep. Boys \"A\"": [34.29195263, 31.34859067],
    "MSF Spain's Al Attar PHCC": [34.2795, 31.347417],
    "PRCS Mawasi Alqarara": [34.292088, 31.385153],
    "Shefaa Alkwaity": [34.275113, 31.366636],
    "Shumukh": [34.318611, 31.397444],
    "Tayara Clinic": [34.354585, 31.417508],
    "Teb Alosra": [34.300083, 31.3935],
}

# Read vaccination data
with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove var declaration and parse JSON
json_str = content.replace('var json_vaccination_data = ', '').strip()
if json_str.endswith(';'):
    json_str = json_str[:-1]

# Split into features (since it's on one line, we need to be careful)
# Let's use simple string replacement instead

changes = []

for facility, coords in coord_map.items():
    # Escape special characters for the search
    search_facility = facility.replace('"', '\\"')

    # Build the search pattern - looking for the facility with [0, 0]
    # The data format is: "Health Facility": "NAME", ... "coordinates": [0, 0]

    # First check if this facility exists with [0, 0]
    if f'"Health Facility": "{facility}"' in content or f'"Health Facility": "{search_facility}"' in content:
        # We need to find the feature containing this facility and replace its coordinates
        pass

# Since the file is complex, let's do a simpler approach
# Read and rebuild the entire JSON

# Extract JSON
prefix = 'var json_vaccination_data = '
if content.startswith(prefix):
    json_str = content[len(prefix):]
    if json_str.endswith(';'):
        json_str = json_str[:-1]
else:
    json_str = content

try:
    data = json.loads(json_str)
except:
    # Try to fix common issues
    print("Error parsing JSON, trying alternate method...")
    import re
    # The file might have newlines, let's read it differently
    with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_data.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple string replacements for each facility
    for facility, coords in coord_map.items():
        # Find facility section and replace [0, 0] with correct coordinates
        # Look for pattern: "Health Facility": "FACILITY_NAME"...coordinates": [0, 0]
        pattern = f'"Health Facility": "{facility}"'
        if pattern in content:
            # Find the position and replace the coordinates that follow
            idx = content.find(pattern)
            # Find the next [0, 0] after this facility
            coord_pattern = '"coordinates": [0, 0]'
            next_feature_start = content.find('{"type": "Feature"', idx + 1)
            if next_feature_start == -1:
                next_feature_start = len(content)

            coord_idx = content.find(coord_pattern, idx)
            if coord_idx != -1 and coord_idx < next_feature_start:
                new_coords = f'"coordinates": [{coords[0]}, {coords[1]}]'
                content = content[:coord_idx] + new_coords + content[coord_idx + len(coord_pattern):]
                changes.append(facility)
                print(f"+ Fixed: {facility} -> [{coords[0]}, {coords[1]}]")

    # Write back
    with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_data.js', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nTotal fixed: {len(changes)} facilities")

    # Check remaining
    remaining = content.count('"coordinates": [0, 0]')
    print(f"Remaining with [0, 0]: {remaining}")
    exit()

# If JSON parsing worked
for feature in data['features']:
    facility = feature['properties']['Health Facility']
    coords = feature['geometry']['coordinates']

    if coords == [0, 0]:
        # Check if we have coordinates for this facility
        if facility in coord_map:
            feature['geometry']['coordinates'] = coord_map[facility]
            changes.append(facility)
            print(f"+ Fixed: {facility} -> {coord_map[facility]}")
        else:
            # Try case-insensitive match
            for key, val in coord_map.items():
                if key.lower() == facility.lower():
                    feature['geometry']['coordinates'] = val
                    changes.append(facility)
                    print(f"+ Fixed: {facility} -> {val}")
                    break
            else:
                print(f"- Not found: {facility}")

# Write back
output = f'var json_vaccination_data = {json.dumps(data, ensure_ascii=False)}'
with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nTotal fixed: {len(changes)} facilities")

# Verify
remaining = sum(1 for f in data['features'] if f['geometry']['coordinates'] == [0, 0])
print(f"Remaining with [0, 0]: {remaining}")
