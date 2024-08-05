import csv
import os

import mpu6050
import numpy as np
import smbus
import serial.serialutil
import numpy as np
import time
import sys
import subprocess
import threading
import gps
import time_current


# from mpu6050 import mpu6050
def read_accel(data):
    process = subprocess.Popen(['python', '-u', 'odometry.py'], stdout=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip():
            try:
                Ax, Ay, Gz, bearing = map(float, output.strip().split())
                data['Ax'] = Ax
                data['Ay'] = Ay
                data['Gz'] = Gz
                data['bearing'] = bearing
            #                 print(f"Odo Data: {Ax}, {Ay}")
            except ValueError:
                print(f"Invalid line received: {output.strip()}")

def read_gps_coordinates(data):
    process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
#         print(f"Invalid line received: {output.strip()}")
        if output == '' and process.poll() is not None:
            break
        # if output.strip() and output.strip() != "Invalid":
        if output.strip():
            try:
                lat, lon = map(float, output.strip().split())
                data['lat'] = lat
                data['lon'] = lon
            except ValueError:
#                 print(f"Invalid line received: {output.strip()}")
                data['lat'] = "N/A"
                data['lon'] = "N/A"

def main_task():
    while True:
        lat = gps_data.get('lat', None)
        lon = gps_data.get('lon', None)
        Ax = accel_data.get('Ax', None)
        Ay = accel_data.get('Ay', None)
        Gz = accel_data.get('Gz', None)
        bearing = accel_data.get('bearing', None)
        print(f"{lat} {lon} {Ax} {Ay} {Gz} {bearing}\n")
        write_data['time'] = time_current.get_HMS()
        write_data['lat'] = lat
        write_data['lon'] = lon
        write_data['Ax'] = Ax
        write_data['Ay'] = Ay
        write_data['Gz'] = Gz
        write_data['bearing'] = bearing
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['time', 'lat', 'lon', 'Ax', 'Ay', 'Gz', 'bearing'])
            writer.writerow(write_data)

        time.sleep(0.1)


if __name__ == "__main__":
    accel_data = {'Ax': 0, 'Ay': 0, 'Gz': 0, 'bearing': 0}
    gps_data = {'lat': 0, 'lon': 0}
    write_data = {'time': "00:00:00", 'lat': 0, 'lon': 0, 'Ax': 0, 'Ay': 0, 'Gz': 0, 'bearing': 0}

    file_path = 'StrideLog/Log_' + time_current.get_GMT7() + '.csv'
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['lat', 'lon', 'Ax', 'Ay', 'Gz'])
            writer.writeheader()

    accel_thread = threading.Thread(target=read_accel, args=(accel_data,))
    gps_thread = threading.Thread(target=read_gps_coordinates, args=(gps_data,))
    main_thread = threading.Thread(target=main_task)

    accel_thread.start()
    gps_thread.start()
    main_thread.start()

    accel_thread.join()
    gps_thread.join()
    main_thread.join()



