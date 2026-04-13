import re
import json

# Read the index.html file
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Define new filters based on the Excel data
new_filters = {
    "Vaccination status of a Child | On Schedule": "int",
    "Vaccination status of a Child | Defaulter": "int",
    "Vaccination status of a Child | Zero Dose": "int",
    "Total Children Vaccinated by Age | above 24": "int",
    "Total Children Vaccinated by Age | 0 to 12": "int",
    "Total Children Vaccinated by Age | 12 to 24": "int",
    "Governorate": "str",
    "Health Facility": "str",
    "Suppervisor Name": "str",
    "all_child": "int"
}

# Convert to JavaScript object string
filters_js = json.dumps(new_filters, ensure_ascii=False)

# Find and replace the Filters variable
pattern = r'var Filters = \{[^}]+\};'
replacement = f'var Filters = {filters_js};'

html_content = re.sub(pattern, replacement, html_content)

# Also update the data source reference if needed
html_content = html_content.replace(
    'src="data/vaccination_data.js"',
    'src="data/location_point_unified_corrected_1.js"'
)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Filters updated successfully!")
print("\nNew filters:")
for key, value in new_filters.items():
    print(f"  - {key}: {value}")
