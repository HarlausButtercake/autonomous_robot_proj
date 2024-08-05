import csv
import numpy as np
import time

from matplotlib import pyplot as plt

import func


def get_F(deltaT, wk):
    F = np.array([[1, 0, deltaT * np.cos(wk), 0],
                  [0, 1, deltaT * np.sin(wk), 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
    return F


def kalman_predict(X0, P0, Qk, Fk, ax, ay, w, deltaT):
    m = deltaT ** 2  # / 2
    pos = X[3][0]
    B1 = np.array([[m * ax],
                   [m * ay],
                   [deltaT * np.sqrt(ax**2 + ay**2)],
                   [0]])
    B2 = np.array([[0], [0], [0], [w]])
    Xp = Fk.dot(X0) + B1 + B2

    Pp = (Fk.dot(P0)).dot(Fk.T) + Qk
    return Xp, Pp


def kalman_update(Xp, Pp, Hk, Rk, Zk):
    K = (Pp.dot(Hk.T)).dot(np.linalg.inv((Hk.dot(Pp)).dot(Hk.T) + Rk))
    X = Xp + K.dot((Zk - Hk.dot(Xp)))
    P = Pp - K.dot((Hk.dot(Pp)))
    return X, P


def gps_to_x_y(lat0, lng0, lat, lng):
    dLat = lat - lat0
    dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    y = rns * np.sin(dLat)
    x = rew * np.sin(dLng) * np.cos(lat0)

    return x, y


def distance_cal(x, y, x_d, y_d):
    return np.sqrt((x - x_d) ** 2 + (y - y_d) ** 2)


prev_lat = None
prev_lon = None
prev_time = None

# Noise covariance form environment
Qk = np.eye(4) * 0.001  # Qk
P = np.eye(4) * 0.2  # Noise from measurement
Rk = np.eye(4) * 0.05  # Rk # Assume that error ~ 0.05
H = np.eye(4)  # transition matrix H

x_p = 0
y_p = 0
begin = 1100
data = func.to_data(begin)
lat0, lon0 = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])


data = func.to_data(begin + 30)
lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])

x, y = gps_to_x_y(lat0, lon0, lat, lon)
theta = data['bearing']
x_p = x
y_p = y
X = np.zeros((4, 1))
# when start X-axis of robot is 90 degree vs X-axis of the Oxy we define

# velocity
v = np.sqrt(x ** 2 + y ** 2) / 3
print(v)

Z = np.array([[x], [y], [v], [theta]])
X, P = kalman_update(X, P, H, Rk, Z)

prev_time_gps = func.time_parser(data['time'])

x_coord = []
y_coord = []
with open('Log_ULIS_c2.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):
        if i >= begin + 31 - 1:  # 102 because indexing starts at 0
            data = {
                'time': row[0],
                'lat': float(row[1]),
                'lon': float(row[2]),
                'Ax': float(row[3]),
                'Ay': float(row[4]),
                'Gz': float(row[5]),
                'bearing': float(row[6])
            }
            deltaT_gps = func.time_parser(data['time']) - prev_time_gps
            if deltaT_gps >= 1:
                # lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
                lat, lon = func.coord_to_rad(data['lat']), func.coord_to_rad(data['lon'])
                x, y = gps_to_x_y(lat0, lon0, lat, lon)
                v = np.sqrt((x - x_p) ** 2 + (y - y_p) ** 2) / deltaT_gps
                theta = np.arctan2((y - y_p), (x - x_p))
                Z = np.array([[x], [y], [v], [theta]])
                X, P = kalman_update(X, P, H, Rk, Z)
                prev_time_gps = func.time_parser(data['time'])
                x_p = x
                y_p = y
                # x_coord.append(x)
                # y_coord.append(y)

            ax, ay, w = data['Ax'], data['Ay'], data['bearing']
            current_time = func.time_parser(data['time'])
            deltaT = current_time - prev_time if prev_time else 0
            prev_time = current_time
            deltaT = 0.1
            F = get_F(deltaT, w)
            X, P = kalman_predict(X, P, Qk, F, ax, ay, w, deltaT)
            # print(X[0][0], X[1][0])
            x_coord.append(X[0][0])
            y_coord.append(X[1][0])

plt.plot(x_coord, y_coord, color='blue', label='Points')

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Scatter Plot of Points')
# plt.gca().invert_yaxis()

plt.legend()

plt.show()





