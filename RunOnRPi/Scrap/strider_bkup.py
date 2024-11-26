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


# from mpu6050 import mpu6050
def read_accel(accel_data):
    process = subprocess.Popen(['python', '-u', 'odometry.py'], stdout=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip():
            try:
                Ax, Ay, Gz = map(float, output.strip().split())
                accel_data['Ax'] = Ax
                accel_data['Ay'] = Ay
                accel_data['Gz'] = Gz
            #                 print(f"Odo Data: {Ax}, {Ay}")
            except ValueError:
                print(f"Invalid line received: {output.strip()}")

def main_task(accel):
    gps_port = '/dev/ttyACM0'  # Adjust this if your serial port is different
    baudrate = 9600

    while True:
        try:
            gps_ser = serial.Serial(gps_port, baudrate, timeout=2)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)
        else:
            break

    while True:
        lat, lon = gps.read_gps(gps_ser)
        Ax = accel_data.get('Ax', None)
        Ay = accel_data.get('Ay', None)
        Gz = accel_data.get('Gz', None)
        if lat != None and lon != None:
#             print(lat, ' ', lon, ' ', Ax, ' ', Ay, '\n')
            print(f"{lat} {lon} {Ax} {Ay} {Gz}\n")

if __name__ == "__main__":
#     accel_data = {'Ax': 0, 'Ay': 0}
    accel_data = {'Ax': 0, 'Ay': 0, 'Gz': 0}

    accel_thread = threading.Thread(target=read_accel, args=(accel_data,))
    main_thread = threading.Thread(target=main_task, args=(accel_data,))

    accel_thread.start()
    main_thread.start()

    # Join threads to wait for them to complete (though they are infinite loops)
    accel_thread.join()
    main_thread.join()



