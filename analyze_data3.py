import pandas as pd

# Load the vaccine doses reference table to get the full mapping
doses_df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\vaccine_doses_tb.xlsx')

print('='*60)
print('COMPLETE VACCINE_DOSES_ID to NAME MAPPING')
print('='*60)
dose_mapping = doses_df[['VACCINE_DOSES_ID', 'VACCINE_DOSES_NAME']].drop_duplicates()
for _, row in dose_mapping.sort_values('VACCINE_DOSES_ID').iterrows():
    print(f"  {row['VACCINE_DOSES_ID']}: {row['VACCINE_DOSES_NAME']}")

# Load PHC center reference table for facility names
print('\n' + '='*60)
print('COMPLETE PHC_CENTER_ID to NAME MAPPING')
print('='*60)
phc_df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\phc_center_tb.xlsx')
phc_mapping = phc_df[['PHC_CENTER_ID', 'NAME_EN', 'NAME_AR']].drop_duplicates()
for _, row in phc_mapping.sort_values('PHC_CENTER_ID').iterrows():
    print(f"  {row['PHC_CENTER_ID']}: {row['NAME_EN']} / {row['NAME_AR']}")

# Load person_vaccine_tb to check which PHC IDs are actually used
print('\n' + '='*60)
print('PHC IDs USED IN person_vaccine_tb')
print('='*60)
person_vaccine_df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\person_vaccine_tb.xlsx')
used_phc_ids = set(person_vaccine_df['PHC_SERVICE_PROVIDER_ID'].unique())
print(f"Number of unique PHC IDs used: {len(used_phc_ids)}")

# Create a mapping dictionary from PHC_CENTER_ID to name
phc_dict = dict(zip(phc_df['PHC_CENTER_ID'], phc_df['NAME_EN']))

print('\n' + '='*60)
print('FACILITY NAMES FOR PHC IDs USED IN DATA (with record counts)')
print('='*60)
phc_counts = person_vaccine_df['PHC_SERVICE_PROVIDER_ID'].value_counts()
for phc_id in sorted(used_phc_ids):
    name = phc_dict.get(phc_id, 'UNKNOWN')
    count = phc_counts.get(phc_id, 0)
    print(f"  {phc_id}: {name} ({count} records)")
