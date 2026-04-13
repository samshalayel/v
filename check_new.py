import pandas as pd

# Re-read the file to check for new data
xl = pd.ExcelFile('data/280120261153.xlsx')
print('Sheets:', xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'\n=== {sheet} ===')
    print(f'Records: {len(df)}')
    print(f'Columns: {list(df.columns)}')
    if len(df) > 0:
        print(df.head(2))
