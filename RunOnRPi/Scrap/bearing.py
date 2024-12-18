
import smbus
import time
import math
import csv
bus = smbus.SMBus(1)

address = 0x1e


def read_byte(adr):
    return bus.read_byte_data(address, adr)


def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)


if __name__ == "__main__":
    write_byte(0, 0b01111000)  # Set to 8 samples @ 15Hz
    write_byte(1, 0b01000000)  # 1.3 gain LSb / Gauss 1090 (default)
    write_byte(2, 0b00000000)  # Continuous sampling

    time.sleep(1)

    scale = 0.92
    while True:
        x_out = read_word_2c(3) * scale
        y_out = read_word_2c(7) * scale
        z_out = read_word_2c(5) * scale

        # bearing = math.atan2(y_out, x_out)
        bearing = math.atan2(y_out, x_out) * 180 / math.pi
        # if (bearing < 0):
        #     bearing += 2 * math.pi

        declination = -0.02
        bearing += declination
        bearing %= 360

        # print(f"{x_out} {y_out} {round(bearing, 2)}")
        print(round(bearing, 2))
        time.sleep(0.2)
    
