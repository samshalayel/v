import xml.etree.ElementTree as ET
import json

# Parse XML
tree = ET.parse('sheet_data.xml')
root = tree.getroot()

# Define namespace
ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

# Get all rows
rows = root.findall('.//x:row', ns)

# Parse header row
headers = []
header_row = rows[0]
for cell in header_row.findall('.//x:c', ns):
    value = cell.find('.//x:v', ns)
    if value is not None:
        headers.append(value.text)

# Find column indices
health_facility_idx = headers.index('Health Facility')
x_idx = headers.index('x')
y_idx = headers.index('y')

# Extract coordinates for each facility
facility_coords = {}

# Parse data rows
for row in rows[1:]:  # Skip header
    cells = row.findall('.//x:c', ns)
    cell_values = {}

    # Extract cell values
    for cell in cells:
        ref = cell.get('r')
        col_letter = ''.join(filter(str.isalpha, ref))
        col_idx = 0
        for i, c in enumerate(col_letter):
            col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
        col_idx -= 1

        if col_idx < len(headers):
            value_elem = cell.find('.//x:v', ns)
            if value_elem is not None:
                cell_values[col_idx] = value_elem.text

    # Get facility name and coordinates
    if health_facility_idx in cell_values:
        facility = cell_values[health_facility_idx]
        x = float(cell_values.get(x_idx, 0))
        y = float(cell_values.get(y_idx, 0))

        # Only store if we have valid coordinates
        if x != 0 and y != 0:
            if facility not in facility_coords:
                facility_coords[facility] = {'x': x, 'y': y, 'count': 1}
            else:
                # Average coordinates if multiple entries
                facility_coords[facility]['count'] += 1

print(f"Facilities with coordinates: {len(facility_coords)}")
print("\nSample coordinates:")
for i, (fac, coords) in enumerate(list(facility_coords.items())[:5]):
    print(f"{i+1}. {fac}: x={coords['x']}, y={coords['y']}")

# Save to JSON
with open('facility_coordinates.json', 'w', encoding='utf-8') as f:
    json.dump(facility_coords, f, indent=2, ensure_ascii=False)

print("\n\nCoordinates saved to facility_coordinates.json")
