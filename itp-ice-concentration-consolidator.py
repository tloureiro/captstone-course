import csv
from datetime import datetime
import pandas as pd
import pytz
import os.path
import pickle

ice_concentration_data = None
a = None


def main():
    global ice_concentration_data, a
    df_itp = pd.read_csv('data/produced-csvs/level3and2-ordered-by-timestamp.csv',
             names=['itp', 'profile', 'timestamp', 'latitude', 'longitude', 'pressure', 'temperature', 'salinity'],
             dtype={'latitude': 'str', 'longitude': 'str', 'pressure': 'str', 'temperature': 'str', 'salinity': 'str'})
    ice_concentration_data = []
    ice_concentration_data.append(2004)
    ice_concentration_data.append(get_ice_concentration_by_year(2004))
    lat_long_to_grid = get_lat_long_to_grid_dictionary()
    df_itp['radius0'], df_itp['radius1'], df_itp['radius2'], df_itp['radius5'], df_itp['radius10'] = \
        zip(*df_itp.apply(lambda x: ice_concentration_mapper(x['timestamp'], x['latitude'], x['longitude'], ice_concentration_data, lat_long_to_grid, [0, 1, 2, 5, 10]), axis=1))

    df_itp.to_csv('data/produced-csvs/final.csv', index=False, header=False, quoting=csv.QUOTE_NONE)

def ice_concentration_mapper(timestamp, latitude, longitude, ice_concentration_data, lat_long_to_grid, radius):

    result = []

    temp_date = datetime.utcfromtimestamp(timestamp)
    date = datetime(year=temp_date.year, month=temp_date.month, day=temp_date.day, tzinfo=pytz.UTC)

    year = date.year
    if ice_concentration_data[0] != year:
        ice_concentration_data[0] = year
        ice_concentration_data[1] = get_ice_concentration_by_year(year)

    ice_concentrations = ice_concentration_data[1]

    if latitude + '#' + longitude not in lat_long_to_grid:
        print('lat long not found')
        result = [-1] * len(radius)
    elif str(date.day) + '#' + str(date.month) not in ice_concentrations:
        print('day not found')
        result = [-2] * len(radius)
    else:
        grid_xy = lat_long_to_grid[latitude + '#' + longitude]

        row = grid_xy[0]
        column = grid_xy[1]

        for k in range(len(radius)):
            total_area = 0
            total_cells = 0

            key = str(date.day) + '#' + str(date.month)

            for i in range(-radius[k], radius[k] + 1):
                for j in range(-radius[k], radius[k] + 1):
                    if 0 <= (row + i) < len(ice_concentrations[key]) and \
                                0 <= (column + j) < len(ice_concentrations[key][0]) and \
                                ice_concentrations[key][row + i][column + j] <= 250:

                        total_area += ice_concentrations[key][row + i][column + j]
                        total_cells += 1

            if total_cells > 0:
                result.append(float('{0:.2f}'.format( total_area/(total_cells * 250) * 100 )))
            else:
                result.append(-3)

    return result


def get_lat_long_to_grid_dictionary():
    dict = {}
    with open('data/produced-csvs/itp-lat-long-to-grid.csv') as f:
        reader = csv.reader(f)
        for line in reader:
            lat = line[0].split('#')[0]
            long = line[0].split('#')[1]
            x = int(line[1])
            y = int(line[2])
            dict[lat + '#' + long] = [x, y]

    return dict

def get_ice_concentration_by_year(year):

    print('loading year ' + str(year))

    data = {}

    if os.path.exists('data/produced-csvs/ice-concentration/ice-concentration-' + str(year) + '.csv.dict'):
        with open('data/produced-csvs/ice-concentration/ice-concentration-' + str(year) + '.csv.dict', 'rb') as pickle_in:
            data = pickle.load(pickle_in)
    else:
        grid_width = 304
        grid_height = 448

        with open('data/produced-csvs/ice-concentration/ice-concentration-' + str(year) + '.csv') as f:
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
    return data


if __name__ == "__main__":
    main()


