import pandas as pd

# Check all sheets in the file
xl = pd.ExcelFile('data/280120261153.xlsx')
print('Sheets in file:', xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'\n=== Sheet: {sheet} ===')
    print(f'Records: {len(df)}')
    print(f'Columns: {df.columns.tolist()[:10]}...')
