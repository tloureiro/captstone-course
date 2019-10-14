import dask.dataframe as dd
import csv
dfITP = dd.read_csv('data/produced-csvs/level3and2.csv', names=['itp', 'profile', 'timestamp', 'latitude', 'longitude', 'pressure', 'temperature', 'salinity'],
                    dtype={'latitude': 'str', 'longitude': 'str', 'pressure': 'str', 'temperature': 'str', 'salinity': 'str'})
dfITP = dfITP.compute()
dfITP.sort_values(by=['timestamp'], inplace=True)
dfITP.to_csv('data/produced-csvs/level3and2-ordered-by-timestamp.csv', index=False, header=False,quoting=csv.QUOTE_NONE)