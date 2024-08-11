import csv
import numpy as np
import time

import read_imu
import read_gps
import read_ground_truth

from matplotlib import pyplot as plt

import func


# def get_F(delta):
#     F = np.array([[1, 0, delta, 0],
#                   [0, 1, 0, delta],
#                   [0, 0, 1, 0],
#                   [0, 0, 0, 1]])
#     return F


# def kalman_predict(X0, P0, l_Qk, Fk, l_ax, l_ay, t):
#     m = t ** 2 / 2
#     B1 = np.array([[m * l_ax],
#                    [m * l_ay],
#                    [t * l_ax],
#                    [t * l_ay]])
#     B2 = np.array([[0], [0], [0], [0]])
#     Xp = Fk.dot(X0) + B1 + B2
#
#     Pp = (Fk.dot(P0)).dot(Fk.T) + l_Qk
#     return Xp, Pp

def get_F(delta):
    F = np.array([[1, 0, delta, 0, (delta ** 2) / 2, 0, 0],    # x
                  [0, 1, 0, delta, 0, (delta ** 2) / 2, 0],    # y
                  [0, 0, 1, 0, delta, 0, 0],                        # vx
                  [0, 0, 0, 1, 0, delta, 0],                       # vx
                  [0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 1]])                       # theta
    return F


def kalman_predict(X0, P0, l_Qk, Fk, l_ax, l_ay, w, t):
    m = t ** 2 / 2
    B1 = np.array([[0],
                   [0],
                   [0],
                   [0],
                   [l_ax],
                   [l_ay],
                   [t * w]])
    # B2 = np.array([[0], [0], [0], [0]])
    Xp = Fk.dot(X0) + B1

    Pp = (Fk.dot(P0)).dot(Fk.T) + l_Qk
    return Xp, Pp


def kalman_update(l_xp, l_p, l_hk, rk_loc, zk_loc):
    K = (l_p.dot(l_hk.T)).dot(np.linalg.inv((l_hk.dot(l_p)).dot(l_hk.T) + rk_loc))
    r_x = l_xp + K.dot((zk_loc - l_hk.dot(l_xp)))
    r_p = l_p - K.dot((l_hk.dot(l_p)))
    return r_x, r_p


def gps_to_x_y(lat_ori, lng0, lat_tar, lng):
    dLat = lat_tar - lat_ori
    dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    y = rns * np.sin(dLat)
    x = rew * np.sin(dLng) * np.cos(lat_ori)

    return x, y


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


def distance_cal(x, y, x_d, y_d):
    return np.sqrt((x - x_d) ** 2 + (y - y_d) ** 2)


def find_nearest_index(array: np.ndarray, time):  # array of timesteps, time to search for
    """Find closest time in array, that has already passed"""
    diff_arr = array - time
    idx = np.where(diff_arr <= 0, diff_arr, -np.inf).argmax()
    return idx


prev_lat = None
prev_lon = None
prev_time = None

########################################################################################

H = np.eye(7)  # transition matrix H, observation model
Qk = np.eye(7) * 0.001 #Qk
Rk = np.array([[50, 0, 0, 0, 0, 0, 0],    # x
                  [0, 50, 0, 0, 0, 0, 0],    # y
                  [0, 0, 10, 0, 0, 0, 0],                        # vx
                  [0, 0, 0, 10, 0, 0, 0],                       # vx
                  [0, 0, 0, 0, 10, 0, 0],
                  [0, 0, 0, 0, 0, 10, 0],
                  [0, 0, 0, 0, 0, 0, 0.2]])

########################################################################################
# file_name = '../Log_ULIS_France_Straight.csv'
TRUNCATION_END = -1
FILE_DATE = "dataset/2012-11-16"
imu_data = read_imu.read_imu(FILE_DATE)
gps_data = read_gps.read_gps(FILE_DATE, False)

euler_data = read_imu.read_euler(FILE_DATE)
euler_data = euler_data[:-1, :]

ground_truth = read_ground_truth.read_ground_truth(FILE_DATE, truncation=TRUNCATION_END)
ground_truth = ground_truth[:TRUNCATION_END, :]
gps_data = gps_data[:TRUNCATION_END, :]
imu_data = imu_data[:TRUNCATION_END, :]
euler_data = euler_data[:TRUNCATION_END, :]
# Using the original Unix Timestamp for timesyncing

x_true = ground_truth[:, 1]  # North
y_true = ground_truth[:, 2]  # East
theta_true = ground_truth[:, 3]  # Heading
true_times = ground_truth[:, 0]

x_p = 0
y_p = 0

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

X_est = np.zeros((7, 1))
P_est = np.eye(7) * 5

