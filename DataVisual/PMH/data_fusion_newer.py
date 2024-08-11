import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import func




# def get_F(delta):
#     F = np.array([[1, 0, delta, 0, (delta ** 2) / 2, 0, 0],    # x
#                   [0, 1, 0, delta, 0, (delta ** 2) / 2, 0],    # y
#                   [0, 0, 1, 0, delta, 0, 0],                        # vx
#                   [0, 0, 0, 1, 0, delta, 0],                       # vx
#                   [0, 0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0, 0],
#                   [0, 0, 0, 0, 0, 0, 1]])                       # theta
#     return F


# def kalman_predict(X0, P0, l_Qk, Fk, l_ax, l_ay, w, t):
#     m = t ** 2 / 2
#     B1 = np.array([[0],
#                    [0],
#                    [0],
#                    [0],
#                    [l_ax],
#                    [l_ay],
#                    [t * w]])
#     # B2 = np.array([[0], [0], [0], [0]])
#     Xp = Fk.dot(X0) + B1
#
#     Pp = (Fk.dot(P0)).dot(Fk.T) + l_Qk
#     return Xp, Pp




# def kalman_update(l_x, l_y, l_Xp, l_Pp):
#     l_H = np.eye(7)
#     l_zh = np.array([l_Xp[0][0], l_Xp[1][0]])
#     l_z = np.array([l_x, l_y])
#
#     l_K = (l_H.dot(l_Pp)).dot(np.linalg.inv((l_H.dot(l_Pp)).dot(l_H.T) + (np.eye(2) * 100)))
#     r_x = l_Xp + l_K.dot((l_z - l_zh))
#     r_p = (np.eye(6) - l_K.dot(l_H)).dot(l_Pp)
#     return r_x, r_p


def gps_to_x_y(lat_ori, lng0, lat_tar, lng):
    re = 6378135
    rp = 6356750

    t = re * np.cos(lat0) * re * np.cos(lat0) + rp * np.sin(lat0) * rp * np.sin(lat0)
    rns = (re * rp * re * rp) / (t * np.sqrt(t))
    rew = re * re / (np.sqrt(t))

    dLat = lat_tar - lat_ori
    dLng = lng - lng0

    # rns = 6343618.3790280195
    # rew = 6380879.425381593

    r_y = rns * np.sin(dLat)
    r_x = rew * np.sin(dLng) * np.cos(lat0)

    return r_x, r_y


def xy_to_gps(lat_ori, lng0, x_tar, y_tar):
    # dLat = lat - lat0
    # dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    dLat = np.asin(y_tar / rns)
    dLng = np.asin(x_tar / rew / np.cos(lat_ori))

    r_lat = dLat + lat_ori
    r_long = dLng + lng0
    return r_lat, r_long


def distance_cal(r_x, r_y, x_d, y_d):
    return np.sqrt((r_x - x_d) ** 2 + (r_y - y_d) ** 2)


def rad_angle_to_oy(x0, y0, r_x, r_y):
    dx = r_x - x0
    dy = r_y - y0
    dot = dx * 0 + dy * 1
    a = np.sqrt(dx**2 + dy**2)
    b = 1
    if a == 0:
        return 0
    if r_y > 0:
        return np.acos(dot / a)
    else:
        return 2 * np.pi - np.acos(dot / a)



prev_lat = None
prev_lon = None
prev_time = None

########################################################################################

H = np.eye(5)  # transition matrix H, observation model

Qk = np.eye(5) * 0.001 #Qk
P_pred = np.eye(5) * 5
#Noise from measurement
#Assume that error ~ 0.05
Rk = np.eye(5)*0.05 #Rk
# Rk = np.array([[10, 0, 0, 0, 0],
#                [0, 10, 0, 0, 0],
#                [0, 0, 10000, 0, 0],
#                [0, 0, 0, 10000, 0],
#                [0, 0, 0, 0, 0.01]])
########################################################################################
# file_name = 'final_data.csv'
# begin = 0
# data = {
#                 'time',
#                 'lat',
#                 'lon',
#                 'Ax',
#                 'Ay',
#                 'Gz',
#                 'bearing'
#             }
# with open(file_name, newline='') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for i, row in enumerate(csvreader):
#         if i == 0:
#             data = {
#                 'time': row[0],
#                 'lat': float(row[1]),
#                 'lon': float(row[2]),
#                 'Ax': float(row[3]),
#                 'Ay': float(row[4]),
#                 'Gz': float(row[5]),
#                 'bearing': float(row[6])
#             }

column_names = ['UTIME', 'Fixmode', 'NumberOfSatelines', 'Latitude', 'Longtitude', 'Altitude', 'Track', 'Speed']
gps_data = pd.read_csv('gps.csv', names=column_names)
# Calculate value for GPS
lat0 = gps_data.iloc[0]['Latitude']
lon0 = gps_data.iloc[0]['Longtitude']



