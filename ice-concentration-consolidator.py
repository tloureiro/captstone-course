import glob
import netCDF4
import csv
import multiprocessing
import pytz
from datetime import datetime
import sys
import pickle

def process_file(file, progress):
    rows = []

    print(progress, file)
    dataset = netCDF4.Dataset(file)

    temp_date = netCDF4.num2date(dataset.variables['time'][0], dataset.variables['time'].units)
    t = int(datetime(year=temp_date.year, month=temp_date.month, day=temp_date.day, tzinfo=pytz.UTC).timestamp())

    latitudes = dataset.variables['latitude'][:]
    longitudes = dataset.variables['longitude'][:]
    concentrations = dataset.variables['Sea_Ice_Concentration_with_Final_Version'][:]

    for i in range(latitudes.shape[0]):
        for j in range(latitudes.shape[1]):
            concentration = int(concentrations[0][i][j])
            rows.append([i, j, t, concentration])
    return rows


if len(sys.argv) == 2:
    year = sys.argv[1]
else:
    year = '2015'

files = glob.glob('data/sea-ice-concentration/netcdf-interval/nt_' + year +'[0-9][0-9][0-9][0-9]_*')
# files = glob.glob('data/sea-ice-concentration/netcdf-interval/nt_2018010[0-9]_*')
# files = glob.glob('data/sea-ice-concentration/netcdf-interval/nt_201801[0-9][0-9]_*')
# files = glob.glob('data/sea-ice-concentration/netcdf-interval/nt_20110111_f17_v1.1_n_reformat.nc')

pool = multiprocessing.Pool(4)
results = []
z = 0
progress = 1

with open("data/produced-csvs/ice-concentration/ice-concentration-" + year + ".csv", "w") as f_csv:

    wr = csv.writer(f_csv)
    for file in files:
        result = pool.apply_async(process_file, args=[file, progress])
        results.append(result)

        if z == 200:
            # now flush the results
            for result in results:
                result.wait()
                wr.writerows(result.get())
            # reset everything
            z = 0
            results = []
        z += 1
        progress += 1

    # flush what's left
    for result in results:
        result.wait()
        wr.writerows(result.get())

    pool.close()


#now serialise dict for future use
data = {}
grid_width = 304
grid_height = 448

with open('data/produced-csvs/ice-concentration/ice-concentration-' + year + '.csv') as f:
# with open('data/produced-csvs/ice-concentration/ice-concentration-2017partial.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        x = int(line[0])
        y = int(line[1])

        temp_date = datetime.utcfromtimestamp(int(line[2]))
        d = datetime(year=temp_date.year, month=temp_date.month, day=temp_date.day, tzinfo=pytz.UTC)

        concentration = int(line[3])

        key = str(d.day) + '#' + str(d.month)
        if key not in data:
            grid = [[None for x in range(grid_width)] for y in range(grid_height)]
            data[key] = grid

        data[key][x][y] = concentration


with open('data/produced-csvs/ice-concentration/ice-concentration-' + year + '.csv.dict', 'wb') as pickle_out_dict:
    pickle.dump(data, pickle_out_dict)


# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2004
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2005
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2006
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2007
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2008
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2009
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2010
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2011
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2012
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2013
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2014
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2015
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2016
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2017
# python3 6.2-sea-ice-concentration-consolidator-parallel.py 2018
