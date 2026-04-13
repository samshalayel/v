import pandas as pd

# Read the Excel file
df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\person_vaccine_tb.xlsx')

print('='*60)
print('VACCINE_DOSES_ID - All Unique Values')
print('='*60)
print(sorted(df['VACCINE_DOSES_ID'].unique()))

print('\n' + '='*60)
print('PHC_SERVICE_PROVIDER_ID - All Unique Values')
print('='*60)
print(sorted(df['PHC_SERVICE_PROVIDER_ID'].unique()))

print('\n' + '='*60)
print('PHC_ENTRY_ID - All Unique Values')
print('='*60)
print(sorted(df['PHC_ENTRY_ID'].unique()))

print('\n' + '='*60)
print('Value Counts for Key Columns')
print('='*60)

print('\nVACCINE_DOSES_ID value counts:')
print(df['VACCINE_DOSES_ID'].value_counts().sort_index())

print('\nCHILDREN_AGE_TYPE value counts:')
print(df['CHILDREN_AGE_TYPE'].value_counts().sort_index())

print('\nCHILD_VACCINATION_STATUS value counts:')
print(df['CHILD_VACCINATION_STATUS'].value_counts().sort_index())

print('\nCAMP_ID value counts:')
print(df['CAMP_ID'].value_counts().sort_index())

print('\nMUAC_ID value counts:')
print(df['MUAC_ID'].value_counts().sort_index())

print('\nPHC_SERVICE_PROVIDER_ID value counts (top 20):')
print(df['PHC_SERVICE_PROVIDER_ID'].value_counts().head(20))

print('\n' + '='*60)
print('VACCINATION_DATE distribution')
print('='*60)
print(df['VACCINATION_DATE'].value_counts().sort_index())

# Check if there are related tables for vaccine doses info
print('\n' + '='*60)
print('Trying to load vaccine_doses_tb.xlsx for reference')
print('='*60)
try:
    doses_df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\vaccine_doses_tb.xlsx')
    print('Columns:', list(doses_df.columns))
    print('\nFirst 10 rows:')
    print(doses_df.head(10).to_string())
except Exception as e:
    print(f'Error: {e}')

# Check phc_center_tb for facility names
print('\n' + '='*60)
print('Trying to load phc_center_tb.xlsx for facility names')
print('='*60)
try:
    phc_df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\phc_center_tb.xlsx')
    print('Columns:', list(phc_df.columns))
    print('\nFirst 10 rows:')
    print(phc_df.head(10).to_string())
except Exception as e:
    print(f'Error: {e}')
