import math



def coll_vector_gen(num):
    if num == 0:
        return 0
    return 1000 / num
#
# def wrapto2pi(deg):
#     if deg > 4 *math.pi:
#         return 4 *math.pi - deg
#     elif deg > 2 *math.pi:
#         return 2 *math.pi - deg
#     elif 0 > deg > - 2 *math.pi:
#         return 2 *math.pi + deg
#     else:
#         raise ValueError("Value out of range")

def wrapto360(deg):
    if deg > 720:
        return 720 - deg
    elif deg > 360:
        return 360 - deg
    elif 0 > deg > -360:
        return 360 + deg
    elif 0 < deg < 360:
        return deg
    else:
        return deg

def wrapto2pi(rad):
    if rad > 4 * math.pi:
        return 4 * math.pi - rad
    elif rad > 2 * math.pi:
        return 2 * math.pi - rad
    elif 0 > rad > -2 * math.pi:
        return 2 * math.pi + rad
    else:
        return rad




def to_dest_deg(deg_dest, deg_curr):
    res = None
    buf = deg_curr - deg_dest
    buf = wrapto360(buf)
    if buf > 180:
        res = 360 - buf
        res = -res
    else:
        res = buf
    return res

print(to_dest_deg(40, 300))

def sum2vec(mag1, rad1, mag2, rad2):
    magx1 = mag1 * math.cos(rad1)
    magy1 = mag1 * math.sin(rad1)
    magx2 = mag2 * math.cos(rad2)
    magy2 = mag2 * math.sin(rad2)
    summagx = magx1 + magx2
    summagy = magy1 + magy2
    sum_mag = math.sqrt(summagx*summagx + summagy*summagy)
    sum_rad = math.atan2(summagy, summagx)
    return sum_mag, sum_rad