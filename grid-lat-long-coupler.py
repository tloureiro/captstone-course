import netCDF4
import csv

file = 'data/sea-ice-concentration/netcdf-interval/nt_20110111_f17_v1.1_n_reformat.nc'

dataset = netCDF4.Dataset(file)

latitudes = dataset.variables['latitude'][:]
longitudes = dataset.variables['longitude'][:]
x = dataset.variables['x'][:]
y = dataset.variables['y'][:]

lines = []

with open("data/produced-csvs/grid-lat-long.csv", "w") as f_csv:

    wr = csv.writer(f_csv)

    for i in range(latitudes.shape[0]):
        for j in range(latitudes.shape[1]):
            lines.append([i, j, latitudes[i][j], longitudes[i][j]])

    wr.writerows(lines)