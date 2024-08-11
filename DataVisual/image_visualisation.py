import csv
import matplotlib.pyplot as plt
import numpy as np

import func
from PIL import Image, ImageDraw


# def gps_to_x_y(lat0, lng0, lat, lng):
#     dLat = lat - lat0
#     dLng = lng - lng0
#
#     rns = 6343618.3790280195
#     rew = 6380879.425381593
#
#     y = rns * np.sin(dLat)
#     x = rew * np.sin(dLng) * np.cos(lat0)
#
#     return x, y


def gps_to_x_y(lat0, lng0, lat, lng):
    dLat = lat - lat0
    dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    y = rns * np.sin(dLat)
    x = rew * np.sin(dLng) * np.cos(lat0)

    return x, y

# def find_pixel(lat_target, lon_target):
#     # Interpolate the pixel coordinates
#     px_target = x0 + (lon_target - lon0) * (x_shadow - x0) / (lon_shadow - lon0)
#     py_target = y0 + (lat_target - lat0) * (y_shadow - y0) / (lat_shadow - lat0)
#
#     return px_target, py_target


if __name__ == "__main__":
    image_path = 'ULIS_C2_demo.png'

    data = {'time': "00:00:00", 'lat': 0, 'lon': 0, 'Ax': 0, 'Ay': 0, 'Gz': 0, 'bearing': 0}
    # width = 700 * 10 / 81
    # length = width

    # x0, y0 = 158, 408  # Example coordinates
    lat0, lon0 = 21.0396111666666, 105.782851
    lat0 = np.deg2rad(lat0)
    lon0 = np.deg2rad(lon0)
    # x_shadow, y_shadow = 368, 379
    # lat_shadow, lon_shadow = 21.0395510374481, 105.78299157040242

    x_geo, y_geo = [], []
    x_coords, y_coords = [], []
    with open('Log_ULIS_C2.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i >= 1043 - 1:
                data = {
                    'time': row[0],
                    'lat': float(row[1]),
                    'lon': float(row[2]),
                    'Ax': float(row[3]),
                    'Ay': float(row[4]),
                    'Gz': float(row[5]),
                    'bearing': float(row[6])
                }
                lat, lon = data['lat'], data['lon']
                x_geo.append(lat)
                y_geo.append(lon)
                lat = np.deg2rad(lat)
                lon = np.deg2rad(lon)
                # print(f"{lat} {lon}")
                x, y = gps_to_x_y(lat0, lon0, lat, lon)
                x_coords.append(x)
                y_coords.append(y)
                print(f"{x} {y}")

    with open('../RemoteController/set.txt', 'w') as file:
        xbuf = 9999
        ybuf = 9999
        for x_val, y_val in zip(x_geo, y_geo):
            # print(f"{x_val} {y_val}")
            if xbuf != x_val or ybuf != y_val:
                file.write(f"{x_val} {y_val}\n")
                xbuf = x_val
                ybuf = y_val

    # radius = 2
    # color = (255, 0, 0)
    # with Image.open(image_path) as img:
    #     img = img.convert("RGBA")
    #     draw = ImageDraw.Draw(img)
    #     for x, y in zip(x_coords, y_coords):
    #         if x >= 0 and y >= 0:
    #             left_up_point = (x - radius, y - radius)
    #             right_down_point = (x + radius, y + radius)
    #             draw.ellipse([left_up_point, right_down_point], fill=color)
    # img.save('marked_image.png')

    plt.scatter(x_coords, y_coords, color='blue', label='Points', s=2)

    # Optionally, add labels and a title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Scatter Plot of Points')
    # plt.gca().invert_yaxis()

    plt.legend()

    plt.show()