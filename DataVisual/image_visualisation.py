import csv
import matplotlib.pyplot as plt
import func
from PIL import Image, ImageDraw


def find_pixel(lat_target, lon_target):
    # Interpolate the pixel coordinates
    px_target = x0 + (lon_target - lon0) * (x_shadow - x0) / (lon_shadow - lon0)
    py_target = y0 + (lat_target - lat0) * (y_shadow - y0) / (lat_shadow - lat0)

    return px_target, py_target

if __name__ == "__main__":
    image_path = 'ULIS_C2_demo.png'

    data = {'time': "00:00:00", 'lat': 0, 'lon': 0, 'Ax': 0, 'Ay': 0, 'Gz': 0, 'bearing': 0}
    width = 700 * 10 / 81
    length = width

    x0, y0 = 158, 408  # Example coordinates
    lat0, lon0 = 21.0395215, 105.7827435

    x_shadow, y_shadow = 368, 379
    lat_shadow, lon_shadow = 21.0395510374481, 105.78299157040242


    x_coords, y_coords = [], []
    with open('Log_ULIS_c2.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i >= 1003 - 1:
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
                # print(f"{lat} {lon}")
                x, y = find_pixel(lat, lon)
                x_coords.append(x)
                y_coords.append(y)
                print(f"{x} {y}")

    radius = 5
    color = (255, 0, 0)
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        draw = ImageDraw.Draw(img)
        for x, y in zip(x_coords, y_coords):
            if x >= 0 and y >= 0:
                left_up_point = (x - radius, y - radius)
                right_down_point = (x + radius, y + radius)
                draw.ellipse([left_up_point, right_down_point], fill=color)
    img.save('marked_image.png')

    plt.plot(x_coords, y_coords, color='blue', label='Points')

    # Optionally, add labels and a title
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Scatter Plot of Points')
    plt.gca().invert_yaxis()

    plt.legend()

    plt.show()