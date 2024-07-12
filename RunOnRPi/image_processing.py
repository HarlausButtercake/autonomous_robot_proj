# xac dinh way point 
# dung directions api de xac dinh nhung diem gia tang waypoint 
import cv2 
import numpy as np 

filepath = r"C:\Users\phima\Downloads\Uf5m99h.jpeg"

image = cv2.imread(filepath)

gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

xf = -1 
yf = -1
xl = -1 
yl = -1 
width, height = gray.shape

case = 1 
index_list = []
if (case == 1) : #xet trai sang phai \
    print('ok')
    for i in range (width) :
        for j in range (height):
            if gray[i,j] < 70 :
                if xf == -1 : 
                    xf = i 
                    yf = j
                xl = i 
                yl = j
                index_list.append([i,j]) 
            else : 
                gray[i,j] = 255 

if (case == 2) : # xet phai sang trai 
    for i in range (width): 
        for j in range (height):
            if gray[width - i,j] < 70 :
                if xf == -1 : 
                    xf = i 
                    yf = j
                xl = i 
                yl = j
                index_list.append([i,j]) 
            else : 
                gray[i,j] = 255 
if (case == 3 ): # xet tren xuong duoi 
    for i in range (height): 
        for j in range (width):
            if gray[j,i] < 70 :
                if xf == -1 : 
                    xf = j 
                    yf = i
                xl = j
                yl = i
                index_list.append([i,j]) 
            else : 
                gray[i,j] = 255 
if (case == 4 ): # xet duoi len tren   
    for i in range (height): 
        for j in range (width):
            if gray[j,height - i] < 70 :
                if xf == -1 : 
                    xf = j 
                    yf = i
                xl = j
                yl = i
                index_list.append([i,j]) 
            else : 
                gray[i,j] = 255 
def get_distance_per_pixel(x,y,xf,yf,xl,yl):
    deltaX = x / np.abs(xf- xl)
    deltaY = y / np.abs(yf- yl)
    return deltaX, deltaY
print(index_list)
print(xf,yf,xl,yl)
cv2.imshow('gray',gray)
cv2.waitKey(0)
cv2.destroyAllWindows()