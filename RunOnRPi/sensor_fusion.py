import mpu6050
import numpy as np
import smbus
import serial.serialutil
import pynmea2
import numpy as np
import time
import sys
import subprocess
import threading

# from mpu6050 import mpu6050
def read_accel(accel_data):
    process = subprocess.Popen(['python', '-u', 'odometry.py'], stdout=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip():
            try:
                Ax, Ay = map(float, output.strip().split())
                accel_data['Ax'] = Ax
                accel_data['Ay'] = Ay
#                 print(f"Odo Data: {Ax}, {Ay}")
            except ValueError:
                print(f"Invalid line received: {output.strip()}")
        time.sleep(1)
        
def coord_to_rad(coord):
    return coord / 180 *np.pi

def read_gps(ser):
    line = ser.readline().decode('utf-8', errors='ignore')
    if line.startswith('$GPGGA'):
        msg = pynmea2.parse(line)
        # Extract latitude, longitude, and timestamp from the message
#         lat = msg.latitude / 180 * np.pi
#         lon = msg.longitude / 180 * np.pi
        lat = msg.latitude
        lon = msg.longitude
        if lat == 0.0 or lon == 0.0:
            return "No", "No"
        return lat, lon
    return None, None

def main_task():

    gps_port = '/dev/ttyACM0'  # Adjust this if your serial port is different
    baudrate = 9600

    while True:
        try:
            gps_ser = serial.Serial(gps_port, baudrate, timeout = 2)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)
        else:
            break


    while True:
        lat, lon = read_gps(gps_ser)
        Ax = accel_data.get('Ax', None)
        Ay = accel_data.get('Ay', None)
        if lat != None and lon != None:
#             print("Check")
            print(lat, ' ', lon, ' ', Ax, ' ', Ay, '\n')
            
if __name__ == "__main__":
    accel_data = {'Ax': 0, 'Ay': 0}

    accel_thread = threading.Thread(target=read_accel, args=(accel_data,))
    main_thread = threading.Thread(target=main_task)

    accel_thread.start()
    main_thread.start()

    # Join threads to wait for them to complete (though they are infinite loops)
    accel_thread.join()
    main_thread.join()



