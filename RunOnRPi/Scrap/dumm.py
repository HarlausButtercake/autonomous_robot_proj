from math import atan2

from numpy import rad2deg, pi

rad = 2*pi - 1.5*pi - atan2(20/3, 5)
deg = rad2deg(rad)
print(deg)