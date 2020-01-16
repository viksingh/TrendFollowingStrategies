import pandas as pd
import glob
import os
import numpy as np
import sys
import time
start_time = time.time()
import os.path
from pathlib import Path

ind_files_directory = '/Users/sakiv/temp/nasdaq/ind/*.txt'
combined_file_path = '/Users/sakiv/temp/nasdaq/combined/stockscombined.csv'


FILEINDEX = 0
STOCKLOOKBACKPERIODMA100 = 100
STOCKLOOKBACKPERIODROC100 = 100

if os.path.exists(combined_file_path):
    os.remove(combined_file_path)
    print('Combined file deleted')

for f in glob.iglob(ind_files_directory):
    my_file = Path(f)
    if ( my_file.is_file() and os.path.getsize(f) > 0 ) :
        FILEINDEX = FILEINDEX + 1
        print("Reading file " +f.lower())
        STOCK = f.split('.')[0].replace('/Users/sakiv/temp/nasdaq/ind/', '')
        dfCurrentStock = pd.read_csv(f, index_col = None, header = 0)



        dfCurrentStockToWrite = pd.DataFrame()
        print(STOCK)
        dfCurrentStockToWrite['PRICE'] = dfCurrentStock['Close']
        dfCurrentStockToWrite['DATE'] = pd.to_datetime(dfCurrentStock['Date'].astype(str), format='%Y-%m-%d')
        dfCurrentStockToWrite['VOLUME'] = dfCurrentStock['Volume']

    #    dfCurrentStockToWrite.apply(lambda row: STOCK, axis=1)
        dfCurrentStockToWrite['STOCK'] = dfCurrentStockToWrite.apply(lambda row: STOCK,axis=1)

        dfCurrentStockToWrite['Weekday'] = pd.DatetimeIndex(dfCurrentStockToWrite['DATE']).dayofweek
        dfCurrentStockToWrite = dfCurrentStockToWrite.query('Weekday == 4')

        dfCurrentStockToWrite = dfCurrentStockToWrite.drop('Weekday', 1)

        # Add moving averages , ROC and percent change
        dfCurrentStockToWrite = dfCurrentStockToWrite.sort_values(by=['DATE'], ascending=[True])
#    df['Date'] = pd.to_datetime(df['Date'].astype(str), format='%Y%m%d')
        decimals = 6
        dfCurrentStockToWrite['MA100'] = dfCurrentStockToWrite['PRICE'].rolling(window=STOCKLOOKBACKPERIODMA100,min_periods=1 ).mean().fillna(0).apply(lambda x: round(x, decimals))
        dfCurrentStockToWrite['MA20'] = dfCurrentStockToWrite['PRICE'].rolling(window=20,min_periods=1 ).mean().fillna(0).apply(lambda x: round(x, decimals))

#        dfCurrentStockToWrite['MA100'] = pd.rolling_mean(dfCurrentStockToWrite['PRICE'],STOCKLOOKBACKPERIODMA100,min_periods=1)
        dfCurrentStockToWrite['PRICE'].rolling(window=STOCKLOOKBACKPERIODMA100).mean().fillna(0).apply(lambda x: round(x, decimals))

        dfCurrentStockToWrite['ROC100'] = ((dfCurrentStockToWrite['PRICE'] / dfCurrentStockToWrite['PRICE'].shift(STOCKLOOKBACKPERIODROC100) - 1) * 100).apply(lambda x: round(x, decimals))
        dfCurrentStockToWrite['STD'] = dfCurrentStockToWrite['PRICE'].rolling(20).std()
        dfCurrentStockToWrite['UPPERBOLLINGER'] =  dfCurrentStockToWrite['MA100'] + 3* dfCurrentStockToWrite['STD']
        dfCurrentStockToWrite['LOWERBOLLINGER'] =  dfCurrentStockToWrite['MA100'] - dfCurrentStockToWrite['STD']


#    df['PerCentChange'] = df['Close'].pct_change().apply(lambda x: round(x, decimals))

        if(FILEINDEX > 1):
            dfCurrentStockToWrite.to_csv(combined_file_path, mode='a', header=False)
        else:
            dfCurrentStockToWrite.to_csv(combined_file_path, mode='a', header=True)


# Use this file to add index crossover : increasing / decreasing : MA > current week, index increasing else decreasing
