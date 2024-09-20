import csv
import numpy as np
import time

from matplotlib import pyplot as plt

import func


# def get_F(delta):
#     F = np.array([[1, 0, delta, 0, 0],
#                   [0, 1, 0, delta, 0],
#                   [0, 0, 1, 0, 0],
#                   [0, 0, 0, 1, 0],
#                   [0, 0, 0, 0, 1]])
#     return F


# def kalman_predict(X0, P0, l_Qk, l_a, l_omega, t):
#     l_F = get_F(t)
#     m = (t ** 2) / 2
#     # l_theta = np.deg2rad(X0[4][0])
#     l_theta = X0[4][0]
#     B1 = np.array([[m * l_a * np.sin(l_theta)],
#                    [m * l_a * np.cos(l_theta)],
#                    [t * l_a * np.sin(l_theta)],
#                    [t * l_a * np.cos(l_theta)],
#                    [0]])
#     B2 = np.array([[0], [0], [0], [0], [t * l_omega]])
#     Xp = l_F.dot(X0) + B1 + B2
#     # Xp[4][0] = np.rad2deg(Xp[4][0])
#     Pp = (l_F.dot(P0)).dot(l_F.T) + l_Qk
#     return Xp, Pp

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


def kalman_update(l_xp, l_p, l_hk, rk_loc, zk_loc):
    K = (l_p.dot(l_hk.T)).dot(np.linalg.inv((l_hk.dot(l_p)).dot(l_hk.T) + rk_loc))
    r_x = l_xp + K.dot((zk_loc - l_hk.dot(l_xp)))
    r_p = l_p - K.dot((l_hk.dot(l_p)))
    return r_x, r_p


# def kalman_update(l_x, l_y, l_Xp, l_Pp):
#     l_H = np.eye(7)
#     l_zh = np.array([l_Xp[0][0], l_Xp[1][0]])
#     l_z = np.array([l_x, l_y])
#
#     l_K = (l_H.dot(l_Pp)).dot(np.linalg.inv((l_H.dot(l_Pp)).dot(l_H.T) + (np.eye(2) * 100)))
#     r_x = l_Xp + l_K.dot((l_z - l_zh))
#     r_p = (np.eye(6) - l_K.dot(l_H)).dot(l_Pp)
#     return r_x, r_p




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


# def rad_angle_to_oy(x0, y0, x, y):
#     dx = x - x0
#     dy = y - y0
#     dot = dx * 0 + dy * 1
#     a = np.sqrt(dx**2 + dy**2)
#     b = 1
#     if a == 0:
#         return 0
#     return np.acos(dot / a)

########################################################################################

H = np.eye(5)  # transition matrix H, observation model

Qk = np.eye(5) * 0.001 #Qk
P_pred = np.eye(5) * 5
#Noise from measurement
#Assume that error ~ 0.05
#Rk = np.eye(4)*0.05 #Rk
Rk = np.array([[3, 0, 0, 0, 0],
               [0, 3, 0, 0, 0],
               [0, 0, 0.1, 0, 0],
               [0, 0, 0, 0.1, 0],
               [0, 0, 0, 0, np.pi /18]])
########################################################################################
file_name = 'Log_ULIS_France_Straight.csv'
begin = 570

data = func.to_data(file_name, begin)
lat0, lon0 = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])

x_p = 0
y_p = 0

# X_est = np.zeros((5, 1))
X_est = np.array([[0], [0], [0], [0], [np.deg2rad(10)]])
P_est = np.eye(5) * 5
prev_time_gps = func.time_parser(data['time'])
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
        if i >= begin + 1 - 1:
            data = {
                'time': row[0],
                'lat': float(row[1]),
                'lon': float(row[2]),
                'Ax': float(row[3]),
                'Ay': float(row[4]),
                'Ax_lin': float(row[5]),
                'Ay_lin': float(row[6]),
                'Gz': float(row[7]),
                'bearing': float(row[8]) # bwoken :(
            }

            ax, omega = data['Ay'], data['Gz']
            current_time = func.time_parser(data['time'])
            deltaT = 0.1
            # F = get_F(deltaT)
            X_pred, P_pred = func.kalman_predict(X_est, P_pred, Qk, ax, np.deg2rad(omega + 0.23), deltaT)

            deltaT_gps = func.time_parser(data['time']) - prev_time_gps
            if deltaT_gps >= 1:
                lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
                x, y = func.gps_to_x_y(lat0, lon0, lat, lon)
                # v = np.sqrt((x - x_p) ** 2 + (y - y_p) ** 2) / deltaT_gps

                theta = func.rad_angle_to_oy(x_p, y_p, x, y)
                Z = np.array([[x], [y], [(x - x_p) / deltaT_gps], [(y - y_p) / deltaT_gps], [theta]])
                # X_pred, P_pred = kalman_update(X_pred, P_pred, H, Rk, Z)

                prev_time_gps = func.time_parser(data['time'])
                x_p = x
                y_p = y
                x_geo.append(x)
                y_geo.append(y)

            X_est = X_pred
            P_est = P_pred

            x_coord.append(X_est[0][0])
            y_coord.append(X_est[1][0])

plt.plot(x_coord, y_coord, color='blue', label='Fused xy')
plt.plot(x_geo, y_geo, color='red', label='GPS xy')

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Scatter Plot of Points')
plt.xlim(-30, 30)

plt.legend()

plt.show()





