import netCDF4
from haversine import haversine
import csv
import pandas as pd


def calc_distance(x, y):
    global shortestDistance, shortestDistanceWasUpdated, testedCoordinatesXY,  \
        itpLat, itpLong, nextPointerXY, shortestDistanceLatLong, shortestDistanceXY

    if x != -1 and x != gridWidth and y != -1 and y != gridHeight and str(x) + '#' + str(y) not in testedCoordinatesXY:
        testingPointerXY = [x, y]
        gridLatLong = [latitudes[testingPointerXY[0]][testingPointerXY[1]], longitudes[testingPointerXY[0]][testingPointerXY[1]]]
        distance = haversine(gridLatLong, [float(itpLat), float(itpLong)])
        testedCoordinatesXY.add(str(testingPointerXY[0]) + '#' + str(testingPointerXY[1]))
        if distance < shortestDistance:
            shortestDistance = distance
            shortestDistanceLatLong = gridLatLong
            shortestDistanceWasUpdated = True
            nextPointerXY = shortestDistanceXY = testingPointerXY

file = 'data/sea-ice-concentration/netcdf-interval/nt_20110111_f17_v1.1_n_reformat.nc'

dataset = netCDF4.Dataset(file)

latitudes = dataset.variables['latitude'][:]
longitudes = dataset.variables['longitude'][:]
x = dataset.variables['x'][:]
y = dataset.variables['y'][:]


coordinates = []

gridHeight = latitudes.shape[0]
gridWidth = latitudes.shape[1]

#build the x y lat long object first
for i in range(gridHeight):
    coordinates.append([])
    for j in range(gridWidth):
        coordinates[i].append([latitudes[i][j], longitudes[i][j]])

dict = {}

#load distinct coordinates and
z = 0
with open("data/produced-csvs/distinct-lat-long-from-itp.csv", "r") as f:
    reader = csv.reader(f)
    for line in reader:
        itpLat = line[0]
        itpLong = line[1]
        key = itpLat + '#' + itpLong

        # calculate shortest distance
        shortestDistance = None
        shortestDistanceLatLong = None
        shortestDistanceXY = None

        nextPointerXY = [224, 152]
        currentDistance = None
        shortestDistanceWasUpdated = True
        testedCoordinatesXY = set()

        while shortestDistanceWasUpdated:

            # test everything around next pointer, including nextPointer, that was not tested yet

            # test self, test u, test ur, test r, test dr, test d, test dl, test l, test ul

            # it will only enter here in the first iteration
            if str(nextPointerXY[0]) + '#' + str(nextPointerXY[1]) not in testedCoordinatesXY:
                testingPointerXY = shortestDistanceXY = nextPointerXY
                gridLatLong = [latitudes[testingPointerXY[0]][testingPointerXY[1]], longitudes[testingPointerXY[0]][testingPointerXY[1]]]
                shortestDistance = haversine(gridLatLong , [float(itpLat), float(itpLong)])
                shortestDistanceLatLong = gridLatLong
                testedCoordinatesXY.add(str(testingPointerXY[0]) + '#' + str(testingPointerXY[1]))

            # now lets test everything around
            shortestDistanceWasUpdated = False

            calc_distance(nextPointerXY[0]    , nextPointerXY[1] + 1) # r
            calc_distance(nextPointerXY[0] + 1, nextPointerXY[1] + 1)  # dr
            calc_distance(nextPointerXY[0] + 1, nextPointerXY[1]) #d
            calc_distance(nextPointerXY[0] + 1, nextPointerXY[1] - 1) #dl
            calc_distance(nextPointerXY[0]    , nextPointerXY[1] - 1) #l
            calc_distance(nextPointerXY[0] - 1, nextPointerXY[1] - 1) #ul
            calc_distance(nextPointerXY[0] - 1, nextPointerXY[1]) #u
            calc_distance(nextPointerXY[0] - 1, nextPointerXY[1] + 1) #ur

        z += 1
        print(z)

        if shortestDistance < 19:
            dict['#'.join([itpLat, itpLong])] = shortestDistanceXY

l = []
for key, value in dict.items():
    row = []
    row.append(key)
    row.extend(value)
    l.append(row)
pd.DataFrame(l).to_csv('data/produced-csvs/itp-lat-long-to-grid.csv', index=False, header=False,quoting=csv.QUOTE_NONE)

