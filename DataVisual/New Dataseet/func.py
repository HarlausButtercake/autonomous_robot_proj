import csv

import numpy as np

from PIL import Image, ImageDraw





def time_parser(time):
    hh, mm, ss = map(int, time.strip().split(':'))
    return hh*3600 + mm*60 + ss


# def to_data(file_name, num):
#     with open(file_name, newline='') as csvfile:
#         csvreader = csv.reader(csvfile)
#         for i, row in enumerate(csvreader):
#             if i == num - 1:  # 102 because indexing starts at 0
#                 data = {
#                     'time': row[0],
#                     'lat': float(row[1]),
#                     'lon': float(row[2]),
#                     'Ax': float(row[3]),
#                     'Ay': float(row[4]),
#                     'Gz': float(row[5]),
#                     'bearing': float(row[6])
#                 }
#                 return data


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


def get_F(delta):
    F = np.array([[1, 0, delta, 0, 0],
                  [0, 1, 0, delta, 0],
                  [0, 0, 1, 0, 0],
                  [0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1]])
    return F


def kalman_predict(X0, P0, l_Qk, l_a, l_omega, t):
    l_F = get_F(t)
    m = (t ** 2) / 2

    l_theta = X0[4][0]
    # l_theta = np.deg2rad(X0[4][0])
    B1 = np.array([[m * l_a * np.sin(l_theta)],
                   [m * l_a * np.cos(l_theta)],
                   [t * l_a * np.sin(l_theta)],
                   [t * l_a * np.cos(l_theta)],
                   [0]])
    B2 = np.array([[0], [0], [0], [0], [t * l_omega]])
    Xp = l_F.dot(X0) + B1 + B2
    # Xp[4][0] = np.rad2deg(Xp[4][0])
    Pp = (l_F.dot(P0)).dot(l_F.T) + l_Qk
    return Xp, Pp


def kalman_update(l_xp, l_p, l_hk, rk_loc, zk_loc):
    K = (l_p.dot(l_hk.T)).dot(np.linalg.inv((l_hk.dot(l_p)).dot(l_hk.T) + rk_loc))
    r_x = l_xp + K.dot((zk_loc - l_hk.dot(l_xp)))
    r_p = l_p - K.dot((l_hk.dot(l_p)))
    return r_x, r_p