dt = 1 / 10
t = np.arange(ground_truth[0, 0], ground_truth[-1, 0], dt)
N = len(t)
# with open(file_name, newline='') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for i, row in enumerate(csvreader):
#         if i >= begin + 1 - 1:
for k in range(1, len(t)):
    # data = {
    #     'time': row[0],
    #     'lat': float(row[1]),
    #     'lon': float(row[2]),
    #     'Ax': float(row[3]),
    #     'Ay': float(row[4]),
    #     'Ax_lin': float(row[5]),
    #     'Ay_lin': float(row[6]),
    #     'Gz': float(row[7]),
    #     'bearing': float(row[8])
    # }
    ax, ay, w = a_x[imu_counter], a_y[imu_counter], omega[imu_counter]
    F = get_F(dt)
    X_pred, P_pred = kalman_predict(X_est, P_est, Qk, F, ax, ay, w + 0.23, deltaT)

    deltaT_gps = func.time_parser(data['time']) - prev_time_gps
    if deltaT_gps >= 1:
        lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
        x, y = gps_to_x_y(lat0, lon0, lat, lon)
        # v = np.sqrt((x - x_p) ** 2 + (y - y_p) ** 2) / deltaT_gps
        theta = np.arctan2((y - y_p), (x - x_p))
        Z = np.array([[x], [y], [x - x_p], [y - y_p], [ax], [ay], [theta]])
        X_pred, P_pred = kalman_update(X_pred, P_pred, H, Rk, Z)
        prev_time_gps = func.time_parser(data['time'])
        x_p = x
        y_p = y
        # x_geo.append(x)
        # y_geo.append(y)

    X_est = X_pred
    P_est = P_pred
#
#             x_coord.append(X_est[0][0])
#             y_coord.append(X_est[1][0])
#             blat, blong = xy_to_gps(lat0, lon0, X_pred[0][0], X_pred[1][0])
#             lat_fused.append(np.rad2deg(blat))
#             long_fused.append(np.rad2deg(blong))
#             # bearing_arr.append(w)



dt = 1 / 10  # 1/Hz = seconds
t = np.arange(ground_truth[0, 0], ground_truth[-1, 0], dt)
N = len(t)
# x_est = np.zeros([N, 6])
# P_est = np.zeros([N, 6, 6])  # state covariance matrices

# x_est = x | y | xdot | ydot | theta | omega
# x_est[0] = np.array([x_true[0], y_true[0], 0, 0, theta_true[0], 0])  # initial state
# P_est[0] = np.diag([1, 1, 1, 1, 1, 1])  # initial state covariance TO-DO: TUNE THIS TO TRAIN
#
# x_true_arr = np.zeros([N])  # Keep track of corresponding truths
# y_true_arr = np.zeros([N])
# theta_true_arr = np.zeros([N])
# x_true_arr[0] = x_true[0]  # initial state
# y_true_arr[0] = y_true[0]
# theta_true_arr[0] = theta_true[0]
#
# ################################ 1. MAIN FILTER LOOP ##########################################################################
#
# a_x = imu_data[:, 1]
# a_y = imu_data[:, 2]
# omega = imu_data[:, 3]
# theta_imu = euler_data[:, 1]
#
# gps_x = gps_data[:, 1]
# gps_y = gps_data[:, 2]
#
# gps_times = gps_data[:, 0]
# imu_times = imu_data[:, 0]
# euler_times = euler_data[:, 0]
# gps_counter = 0
# wheel_counter = 0
# imu_counter = 0
# fog_counter = 0
# euler_counter = 0
# ground_truth_counter = 0
#
# prev_gps_counter = -1
# prev_wheel_counter = -1
# prev_imu_counter = -1
# prev_fog_counter = -1
# prev_euler_counter = -1
# x_coord = []
# y_coord = []
# # Start at 1 because we have initial prediction from ground truth.
# for k in range(1, len(t)):
#     print(k, "/", len(t))
#
#     # PREDICTION - UPDATE OF THE ROBOT STATE USING MOTION MODEL AND INPUTS (IMU)
#     F = get_F(dt)
#     X_pred, P_pred = kalman_predict(X_est, P_est, Qk, F, a_x[imu_counter], a_y[imu_counter], theta_imu[euler_counter], dt)
#
#     imu_counter = find_nearest_index(imu_times, t[k])
#     euler_counter = find_nearest_index(euler_times, t[k])  # Grab closest Theta correction data
#     gps_counter = find_nearest_index(gps_times, t[k])  # Grab closest GPS data
#     ground_truth_counter = find_nearest_index(true_times, t[k])  # Grab closest Ground Truth data
#
#     if gps_counter != prev_gps_counter:  # Use GPS data only if new
#         Z = np.array([[x], [y], [x - x_p], [y - y_p], [ax], [ay], [theta]])
#         X_pred, P_pred = kalman_update(X_pred, P_pred, H, Rk, Z)
#         prev_gps_counter = gps_counter
#
#     X_est = X_pred
#     P_est = P_pred
#     x_coord.append(X_est[0][0])
#     y_coord.append(X_est[1][0])
#     # x_true_arr[k] = x_true[ground_truth_counter]
#     # y_true_arr[k] = y_true[ground_truth_counter]
#     # theta_true_arr[k] = theta_true[ground_truth_counter]







# plt.plot(x_coord, y_coord, color='blue', label='Fused xy')
# plt.plot(x_geo, y_geo, color='red', label='GPS xy')

# bearing_rad = np.deg2rad(bearing_arr)
# plt.quiver(x_coord, y_coord, np.sin(bearing_rad), np.cos(bearing_rad), angles='xy', scale_units='xy', scale=0.5, color='red')

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Scatter Plot of Points')
plt.xlim(-30, 30)
# plt.gca().invert_yaxis()

plt.legend()

plt.show()





