import csv
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image, ImageDraw


# def find_pixel(lat_target, lon_target):
#     px_target = x0 + (lon_target - lon0) * (x_shadow - x0) / (lon_shadow - lon0)
#     py_target = y0 + (lat_target - lat0) * (y_shadow - y0) / (lat_shadow - lat0)
#
#     return px_target, py_target


def gps_to_x_y(lat0, lng0, lat, lng):
    dLat = lat - lat0
    dLng = lng - lng0

    rns = 6343618.3790280195
    rew = 6380879.425381593

    y = rns * np.sin(dLat)
    x = rew * np.sin(dLng) * np.cos(lat0)

    return x, y




# Example usage:


# pixel_x, pixel_y = coordinates_to_pixels(coord_x, coord_y, min_x, min_y, max_x, max_y, image_width, image_height)

if __name__ == "__main__":
    image_path = 'LDT_Alt.png'

    # lat0, lon0 = 21.0385716666666, 105.782557666666
    lat0 = 500
    lon0 = 500

    begin = 1
    end = 200000

    x_rtk, y_rtk = [], []
    x_gps, y_gps = [], []
    x_geo, y_geo = [], []
    bearing_arr = []
    bearing = 0
    with open('gps_rtk.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if begin - 1 <= i <= 2000 - 1:
                # if row[1] == "N/A" or row[1] == 0:
                #     continue
                data = {
                    'time': row[0],


                    'lat': float(row[3]),
                    'lon': float(row[4])
                }

                lat, lon = data['lat'], data['lon']
                x_geo.append(lat)
                y_geo.append(lon)
                if lat0 == 500:
                    lat0 = lat
                    lon0 = lon
                    # lat0 = np.deg2rad(lat0)
                    # lon0 = np.deg2rad(lon0)
                # lat = np.deg2rad(lat)
                # lon = np.deg2rad(lon)
                x, y = gps_to_x_y(lat0, lon0, lat, lon)
                x_rtk.append(x)
                y_rtk.append(y)

    # with open('gps_1hz.csv', newline='') as csvfile:
    #     csvreader = csv.reader(csvfile)
    #     for i, row in enumerate(csvreader):
    #         if begin - 1 <= i <= (end * 3) - 500:
    #             # if row[1] == "N/A" or row[1] == 0:
    #             #     continue
    #             data = {
    #                 'time': row[0],
    #
    #
    #                 'lat': float(row[1]),
    #                 'lon': float(row[2])
    #             }
    #             lat, lon = data['lat'], data['lon']
    #             # lat = np.deg2rad(lat)
    #             # lon = np.deg2rad(lon)
    #             x, y = gps_to_x_y(lat0, lon0, lat, lon)
    #             x_gps.append(x)
    #             y_gps.append(y)

    plt.plot(x_rtk, y_rtk, color='red', label='GPS RTK')
    # plt.plot(x_gps, y_gps, color='blue', label='GPS')
    # bearing_rad = np.deg2rad(bearing_arr)
    # plt.quiver(x_coords, y_coords, np.sin(bearing_rad), np.cos(bearing_rad), angles='xy', scale_units='xy', scale=0.5,
    #            color='red')

    # Optionally, add labels and a title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    # plt.xlim(-20, 0)
    # plt.ylim(-17, -7)
    plt.title('Scatter Plot of Points')
    # plt.gca().invert_yaxis()

    plt.legend()

    plt.show()

    with open('../../RemoteController/set.txt', 'w') as file:
        xbuf = 9999
        ybuf = 9999
        for x_val, y_val in zip(x_rtk, y_rtk):
            # print(f"{x_val} {y_val}")
            if xbuf != x_val or ybuf != y_val:
                file.write(f"{x_val} {y_val}\n")
                # xbuf = x_val
                # ybuf = y_val