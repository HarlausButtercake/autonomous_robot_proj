import csv
import math

import numpy as np
from matplotlib import pyplot as plt


def print_line(csv_file_path, num):
    with open(csv_file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i == num - 1:  # 102 because indexing starts at 0
                print(row)
                break

# def to_data(num):
#
#                 return data


def time_parser(time):
    hh, mm, ss = map(int, time.strip().split(':'))
    return hh*3600 + mm*60 + ss

declination = -(1 + 56/60)
bearing = math.atan2(0.0648760497570038, 0.164508059620857)
if bearing < 0:
    bearing += 2 * math.pi
if bearing > 2 * math.pi:
    bearing -= 2 * math.pi
bearing = math.degrees(bearing) + declination
print(bearing)
# x_coord = []
# y_coord = []
# t = []
# with open('Log_ULIS_France_Straight.csv', newline='') as csvfile:
#     csvreader = csv.reader(csvfile)
#     count = 0
#     for i, row in enumerate(csvreader):
#         if i >= 540 - 1:  # 102 because indexing starts at 0
#             data = {
#                 'time': row[0],
#                 'lat': float(row[1]),
#                 'lon': float(row[2]),
#                 'Ax': float(row[3]),
#                 'Ay': float(row[4]),
#                 'Ax_lin': float(row[5]),
#                 'Ay_lin': float(row[6]),
#                 'Gz': float(row[7]),
#                 'bearing': float(row[8])
#             }
#             x_coord.append(data['Ax_lin'])
#             y_coord.append(data['Ay_lin'])
#             t.append(count)
#             count += 1
#
# # Replace 'your_file.csv' with the path to your CSV file
# plt.plot(t, x_coord, color='blue', label='Points')
# plt.plot(t, y_coord, color='red', label='Points')
#
# # plt.quiver(x_coord, y_coord, np.sin(bearing_rad), np.cos(bearing_rad), angles='xy', scale_units='xy', scale=1, color='red')
# plt.xlabel('X Coordinate')
# plt.ylabel('Y Coordinate')
# plt.title('Scatter Plot of Points')
# # plt.gca().invert_yaxis()
#
# plt.legend()
#
# plt.show()