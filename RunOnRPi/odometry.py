import mpu6050 
import numpy as np
import smbus
import time
# from mpu6050 import mpu6050

mpu = mpu6050.MPU6050(1, 0x68)
mpu.dmp_initialize()
mpu.set_DMP_enabled(True)

packet_size = mpu.DMP_get_FIFO_packet_size()
FIFO_buffer = [0]*64

# g = 9.8 # gravity
g = 9.8

while True:
    if mpu.isreadyFIFO(packet_size):
        FIFO_buffer = mpu.get_FIFO_bytes(packet_size)
        
        accel = mpu.get_acceleration()
#         Ax = accel.x * 2*g / 2**15
#         Ay = accel.y * 2*g / 2**15
#         Az = accel.z * 2*g / 2**15
        
        accel_dmp = mpu.DMP_get_acceleration_int16(FIFO_buffer)
        Ax = accel_dmp.x * 2*g / 2**15 * 2
        Ay = accel_dmp.y * 2*g / 2**15 * 2
#         Az_dmp = accel_dmp.z * 2*g / 2**15 * 2
        
        print(Ax, " ", Ay, "\n")




