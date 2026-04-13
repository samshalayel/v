import pandas as pd
import json

# Read Excel file
excel_file = "S123_2adf56689a684dc2b08d6be6b905a2d6_EXCEL (22).xlsx"
df = pd.read_excel(excel_file)

# Display column names
print("Column names:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nData types:")
print(df.dtypes)
print(f"\nTotal rows: {len(df)}")
