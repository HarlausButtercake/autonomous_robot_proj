# import requests
# import cv2
# from io import BytesIO
# import numpy as np
# import get_direct as gd
# def get_distance_per_pixel(x,y,xf,yf,xl,yl):
#     deltaX = x / np.abs(xf- xl)
#     deltaY = y / np.abs(yf- yl)
#     return deltaX, deltaY
# def get_way_point(lat0,lng0,lat,lng):
#     #waypoint = []
#     x,y = gd.Gps_to_x_y(gd.deg_to_rad(lat0), gd.deg_to_rad(lng0),gd.deg_to_rad(lat),gd.deg_to_rad(lng))
#
#     #doan duong 1km tro len thi moi co kha nang cong => chi set waypoint = image cho duogn 1 km, k thi cho thang luon :D
#     url = "https://rsapi.goong.io/staticmap/route?origin=" + str(lat0)+ "," + str(lng0) + "&destination="+ str(lat)+ ","+ str(lng)+ "&width=300&height=200&vehicle=car&api_key=2fs1WEAFwFsfZ5UqFOgq6HPJvSA7HOqfKKB9yorg"
#     print(url)
#     response = requests.get(url)
#
#     xf = -1
#     xl = -1
#     yf = -1
#     yl = -1
#     if response.status_code == 200:
#         # Extract image data from the response
#       #  image_data = np.frombuffer(response.content, np.uint8)
#
#         # Decode the image data and open it as an image
#       #  image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
#         image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
#         gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#
#         width,height = gray.shape
#
#         index_list = []
#         if (np.abs(x)> np.abs(y) and x >= 0) : #xet trai sang phai \
#             print(1)
#             for i in range (width) :
#                 for j in range (height):
#                     if gray[i,j] < 50 :
#                         if xf == -1 :
#                             xf = i
#                             yf = j
#                         xl = i
#                         yl = j
#                         index_list.append([i,j])
#                     else :
#                         gray[i,j] = 255
#
#         elif (np.abs(x)> np.abs(y) and x < 0) : # xet phai sang trai
#             print(2)
#
#             for i in range (width):
#                 for j in range (height):
#                     if gray[(width-1-i),j] < 50 :
#                         if xf == -1 :
#                             xf = i
#                             yf = j
#                         xl = i
#                         yl = j
#                         gray[(width-1-i),j] = 255
#                         index_list.append([width-i-1,j])
#                         break
#                     else :
#                         gray[width-i-1,j] = 255
#             for i in range (width):
#                 for j in range(height):
#                     if gray(i,j)<50 :
#                         xl = i
#                         yl = j
#                         index_list.append(i,j)
#                         break
#
#         elif ( np.abs(y)> np.abs(x) and y < 0  ): # xet tren xuong duoi
#             print(3)
#
#             for i in range (height):
#                 for j in range (width):
#
#                     if gray[i,j] < 50 :
#                         if xf == -1 :
#                             xf = i
#                             yf = j
#                         xl = i
#                         yl = j
#                         index_list.append([i,j])
#                     else :
#                         gray[j,i] = 255
#         else : # xet duoi len tren
#             print(4)
#             for i in range (height):
#                 for j in range (width):
#                     k = height - 1  - i
#
#                     if gray[j,k] < 50 :
#                         if xf == -1 :
#                             xf = j
#                             yf = i
#                         xl = j
#                         yl = i
#                         index_list.append([j,k])
#                     else :
#                         gray[j,k] = 255
#         gps_list=[]
#         for index in index_list:
#             deltaX,deltaY = get_distance_per_pixel(x,y,xf,yf,xl,yl)
#             lat,lng = gd.x_y_to_gps(index[0]*deltaX,index[1]*deltaY, lat0, lng0)
#             gps_list.append([lat,lng])
#         #cv2.imshow('Grayscale Image', gray)
#         # Display the image
#         # cv2.imshow('Image', image)
#         # cv2.waitKey(0)
#         # cv2.destroyAllWindows()
#     else:
#         print("Failed to fetch image. Status code:", response.status_code)
#
#
#     return gps_list
# # gps_list = get_way_point(21.00335,105.82004,21.02755,105.7996)
# # print(gps_list)