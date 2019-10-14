import glob
import re
import csv
from datetime import datetime, timedelta
import pytz


lines = []


filesLevel3 = glob.glob('data/itp/level3/itp*grd*dat')
filesLevel2 = glob.glob('data/itp/level2/itp*grd*dat')


itpsLevel2 = set(re.findall('itp\d+', ','.join(filesLevel2)))
itpsLevel3 = set(re.findall('itp\d+', ','.join(filesLevel3)))


with open("data/produced-csvs/level3and2.csv", "w") as f_csv:
    wr = csv.writer(f_csv, quoting=csv.QUOTE_NONE)

    for file in filesLevel3:
        with open(file) as f:
            content = f.readlines()

            itp = int(content[0].split()[1][:-1])
            profile = int(content[0].split()[3][:-1])
            year = int(content[1].split()[0])
            day = float(content[1].split()[1])
            timestamp = round((datetime(year=year, month=1, day=1, tzinfo=pytz.UTC) + timedelta(days=(day - 1))).timestamp())
            longitude = content[1].split()[2]
            latitude = content[1].split()[3]

            for observation in content[3:-1]:
                pressure = observation.split()[0]
                temperature = observation.split()[1]
                salinity = observation.split()[2][:-1] if observation.split()[2][:-1] != 'Na' else None

                lines.append([itp, profile, timestamp, latitude, longitude, pressure, temperature, salinity])

    for itp in itpsLevel2.difference(itpsLevel3):
        files = glob.glob('data/itp/level2/' + itp + '*grd*dat')

        for file in files:
            with open(file) as f:
                content = f.readlines()

                itp = int(content[0].split()[1][:-1])
                profile = int(content[0].split()[3][:-1])
                longitude = content[1].split()[2]
                latitude = content[1].split()[3]

                for observation in content[3:-1]:
                    year = int(observation.split()[0])
                    day = float(observation.split()[1])
                    pressure = observation.split()[2]
                    temperature = observation.split()[3]
                    salinity = observation.split()[4]
                    timestamp = round((datetime(year=year, month=1, day=1, tzinfo=pytz.UTC) + timedelta(days=(day - 1))).timestamp())

                    lines.append([itp, profile, timestamp, latitude, longitude, pressure, temperature, salinity])

    wr.writerows(lines)