# Read IMU data
column_names = ['UTIME', 'Mx', 'My', 'Mz', 'X_a', 'Y_a', 'Z_a', 'X_r', 'Y_r', 'Z_r']
imu_data = pd.read_csv('ms25.csv', names=column_names)
imu_data['X_a'] = pd.to_numeric(imu_data['X_a'], errors='coerce')
imu_data['Z_r'] = pd.to_numeric(imu_data['Z_r'], errors='coerce')

utime = 0
indexOfImu = 2
x_recorded = []

y_recorded = []
length = 5000

x_gps = []
y_gps = []
x_gps.append(0)
y_gps.append(0)

x_p = 0
y_p = 0

# X_est = np.zeros((5, 1))
X_est = np.array([[0], [0], [0], [0], [np.deg2rad(300)]])
P_est = np.eye(5) * 5
# prev_time_gps = func.time_parser(data['time'])
prev_time_gps = gps_data.iloc[0]['UTIME']
# prev_time = prev_time_gps
Z = X_est
theta = 0

x_geo = []
y_geo = []
x_coord = []
y_coord = []
lat_fused = []
long_fused = []
bearing_arr = []
error =[]
for i in range(1, 3000):
    # if (gps_data.iloc[i]['Fixmode'] == 2 or gps_data.iloc[i]['Fixmode'] == 3):
    utime = gps_data.iloc[i]['UTIME']
    lat = gps_data.iloc[i]['Latitude']
    lon = gps_data.iloc[i]['Longtitude']
    # get previous x and y
    x, y = gps_to_x_y(lat0, lon0, lat, lon)

    x_previous = x_gps[-1]
    y_previous = y_gps[-1]

    # check if robot not move so skip calculate angle.
    # if x != x_previous:
    #     angle = np.arctan((y - y_previous) / (x - x_previous))
    # else:
    #     if y != y_previous:
    #         angle = np.pi / 2  # 90 degrees if x and x_previous are the same but y is different
    #     else:
    #         continue  # use previous state if both x and y are the same


    x_gps.append(x)
    y_gps.append(y)
    vx = gps_data.iloc[i]['Speed']

    if (pd.isna(vx)):  # check if vx is number or NaN
        vx = gps_data.iloc[i + 1]['Speed']

    # fusion
    while utime > imu_data.iloc[indexOfImu]['UTIME']:
        # prev_time = imu_data.iloc[indexOfImu]['UTIME']
        deltaT = (imu_data.iloc[indexOfImu]['UTIME'] - imu_data.iloc[indexOfImu - 1]['UTIME']) / 1000000

        ax = imu_data.iloc[indexOfImu - 1]['X_a']
        omega = imu_data.iloc[indexOfImu - 1]['Z_r']
        X_pred, P_pred = func.kalman_predict(X_est, P_pred, Qk, ax, np.deg2rad(omega), deltaT)

        indexOfImu += 1

        X_est = X_pred
        P_est = P_pred

        x_coord.append(X_est[0][0])
        y_coord.append(X_est[1][0])

            # update matrix
    theta = rad_angle_to_oy(x_previous, y_previous, x, y)
    # deltaT_gps = (utime - prev_time_gps) # / (10 ** 6)
    deltaT_gps = (gps_data.iloc[i]['UTIME'] - gps_data.iloc[i - 1]['UTIME']) / (10 ** 6)
    prev_time_gps = utime
    if x != x_previous and y != y_previous:
        # Z = np.array([[x], [y], [(x - x_previous) / deltaT_gps], [(y - y_previous) / deltaT_gps], [theta]])
        Z = np.array([[x], [y], [vx * np.sin(theta)], [vx * np.cos(theta)], [theta]])
    X_pred, P_pred = func.kalman_update(X_pred, P_pred, H, Rk, Z)

    X_est = X_pred
    P_est = P_pred

    x_coord.append(X_est[0][0])
    y_coord.append(X_est[1][0])



# Plot (x, y)
plt.plot(x_coord, y_coord, color='blue', label='filtered')
plt.plot(x_gps, y_gps, color="red", label='ground truth')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('(X, Y)')



# count = 0
# with open('rtk_xy.txt', 'r') as file:
#     for line in file:
#         # if count >= 300:
#         #     break
#         fields = line.strip().split(' ')
#         x_rtk.append(float(fields[0]))
#         y_rtk.append(float(fields[1]))
#         count = count + 1
#
# plt.plot(x_rtk, y_rtk, color='green', label='RTK-GPS(pseudo-groundtruth)')
# bearing_rad = np.deg2rad(bearing_arr)
# bearing_rad = bearing_arr
# plt.quiver(x_coord, y_coord, np.sin(bearing_rad), np.cos(bearing_rad), angles='xy', scale_units='xy', scale=0.05, color='red')

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Scatter Plot of Points')
# plt.xlim(-30, 30)
# plt.gca().invert_yaxis()

plt.legend()

plt.show()





