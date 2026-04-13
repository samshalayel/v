import xml.etree.ElementTree as ET
import json
from collections import defaultdict

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

print(f"Total columns: {len(headers)}")
print("\nColumn mapping:")
for i, h in enumerate(headers):
    print(f"{i}: {h}")

# Identify key columns
health_facility_idx = headers.index('Health Facility')
numeric_columns = [
    'MUAC Screeninig (mm) | Normal >= 125',
    'MUAC Screeninig (mm) | MAM 115 - 124',
    'MUAC Screeninig (mm) | SAM <115',
    'MUAC Screenings (mm) | Oedema +, ++, +++',
    'Total Children Vaccinated by Age | 0 to 12',
    'Total Children Vaccinated by Age | 12 to 24',
    'Total Children Vaccinated by Age | above 24',
    'Vaccination status of a Child | Zero Dose',
    'Vaccination status of a Child | Defaulter',
    'Vaccination status of a Child | On Schedule',
    'all_child'
]

# Get indices for numeric columns
numeric_indices = {}
for col in numeric_columns:
    if col in headers:
        numeric_indices[col] = headers.index(col)

print(f"\n\nNumeric columns found: {len(numeric_indices)}")

# Group by Health Facility
aggregated = defaultdict(lambda: {col: 0 for col in numeric_columns if col in headers})
facilities = set()

# Parse data rows
for row in rows[1:]:  # Skip header
    cells = row.findall('.//x:c', ns)
    cell_values = {}

    # Extract cell values
    for cell in cells:
        ref = cell.get('r')  # e.g., "A2", "B2"
        col_letter = ''.join(filter(str.isalpha, ref))
        col_idx = 0
        for i, c in enumerate(col_letter):
            col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
        col_idx -= 1

        if col_idx < len(headers):
            value_elem = cell.find('.//x:v', ns)
            if value_elem is not None:
                cell_values[col_idx] = value_elem.text

    # Get facility name
    if health_facility_idx in cell_values:
        facility = cell_values[health_facility_idx]
        facilities.add(facility)

        # Sum numeric values
        for col_name, col_idx in numeric_indices.items():
            if col_idx in cell_values:
                try:
                    value = float(cell_values[col_idx])
                    aggregated[facility][col_name] += value
                except:
                    pass

print(f"\n\nTotal unique facilities: {len(facilities)}")
print("\nFacilities found:")
for i, fac in enumerate(sorted(facilities), 1):
    print(f"{i}. {fac}")

# Save aggregated data
output = {}
for facility, data in aggregated.items():
    output[facility] = {k: int(v) for k, v in data.items()}

with open('aggregated_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n\nAggregated data saved to aggregated_data.json")
print(f"Sample (first facility):")
first_fac = sorted(facilities)[0]
print(f"\n{first_fac}:")
for k, v in sorted(output[first_fac].items()):
    if v > 0:
        print(f"  {k}: {v}")
