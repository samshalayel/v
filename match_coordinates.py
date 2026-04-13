import xml.etree.ElementTree as ET
import json
from collections import defaultdict
import math

# Parse XML to get all records with coordinates
tree = ET.parse('sheet_data.xml')
root = tree.getroot()
ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
rows = root.findall('.//x:row', ns)

# Parse header
headers = []
for cell in rows[0].findall('.//x:c', ns):
    value = cell.find('.//x:v', ns)
    if value is not None:
        headers.append(value.text)

health_facility_idx = headers.index('Health Facility')
x_idx = headers.index('x')
y_idx = headers.index('y')

# Collect all records with their coordinates
records = []
for row in rows[1:]:
    cells = row.findall('.//x:c', ns)
    cell_values = {}

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

    if health_facility_idx in cell_values and x_idx in cell_values and y_idx in cell_values:
        facility = cell_values[health_facility_idx]
        x = float(cell_values[x_idx])
        y = float(cell_values[y_idx])

        if x != 0 and y != 0:
            records.append({
                'facility': facility,
                'lon': x,
                'lat': y
            })

print(f"Total records with coordinates: {len(records)}")

if len(records) == 0:
    print("\nNo valid coordinates found in Excel data!")
    print("The x and y columns in the Excel file appear to be empty or zero.")
    print("\nShowing first few facility names from Excel:")

    facilities = []
    for row in rows[1:11]:  # First 10 rows
        cells = row.findall('.//x:c', ns)
        cell_values = {}

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

        if health_facility_idx in cell_values:
            print(f"  - {cell_values[health_facility_idx]}")

    print("\nYou need to either:")
    print("1. Provide the original shapefile or layer that has facility names")
    print("2. Manually create a mapping file between point numbers (1-123) and facility names")
    print("3. Export the data from QGIS again with all attributes included")
