import csv
import numpy as np

from matplotlib import pyplot as plt

import func
import read_imu
import read_gps


def rad_angle_to_oy(x0, y0, x, y):
    dx = x - x0
    dy = y - y0
    dot = dx * 0 + dy * 1
    a = np.sqrt(dx**2 + dy**2)
    b = 1
    if a == 0:
        return 0
    if y > 0:
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
#Rk = np.eye(4)*0.05 #Rk
Rk = np.array([[10, 0, 0, 0, 0],
               [0, 10, 0, 0, 0],
               [0, 0, 10000, 0, 0],
               [0, 0, 0, 10000, 0],
               [0, 0, 0, 0, 0.01]])

########################################################################################
file_name = 'final_data.csv'
FILE_DATE = "2012-11-16"

######################### 0. INITIALIZE IMPORTANT VARIABLES #################################################################

# CURRENT STATE MODEL IS: X = [x, y, x_dot, y_dot, theta]
# CURRENT INPUT MODEL IS: U = [ax, omega]



gps_data = read_gps.read_gps(FILE_DATE, False)  # 2.5 or 6 Hz
imu_data = read_imu.read_imu(FILE_DATE)  # 47 Hz
# ground_truth = read_ground_truth.read_ground_truth(FILE_DATE, truncation=-1)  # 107 Hz
# Truncate data to first few datapoints, for testing
# ground_truth = ground_truth[:TRUNCATION_END, :]
gps_data = gps_data[:-1, :]
imu_data = imu_data[:-1, :]
# Using the original Unix Timestamp for timesyncing

# x_true = ground_truth[:, 1]  # North
# y_true = ground_truth[:, 2]  # East
# theta_true = ground_truth[:, 3]  # Heading
# true_times = ground_truth[:, 0]

# Generate list of timesteps, from 0 to last timestep in ground_truth
dt = 1 / KALMAN_FILTER_RATE  # 1/Hz = seconds
t = np.arange(ground_truth[0, 0], ground_truth[-1, 0], dt)
N = len(t)
x_est = np.zeros([N, 6])
P_est = np.zeros([N, 6, 6])  # state covariance matrices

# x_est = x | y | xdot | ydot | theta | omega
x_est[0] = np.array([x_true[0], y_true[0], 0, 0, theta_true[0], 0])  # initial state
P_est[0] = np.diag([1, 1, 1, 1, 1, 1])  # initial state covariance TO-DO: TUNE THIS TO TRAIN


    ################################ 1. MAIN FILTER LOOP ##########################################################################

a_x = imu_data[:, 1]
a_y = imu_data[:, 2]
omega = imu_data[:, 3]
theta_imu = euler_data[:, 1]

gps_x = gps_data[:, 1]
gps_y = gps_data[:, 2]

gps_times = gps_data[:, 0]
imu_times = imu_data[:, 0]
gps_counter = 0
imu_counter = 0

prev_gps_counter = -1
prev_imu_counter = -1



################################################################################################################
data = {
                'time',
                'lat',
                'lon',
                'Ax',
                'Ay',
                'Gz',
                'bearing'
            }
with open(file_name, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):
        if i == 0:
            data = {
                'time': row[0],
                'lat': float(row[1]),
                'lon': float(row[2]),
                'Ax': float(row[3]),
                'Ay': float(row[4]),
                'Gz': float(row[5]),
                'bearing': float(row[6])
            }


# data = func.to_data(file_name, begin)
# lat0, lon0 = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
lat0, lon0 = data['lat'], data['lon']

x_p = 0
y_p = 0

# X_est = np.zeros((5, 1))
X_est = np.array([[0], [0], [0], [0], [np.deg2rad(300)]])
P_est = np.eye(5) * 5
# prev_time_gps = func.time_parser(data['time'])
prev_time_gps = int(data['time'])
prev_time = int(data['time'])
theta = 0

x_geo = []
y_geo = []
x_coord = []
y_coord = []
lat_fused = []
long_fused = []
bearing_arr = []

with open(file_name, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):
        if i >= 0 + 1 - 1 and i <= 11000: # 11000

            data = {
                'time': row[0],
                'lat': float(row[1]),
                'lon': float(row[2]),
                'Ax': float(row[3]),
                'Ay': float(row[4]),
                'Gz': float(row[5]),
                'bearing': float(row[6])
            }

            ax, omega = data['Ax'], data['Gz']
            # ax = 0 - np.abs(ax)
            # current_time = func.time_parser(data['time'])
            current_time = int(data['time'])
            # deltaT = 0.1
            deltaT = (current_time - prev_time) / (10 ** 6)
            delta = np.abs(deltaT)
            print(deltaT)
            # F = get_F(deltaT)
            X_pred, P_pred = func.kalman_predict(X_est, P_pred, Qk, ax, np.deg2rad(omega), deltaT)
            prev_time = current_time
            # deltaT_gps = func.time_parser(data['time']) - prev_time_gps
            deltaT_gps = current_time - prev_time_gps
            deltaT_gps = deltaT_gps / (10 ** 6)
            if deltaT_gps >= 1/2:
                # deltaT_gps = 1
                # lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
                lat, lon = data['lat'], data['lon']
                x, y = func.gps_to_x_y(lat0, lon0, lat, lon)
                # v = np.sqrt((x - x_p) ** 2 + (y - y_p) ** 2) / deltaT_gps

                theta = rad_angle_to_oy(x_p, y_p, x, y)
                print(np.rad2deg(theta))
                Z = np.array([[x], [y], [(x - x_p)/deltaT_gps], [(y - y_p)/deltaT_gps], [theta]])
                X_pred, P_pred = func.kalman_update(X_pred, P_pred, H, Rk, Z)
                # prev_time_gps = func.time_parser(data['time'])
                prev_time_gps = current_time
                x_p = x
                y_p = y
                x_geo.append(x)
                y_geo.append(y)

            X_est = X_pred
            P_est = P_pred

            x_coord.append(X_est[0][0])
            y_coord.append(X_est[1][0])
            bearing_arr.append(X_est[4][0])

# with open('../../RemoteController/rtk_xy.txt', 'w') as file:
#     xbuf = 9999
#     ybuf = 9999
#     for x_val, y_val in zip(lat_fused, long_fused):
#         # print(f"{x_val} {y_val}")
#         if xbuf != x_val or ybuf != y_val:
#             file.write(f"{x_val} {y_val}\n")
#             xbuf = x_val
#             ybuf = y_val

plt.plot(x_coord, y_coord, color='blue', label='Fused xy')
plt.plot(x_geo, y_geo, color='red', label='GPS xy')

x_rtk = []
y_rtk = []
count = 0
with open('rtk_xy.txt', 'r') as file:
    for line in file:
        # if count >= 300:
        #     break
        fields = line.strip().split(' ')
        x_rtk.append(float(fields[0]))
        y_rtk.append(float(fields[1]))
        count = count + 1

plt.plot(x_rtk, y_rtk, color='green', label='RTK-GPS(pseudo-groundtruth)')
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





