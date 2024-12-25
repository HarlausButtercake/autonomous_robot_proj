# import math
#
# import mpu6050
# import numpy as np
# import smbus
# import time
# # from mpu6050 import mpu6050
#
#
# # https://github.com/OmidAlekasir/mpu6050
#
# def read_byte(adr):
#     return bus.read_byte_data(address, adr)
#
# def read_word(adr):
#     high = bus.read_byte_data(address, adr)
#     low = bus.read_byte_data(address, adr + 1)
#     val = (high << 8) + low
#     return val
#
#
# def read_word_2c(adr):
#     val = read_word(adr)
#     if (val >= 0x8000):
#         return -((65535 - val) + 1)
#     else:
#         return val
#
#
# def write_byte(adr, value):
#     bus.write_byte_data(address, adr, value)
#
# def DECLINATION(rad, direction):
#     if direction == "E":
#         return rad
#     else:
#         return -rad;
#
# // South and West
# are
# negative
# case
# 'W':
# declination_offset_radians = 0 - ((declination_degs + (1 / 60 * declination_mins)) * (M_PI / 180));
# break;
#
#
# i2c_bus = 1
# device_address = 0x68
# freq_divider = 0x04
# mpu = mpu6050.MPU6050(i2c_bus, device_address, freq_divider)
#
# mpu.dmp_initialize()
# mpu.set_DMP_enabled(True)
#
# packet_size = mpu.DMP_get_FIFO_packet_size()
# FIFO_buffer = [0]*64
#
# # g = 9.8 # gravity
# g = 9.8
#
# address = 0x1e
# bus = smbus.SMBus(1)
# scale = 0.92
#
# write_byte(0, 0b01111000)  # Set to 8 samples @ 15Hz
# write_byte(1, 0b01000000)  # 1.3 gain LSb / Gauss 1090 (default)
# write_byte(2, 0b00000000)  # Continuous sampling
# while True:
#     if mpu.isreadyFIFO(packet_size):
#         FIFO_buffer = mpu.get_FIFO_bytes(packet_size)  # get all the DMP data here
#
#         # raw acceleration
#         accel = mpu.get_acceleration()
#         accel.x = accel.x * 2 * g / 2 ** 15
#         accel.y = accel.y * 2 * g / 2 ** 15
#         accel.z = accel.z * 2 * g / 2 ** 15
#
#         # quaternion
#         q = mpu.DMP_get_quaternion_int16(FIFO_buffer)
#         q.normalize()
#
#         # world-frame acceleration vectors (practical for INS)
#         accel_linear = mpu.get_linear_accel(accel, q)
#         Ax = round(accel_linear.x, 2)
#         Ay = round(accel_linear.y, 2)
#         Az_linear = round(accel_linear.z, 2)
#         # accel_dmp = mpu.DMP_get_acceleration_int16(FIFO_buffer)
#         # Ax = accel_dmp.x * 2 * g / 2 ** 15 * 2
#         # Ay = accel_dmp.y * 2 * g / 2 ** 15 * 2
#         # Az_dmp = accel_dmp.z * 2 * g / 2 ** 15 * 2
#
#         gyro = mpu.get_rotation()
#         Gx = gyro.x * 250 / 2 ** 15
#         Gy = gyro.y * 250 / 2 ** 15
#         Gz = gyro.z * 250 / 2 ** 15
# #         grav = mpu.DMP_get_gravity(q)
# #         roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(q)
#
#         x_out = read_word_2c(3) * scale
#         y_out = read_word_2c(7) * scale
#         z_out = read_word_2c(5) * scale
#
#         bearing = math.atan2(y_out, x_out)
#         if bearing < 0:
#             bearing += 2 * math.pi
#         if bearing > 2 * math.pi:
#             bearing -= 2 * math.pi
#
#         decline = DECLINATION
#         bearing = math.degrees(bearing) + declination
#
#
#
#         print(f"{Ax} {Ay} {Gz} {bearing}\n")
#
#
#
#
