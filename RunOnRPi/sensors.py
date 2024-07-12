import mpu6050
import numpy as np


def read_sensor_data():
    # Read the accelerometer values
    accelerometer_data = mpu6050.get_accel_data()
    a = accelerometer_data['x']
    # Read the gyroscope values
    gyroscope_data = mpu6050.get_gyro_data()
    w = gyroscope_data['z'] / 180 * np.pi

    return a, w

mpu6050 = mpu6050.mpu6050(0x68)
while True:
    a, w = read_sensor_data()
    print('Forward accel:', a, '; Bearing:', w, '\n')
