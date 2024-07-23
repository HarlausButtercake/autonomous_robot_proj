import serial.serialutil
import pynmea2
import numpy as np
import mpu6050
import time
import sys
# import control # Physical control

# Define the serial port and baudrate
gps_port = '/dev/ttyACM0'  # Adjust this if your serial port is different
baudrate = 9600  # Adjust this if your GPS module uses a different baudrate



def coord_to_rad(coord):
    return coord / 180 *np.pi
def read_gps():
    line = gps_ser.readline().decode('utf-8', errors='ignore')
    if line.startswith('$GPGGA'):
        # Parse the NMEA sentence
        msg = pynmea2.parse(line)

        # Extract latitude, longitude, and timestamp from the message
#         lat = msg.latitude / 180 * np.pi
#         lon = msg.longitude / 180 * np.pi
        lat = msg.latitude
        lon = msg.longitude
        if lat == 0.0 or lon == 0.0:
            return "Invalid", "Invalid"
        return lat, lon
    return None, None

while True:
    try:
        gps_ser = serial.Serial(gps_port, baudrate, timeout = 2)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(2)
    else:
        break


while True:
    lat, lon = read_gps()
    if lat != None and lon != None:
        print(lat, ' ', lon, '\n')
        
        
        
        

            
        
        
    


