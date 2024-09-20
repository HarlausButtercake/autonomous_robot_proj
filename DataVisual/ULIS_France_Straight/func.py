import csv

import numpy as np

from PIL import Image, ImageDraw


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
    l_theta = wraptopi(X0[4][0])
    l_theta = t * l_omega + X0[4][0]
    l_theta = wraptopi(l_theta)
    # l_theta = np.deg2rad(X0[4][0])
    B1 = np.array([[m * l_a * np.sin(l_theta)],
                   [m * l_a * np.cos(l_theta)],
                   [t * l_a * np.sin(l_theta)],
                   [t * l_a * np.cos(l_theta)],
                   [0]])
    B2 = np.array([[0], [0], [0], [0], [t * l_omega]])

    Xp = l_F.dot(X0) + B1 + B2
    Xp[4][0] %= np.deg2rad(360)
    Pp = (l_F.dot(P0)).dot(l_F.T) + l_Qk
    return Xp, Pp


def kalman_update(l_xp, l_p, l_hk, rk_loc, zk_loc):
    K = (l_p.dot(l_hk.T)).dot(np.linalg.inv((l_hk.dot(l_p)).dot(l_hk.T) + rk_loc))
    r_x = l_xp + K.dot((zk_loc - l_hk.dot(l_xp)))
    r_p = l_p - K.dot((l_hk.dot(l_p)))
    return r_x, r_p


def y_portion(theta):
    theta = wraptopi(theta)

def rad_angle_to_oy(x0, y0, r_x, r_y):
    dx = r_x - x0
    dy = r_y - y0
    dot = dx * 0 + dy * 1
    a = np.sqrt(dx**2 + dy**2)
    b = 1
    if a == 0:
        return 0

    res = np.acos(dot / a)
    if dx < 0:
        return 2 * np.pi - res
    else:
        return res

    if r_y > 0:
        return np.acos(dot / a)
    else:
        return 2 * np.pi - np.acos(dot / a)


def wraptopi(x):
    """
    Wrap theta measurements to [-pi, pi].
    Accepts an angle measurement in radians and returns an angle measurement in radians
    """
    if x > np.pi:
        x = x - (np.floor(x / (2 * np.pi)) + 1) * 2 * np.pi
    elif x < -np.pi:
        x = x + (np.floor(x / (-2 * np.pi)) + 1) * 2 * np.pi
    return x


def mark_pixel_with_circle(img, x, y, radius=5, color=(255, 0, 0)):
    # with Image.open(image_path) as img:
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    left_up_point = (x - radius, y - radius)
    right_down_point = (x + radius, y + radius)
    draw.ellipse([left_up_point, right_down_point], fill=color)


def time_parser(time):
    hh, mm, ss = map(int, time.strip().split(':'))
    return hh*3600 + mm*60 + ss


def coord_to_rad(coord):
    return coord / 180 * np.pi


def to_data(file_name, num):
    with open(file_name, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i == num - 1:  # 102 because indexing starts at 0
                data = {
                    'time': row[0],
                    'lat': float(row[1]),
                    'lon': float(row[2]),
                    'Ax': float(row[3]),
                    'Ay': float(row[4]),
                    'Gz': float(row[5]),
                    'bearing': float(row[6])
                }
                return data

def gps_to_x_y(lat_ori, lng0, lat_tar, lng):
    re = 6378135
    rp = 6356750

    t = re * np.cos(lat_ori) * re * np.cos(lat_ori) + rp * np.sin(lat_ori) * rp * np.sin(lat_ori)
    rns = (re * rp * re * rp) / (t * np.sqrt(t))
    rew = re * re / (np.sqrt(t))

    dLat = lat_tar - lat_ori
    dLng = lng - lng0

    # rns = 6343618.3790280195
    # rew = 6380879.425381593

    r_y = rns * np.sin(dLat)
    r_x = rew * np.sin(dLng) * np.cos(lat_ori)

    return r_x, r_y