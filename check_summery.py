import pandas as pd

df = pd.read_excel('data/summery.xlsx')
print('Records:', len(df))
print('Columns:', df.columns.tolist())
print()
print('First 3 rows:')
print(df.head(3))
