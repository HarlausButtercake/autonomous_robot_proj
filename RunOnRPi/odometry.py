import mpu6050 
import numpy as np
import smbus
import time
# from mpu6050 import mpu6050


# https://github.com/OmidAlekasir/mpu6050

i2c_bus = 1
device_address = 0x68
freq_divider = 0x04
mpu = mpu6050.MPU6050(i2c_bus, device_address, freq_divider)

mpu.dmp_initialize()
mpu.set_DMP_enabled(True)

packet_size = mpu.DMP_get_FIFO_packet_size()
FIFO_buffer = [0]*64

# g = 9.8 # gravity
g = 9.8

while True:
    if mpu.isreadyFIFO(packet_size):
        FIFO_buffer = mpu.get_FIFO_bytes(packet_size)  # get all the DMP data here

        # raw acceleration
        accel = mpu.get_acceleration()
        accel.x = accel.x * 2 * g / 2 ** 15
        accel.y = accel.y * 2 * g / 2 ** 15
        accel.z = accel.z * 2 * g / 2 ** 15

        # quaternion
        q = mpu.DMP_get_quaternion_int16(FIFO_buffer)
        q.normalize()

        # world-frame acceleration vectors (practical for INS)
        accel_linear = mpu.get_linear_accel(accel, q)
        Ax_linear = round(accel_linear.x, 2)
        Ay_linear = round(accel_linear.y, 2)
        Az_linear = round(accel_linear.z, 2)

#         grav = mpu.DMP_get_gravity(q)
#         roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(q)
        print(f"{Ax_linear} {Ay_linear}\n")
#         print(f"{Ax_linear} {Ay_linear} {Az_linear} {roll_pitch_yaw.x} {roll_pitch_yaw.y} {roll_pitch_yaw.z}\n")




#         FIFO_buffer = mpu.get_FIFO_bytes(packet_size)
#         
#         accel = mpu.get_acceleration()
#         gyro = mpu.get_gyroscope()
# #         Ax = accel.x * 2*g / 2**15
# #         Ay = accel.y * 2*g / 2**15
# #         Az = accel.z * 2*g / 2**15
#         
#         accel_dmp = mpu.DMP_get_acceleration_int16(FIFO_buffer)
#         Ax = accel_dmp.x * 2*g / 2**15 * 2
#         Ay = accel_dmp.y * 2*g / 2**15 * 2
# #         Az_dmp = accel_dmp.z * 2*g / 2**15 * 2
#         gyro_dmp = mpu.get_gyroscope()
#         
#         print(Ax, " ", Ay, "\n")




