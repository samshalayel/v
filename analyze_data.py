import pandas as pd

# Read the Excel file
df = pd.read_excel(r'C:\Users\Administrator\gaza_vaccination\data\person_vaccine_tb.xlsx')

print('='*60)
print('1. COLUMN NAMES')
print('='*60)
for i, col in enumerate(df.columns):
    print(f'{i+1}. {col}')

print('\n' + '='*60)
print('2. FIRST 5 ROWS')
print('='*60)
print(df.head().to_string())

print('\n' + '='*60)
print('3. DATA TYPES AND STRUCTURE')
print('='*60)
print(df.dtypes)

print('\n' + '='*60)
print('4. UNIQUE VALUE COUNTS FOR KEY COLUMNS')
print('='*60)
for col in df.columns:
    unique_count = df[col].nunique()
    null_count = df[col].isnull().sum()
    print(f'{col}: {unique_count} unique values, {null_count} nulls')

print('\n' + '='*60)
print('5. SAMPLE UNIQUE VALUES FOR KEY COLUMNS')
print('='*60)

# Show unique values for columns that look like categories
for col in df.columns:
    unique_vals = df[col].dropna().unique()
    if len(unique_vals) <= 20:
        print(f'\n{col}:')
        for val in unique_vals:
            print(f'  - {val}')

print('\n' + '='*60)
print('6. DATAFRAME SHAPE')
print('='*60)
print(f'Rows: {len(df)}, Columns: {len(df.columns)}')
