import serial.serialutil
import pynmea2
import numpy as np
import mpu6050
import time
import sys
# import control # Physical control

# Define the serial port and baudrate
gps_port = '/dev/ttyACM2'  # Adjust this if your serial port is different
baudrate = 9600

def coord_to_rad(coord):
    return coord / 180 *np.pi

def read_gps(gps_ser):
    line = gps_ser.readline().decode('utf-8', errors='ignore')

    locquality = None
#     return 69, 69
    if line.startswith('$GPGGA'):
#         print(line)
        msg = pynmea2.parse(line)

        # Extract latitude, longitude, and timestamp from the message
#         lat = msg.latitude / 180 * np.pi
#         lon = msg.longitude / 180 * np.pi
        locquality = msg.gps_qual
        lat = msg.latitude
        lon = msg.longitude
        if locquality == 0:
            return 0, 0, 0
        else:
            return locquality, lat, lon
    return None, None, None


if __name__ == "__main__":
    lat = 21.0383064
    lon = 105.7826117
    quality = 1
    while len(sys.argv) > 1:
        print(quality, ' ', lat, ' ', lon, '\n')
        # lat -= 0.0000001 * 200
        # lon -= 0.0000001 * 200
        # lat = round(lat, 7)
        # lon = round(lon, 7)
    while True:
        try:
            gps_ser = serial.Serial(gps_port, baudrate, timeout = 2)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)
        else:
            break

    while True:
        try:
            quality, lat, lon = read_gps(gps_ser)
            # if lat is not None and lon is not None:
            if quality is not None:
                print(quality, ' ', lat, ' ', lon, '\n')
        except Exception as e:

            #
            print(f"An error occurred: {e}")
            # time.sleep(2)
        
        
        
        

            
        
        
    



