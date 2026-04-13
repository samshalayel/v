import pandas as pd

s = pd.read_excel('data/280120261153.xlsx')
print('Records:', len(s))
print('Columns:', s.columns.tolist())
