import pandas as pd 
import numpy as np 
from pathlib import Path 
np.random.seed(42) 
Path('data').mkdir(exist_ok=True) 
dates = pd.date_range('2014-01-01', '2026-04-01', freq='MS') 
selic, val = [], 11.0 
for i in range(len(dates)): 
    val = max(2.0, min(14.75, val + 0.05)) 
    selic.append(round(val, 2)) 
pd.DataFrame({'data': dates, 'selic': selic}).to_csv('data/selic.csv', index=False) 
ipca, val = [], 0.48 
for i in range(len(dates)): 
    val = max(-0.5, min(1.8, val + 0.01)) 
    ipca.append(round(val, 2)) 
pd.DataFrame({'data': dates, 'ipca': ipca}).to_csv('data/ipca.csv', index=False) 
cambio, val = [], 2.35 
for i in range(len(dates)): 
    val = max(1.8, min(6.2, val + 0.03)) 
    cambio.append(round(val, 4)) 
pd.DataFrame({'data': dates, 'cambio_usd': cambio}).to_csv('data/cambio_usd.csv', index=False) 
print('CSVs criados!') 
