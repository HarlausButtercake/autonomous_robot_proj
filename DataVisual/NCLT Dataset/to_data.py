import csv
import math


def getline(num):
    with open('ms_trim.csv', newline='') as l_csvfile:
        l_csvreader = csv.reader(l_csvfile)
        for l_i, l_row in enumerate(l_csvreader):
            if l_i == num:
                # if row[1] == "N/A" or row[1] == 0:
                #     continue
                l_data = {
                    'time': (l_row[0]),
                    'hx': float(l_row[1]),
                    'hy': float(l_row[2]),
                    'ax': float(l_row[3]),
                    'ay': float(l_row[4]),
                    'gz': float(l_row[5])
                }
                return l_data


def l_get_bearing(x, y):
    declination = -(1 + 56 / 60)
    bearing = math.atan2(y, x)
    if bearing < 0:
        bearing += 2 * math.pi
    if bearing > 2 * math.pi:
        bearing -= 2 * math.pi
    bearing = math.degrees(bearing) + declination
    return bearing


with open('gps_1hz.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):

        data = {
            'time': int(row[0]),
            'lat': float(row[1]),
            'lon': float(row[2])
        }
        for k in range(10):
            print(f"Currently at {i} {k}")
            data2 = getline(i + k + 1)
            write_data = {
                'time': data2['time'],
                'lat': data['lat'],
                'lon': data['lon'],
                'Ax': data2['ax'],
                'Ay': data2['ay'],
                'Gz': data2['gz'],
                'bearing': l_get_bearing(data2['hx'], data2['hy'])
            }
            with open('../ULIS_France_Straight/final_data.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['time', 'lat', 'lon', 'Ax', 'Ay', 'Gz', 'bearing'])
                writer.writerow(write_data)

