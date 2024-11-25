import smbus
import time
import math
import csv


bus = smbus.SMBus(1)
address = 0x60

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

while True:
#     out = read_byte(2)
#     ut2 = read_byte(3)
#     ut2 = 0
    out = read_word(2)
#     out /= 10
#     round(out, 1)
#     out -= 150
#     if out < 0:
#         out = 360 + out
    out /= 10
    print(f"{out}")
    time.sleep(0.5)