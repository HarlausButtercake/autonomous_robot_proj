import numpy as np

def deg_to_rad(deg):
    return deg / 180 * np.pi

def rad_to_deg(rad):
    return rad * 180 / np.pi

def Gps_to_x_y(lat0, lng0, lat, lng):
    lat0, lng0, lat, lng = map(deg_to_rad, [lat0, lng0, lat, lng])
    dLat = lat - lat0
    dLng = lng - lng0

    rns = 6343618.3790280195  # Radius for north-south
    rew = 6380879.425381593   # Radius for east-west

    x = rns * np.sin(dLat)
    y = rew * np.sin(dLng)* np.cos(lat0)

    return x, y

def x_y_to_gps(x, y, lat0, lng0):
    lat0, lng0 = map(deg_to_rad, [lat0, lng0])
    rns = 6343618.3790280195
    rew = 6380879.425381593

    lat = np.arcsin(x / rns )+ lat0
    lng = np.arcsin(y / (rew * np.cos(lat0))) + lng0

    lat, lng = map(rad_to_deg, [lat, lng])

    return round(lat, 6), round(lng, 6)

def calculate_space(x1, y1, x2, y2):
    dis = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    waypoint_number = max(int(dis), 1)
    deltax = (x2 - x1) / waypoint_number
    deltay = (y2 - y1) / waypoint_number
    return deltax, deltay, waypoint_number

def get_way_points(points):
    if not points:
        return []

    lat0, lng0 = points[0]
    gps_lst = [(lat0, lng0)]

    for i in range(len(points) - 1):
        current_lat, current_lng = points[i]
        next_lat, next_lng = points[i + 1]

        x, y = Gps_to_x_y(lat0, lng0, current_lat, current_lng)
        next_x, next_y = Gps_to_x_y(lat0, lng0, next_lat, next_lng)

        deltax, deltay, n = calculate_space(x, y, next_x, next_y)

        current_x, current_y = x, y

        for _ in range(n):
            current_x += deltax
            current_y += deltay
            gps_lst.append(x_y_to_gps(current_x, current_y, lat0, lng0))

    gps_lst.append((points[-1][0], points[-1][1]))  # Adding the last point
    return gps_lst

if __name__ == "__main__":
    lct_lst = [
        (21.037599817956412, 105.76885153253623),
        (21.037657396753815, 105.76886896689449),
        (21.037604824809257, 105.76902654667104),
        (21.037549570503668, 105.76900756454087),
        (21.037599817956412, 105.76885153253623)
    ]
    
    # Get waypoints
    gps_lst = get_way_points(lct_lst)
    print(gps_lst)
