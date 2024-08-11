import csv
import matplotlib.pyplot as plt
import numpy as np

import func
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

    begin = 530

    x_coords, y_coords = [], []
    x_geo, y_geo = [], []
    bearing_arr = []
    bearing = 0
    with open('Log_ULIS_France_Straight.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i >= begin - 1:
                if row[1] == "N/A" or row[1] == 0:
                    continue
                data = {
                    'time': row[0],
                    'lat': float(row[1]),
                    'lon': float(row[2]),
                    'Ax': float(row[3]),
                    'Ay': float(row[4]),
                    'Ax_lin': float(row[5]),
                    'Ay_lin': float(row[6]),
                    'Gz': float(row[7]),
                    'bearing': float(row[8])
                }

                lat, lon = data['lat'], data['lon']
                if lat0 == 500:
                    lat0 = lat
                    lon0 = lon
                    print(f"{lat0} {lon0}")
                    lat0 = np.deg2rad(lat0)
                    lon0 = np.deg2rad(lon0)
                    continue
                x_geo.append(lat)
                y_geo.append(lon)
                lat = np.deg2rad(lat)
                lon = np.deg2rad(lon)
                # print(f"{lat} {lon}")
                # x, y = find_pixel(lat, lon)
                # x, y = geo_to_pixel(lat, lon, min_lat, min_lon, max_lat, max_lon, image_width, image_height)
                x, y = gps_to_x_y(lat0, lon0, lat, lon)
                x_coords.append(x)
                y_coords.append(y)
                bearing += (data['Gz'] + 0.24)
                # bearing = np.atan2(data['Ay_lin'], data['Ax_lin'])
                # bearing = 90 - np.rad2deg(bearing)
                bearing_arr.append(bearing)
                # print(f"{x} {y}")

    with open('../RemoteController/set.txt', 'w') as file:
        xbuf = 9999
        ybuf = 9999
        for x_val, y_val in zip(x_geo, y_geo):
            # print(f"{x_val} {y_val}")
            if xbuf != x_val or ybuf != y_val:
                file.write(f"{x_val} {y_val}\n")
                xbuf = x_val
                ybuf = y_val

    print("Waypoint file received successfully.")

    # radius = 5
    # color = (255, 0, 0)
    # with Image.open(image_path) as img:
    #     img = img.convert("RGBA")
    #     draw = ImageDraw.Draw(img)
    #     for x, y in zip(x_coords, y_coords):
    #         if x >= 0 and y >= 0:
    #             left_up_point = (x - radius, y - radius)
    #             right_down_point = (x + radius, y + radius)
    #             draw.ellipse([left_up_point, right_down_point], fill=color)
    # img.save('ULIS_image.png')

    plt.plot(x_coords, y_coords, color='blue', label='Points')
    bearing_rad = np.deg2rad(bearing_arr)
    plt.quiver(x_coords, y_coords, np.sin(bearing_rad), np.cos(bearing_rad), angles='xy', scale_units='xy', scale=0.5,
               color='red')

    # Optionally, add labels and a title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.xlim(-30, 30)
    plt.title('Scatter Plot of Points')
    # plt.gca().invert_yaxis()

    plt.legend()

    plt.show()
