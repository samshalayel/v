import pandas as pd
import json

# Read Excel file
df = pd.read_excel('170120261350.xlsx')

# Print column names
print("=" * 80)
print("COLUMNS IN EXCEL FILE:")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print("\n" + "=" * 80)
print("SAMPLE DATA (First 3 rows):")
print("=" * 80)
print(df.head(3).to_string())

print("\n" + "=" * 80)
print("GOVERNORATE VALUES:")
print("=" * 80)
if 'Governorate' in df.columns:
    print(df['Governorate'].unique())
else:
    print("Governorate column not found!")

print("\n" + "=" * 80)
print("DATA SUMMARY:")
print("=" * 80)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
