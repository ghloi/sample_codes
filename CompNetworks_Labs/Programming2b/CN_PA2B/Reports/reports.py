import pandas as pd
import os

directory=os.getcwd()
files=os.listdir(directory)
dataframes=[]
errors=[]
for file in files:
    try:
        df=pd.read_csv(os.path.join(directory, file))
    except Exception as e:
        errors.append(str(e))
        continue
    dataframes.append(df)
try:
    finalDf=pd.concat(dataframes)
    finalDf.to_csv('Final Report.csv')
    
except Exception as e:
    errors.append(str(e))
with open('errors.txt', 'w') as f:
    for line in errors:
        f.write(f'{line}\n')

