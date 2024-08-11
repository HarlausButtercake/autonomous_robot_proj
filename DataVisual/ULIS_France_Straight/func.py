import csv

import numpy as np

from PIL import Image, ImageDraw


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


def gps_to_x_y(lat0, lng0, lat, lng, x0, y0):
    dLat = lat - lat0
    dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    y = rns * np.sin(dLat)
    x = rew * np.sin(dLng) * np.cos(lat0)

    return x + x0, y + y0