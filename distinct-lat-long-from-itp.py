import pandas as pd
import csv

dfITP = pd.read_csv('data/produced-csvs/level3and2.csv', names=['itp', 'profile', 'timestamp', 'latitude', 'longitude', 'pressure', 'temperature', 'salinity'],
                    dtype={'latitude': 'str', 'longitude': 'str', 'pressure': 'str', 'temperature': 'str', 'salinity': 'str'})

distinctLatLong = dfITP[['latitude', 'longitude']].drop_duplicates()

distinctLatLong.to_csv('data/produced-csvs/distinct-lat-long-from-itp.csv', index=False, header=False, quoting=csv.QUOTE_NONE)
