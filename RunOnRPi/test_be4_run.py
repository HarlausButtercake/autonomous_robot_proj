import numpy as np 
import matplotlib.pyplot as plt 
def gps_to_x_y(lat0,lng0,lat,lng):
        dLat = lat - lat0
        dLng = lng - lng0

        rns = 6343618.3790280195
        rew = 6380879.425381593 

        y = rns*np.sin(dLat)
        x = rew*np.sin(dLng)*np.cos(lat0) 
        
        return x,y 
lat0 = 21.03949431917736/180*np.pi
lon0 =  105.77122080476737/180*np.pi
#21.03949431917736, 105.77122080476737

waypointx = [0] 
waypointy = [0] 
with open('waypoint.txt','r') as file : 
    for line in file : 
        fields = line.strip().split(',')
        lat = float(fields[0]) /180*np.pi
        long = float(fields[1]) /180*np.pi
        x,y = gps_to_x_y(lat0,lon0,lat,long)
        waypointx.append(x)
        waypointy.append(y)

plt.figure() 

plt.plot(waypointx,waypointy)
plt.show()


