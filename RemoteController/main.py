import asyncio
import multiprocessing
import subprocess
import threading

import numpy
import customtkinter
import cv2
import numpy as np
from PIL import ImageTk
from PIL import Image as Img
from tkintermapview import TkinterMapView
import socket
import ast
from tkinter import *
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
from av import VideoFrame

customtkinter.set_default_color_theme("blue")
from cam_rtc_fetch import start_rtc
frame_queue = multiprocessing.Queue()
rtc_thread = threading.Thread(target=start_rtc, args=(frame_queue,))
rtc_thread.daemon = True


class App(customtkinter.CTk):
    APP_NAME = "Control panel"
    WIDTH = 1024
    HEIGHT = 768
    HOST = 'piminer'  #piminer/localhost
    PORT = 5000
    file_path = "waypoint.txt"
    CTRL_BUTTON_SIZE = 80



    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = queue
        self.pi_marker = []
        self.debug_marker = []
        self.marker_list = []
        self.coord_list = []

        self.feed_process = ''
        self.feed_thread = None
        self.feed_status = 0

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=300, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_rowconfigure(1, weight=1)



        # self.button_7 = customtkinter.CTkButton(master=self.frame_left,
        #                                         text="Show marker set",
        #                                         command=self.show_marker_set)
        # self.button_7.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)

        # ============ subframe_left_upper ============

        self.subframe_left_upper = customtkinter.CTkFrame(master=self.frame_left, corner_radius=10)
        self.subframe_left_upper.grid(pady=(0, 0), padx=(10, 10), row=0, column=0)
        self.subframe_left_upper.grid_rowconfigure(5, weight=0)
        self.subframe_left_upper.grid_columnconfigure(1, weight=0)

        self.live_feed_window = customtkinter.CTkCanvas(master=self.subframe_left_upper, height=200)

        self.live_feed_window.grid(pady=(10, 0), padx=(20, 20), row=0, column=0)

        self.button_1 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Start live feed",
                                                command=self.show_feed)
        self.button_1.grid(pady=(10, 0), padx=(20, 20), row=1, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Clear Markers",
                                                # width=700,
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(10, 0), padx=(20, 20), row=2, column=0)

        self.button_3 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Center on robot",
                                                command=self.get_pi_address)
        self.button_3.grid(pady=(10, 0), padx=(20, 20), row=3, column=0)

        self.button_6 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Go",
                                                command=self.sent_data_to_pi)
        self.button_6.grid(pady=(10, 10), padx=(20, 20), row=4, column=0)

        # ============ subframe_left_lower ============

        self.subframe_left_lower = customtkinter.CTkFrame(master=self.frame_left, corner_radius=10)
        self.subframe_left_lower.grid(pady=(20, 0), padx=(10, 10), row=1, column=0)
        # self.subframe_left_lower.grid_rowconfigure(4, weight=0)
        # self.subframe_left_lower.grid_columnconfigure(3, weight=0)

        self.video_frame = customtkinter.CTkLabel(master=self.subframe_left_lower)
        self.video_frame.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, columnspan=3)

        self.forward_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                      text="Forward",
                                                      # command=self.forward,
                                                      width=self.CTRL_BUTTON_SIZE,
                                                      height=self.CTRL_BUTTON_SIZE)
        self.forward_button.grid(pady=(0, 5), padx=(0, 0), row=1, column=1)
        self.forward_button.bind("<ButtonPress-1>", lambda event: self.forward())
        self.forward_button.bind("<ButtonRelease-1>", lambda event: self.halt())

        self.reverse_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                      text="Reverse",
                                                      # command=self.reverse,
                                                      width=self.CTRL_BUTTON_SIZE,
                                                      height=self.CTRL_BUTTON_SIZE)
        self.reverse_button.grid(pady=(5, 20), padx=(0, 0), row=3, column=1)
        self.reverse_button.bind("<ButtonPress-1>", lambda event: self.reverse())
        self.reverse_button.bind("<ButtonRelease-1>", lambda event: self.halt())

        self.left_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Left",
                                                   # command=self.left,
                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.left_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=0)
        self.left_button.bind("<ButtonPress-1>", lambda event: self.left())
        self.left_button.bind("<ButtonRelease-1>", lambda event: self.halt())

        self.right_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                    text="Right",
                                                    # command=self.right,
                                                    width=self.CTRL_BUTTON_SIZE,
                                                    height=self.CTRL_BUTTON_SIZE)
        self.right_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=2)
        self.right_button.bind("<ButtonPress-1>", lambda event: self.right())
        self.right_button.bind("<ButtonRelease-1>", lambda event: self.halt())
        self.bind("<d>", lambda event: self.mecha_steer_right())
        self.bind("<KeyRelease-d>", lambda event: self.halt())

        self.halt_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Halt",
                                                   command=self.halt,
                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.halt_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=1)

        self.steer_left = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                    text="Right",
                                                    # command=self.right,
                                                    width=self.CTRL_BUTTON_SIZE,
                                                    height=self.CTRL_BUTTON_SIZE)
        self.steer_left.grid(pady=(5, 5), padx=(5, 5), row=0, column=0)
        self.steer_left.bind("<ButtonPress-1>", lambda event: self.mecha_steer_left())
        self.steer_left.bind("<ButtonRelease-1>", lambda event: self.halt())

        self.steer_right = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Halt",
                                                   command=self.halt,
                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.steer_right.grid(pady=(5, 5), padx=(5, 5), row=0, column=2)
        self.steer_right.bind("<ButtonPress-1>", lambda event: self.mecha_steer_right())
        self.steer_right.bind("<ButtonRelease-1>", lambda event: self.halt())

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=100)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 20), pady=(20, 20))

        #21.0368116 105.7820678;;; VNU main gate
        # self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        # self.entry = customtkinter.CTkEntry(master=self.frame_right,
        #                                     placeholder_text="type address")
        # self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        # self.entry.bind("<Return>", self.search_event)
        #self.bind("<ButtonRelease>",lambda event: self.set_marker_event2())
        # self.button_5 = customtkinter.CTkButton(master=self.frame_right,
        #                                         text="Search",
        #                                         width=90,
        #                                         command=self.search_event)
        # self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        #####################################################################
        # READ THIS
        # https://github.com/TomSchimansky/TkinterMapView
        # https://customtkinter.tomschimansky.com/documentation/
        #####################################################################

        # Set default values

        # self.map_widget.set_address("Dai hoc cong nghe")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        # self.customtkinter.set_appearance_mode("Light")

        self.go_to_location(21.0368116, 105.7820678, 18)
        self.clear_marker_event()
        #######################

        self.string = ''
         #CONNECTION

        self.map_widget.add_right_click_menu_command(label="Add waypoint",
                                                     command=self.add_marker_event,
                                                     pass_coords=True)



    def show_frame(self):
        while True:
            try:
                frame = self.queue.get()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # cv2.imshow("Frame", frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                image = Img.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                # self.live_feed_window.delete("all")
                self.live_feed_window.create_image(0, 0, image=photo, anchor="nw")
                self.live_feed_window.image = photo
            except Exception as e:
                print(e)




    def show_feed(self):
        if self.feed_status == 0:

            update_frame_thread = threading.Thread(target=self.show_frame)
            update_frame_thread.daemon = True
            update_frame_thread.start()

            self.button_1.configure(text="Stop live feed")

            self.feed_status = 1
        else:
            self.button_1.configure(text="Start live feed")
            self.feed_status = 0


    def change_view(self, new_map: str):
        if new_map == "Map view":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Live camera feed":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def add_marker_event(self, coords):
        print("Add marker:", coords)
        #new_marker = self.map_widget.set_marker(coords[0], coords[1], text="new marker")
        self.marker_list.append(self.map_widget.set_marker(coords[0], coords[1]))
        self.coord_list.append(coords)

    def go_to_location(self, x, y, zoom):
        self.map_widget.set_position(x, y)  # 21.0368116 105.7820678;;; VNU main gate
        self.map_widget.set_zoom(zoom)

    def fetch_robot_location(self):
        self.client_socket.send('pi_location'.encode())
        str_position = self.client_socket.recv(1024).decode()
        return (ast.literal_eval(str_position))

    def get_pi_address(self):
        for marker in self.pi_marker:
            marker.delete()

        self.pi_position = self.fetch_robot_location()
        print(self.pi_position)
        #self.pi_position = self.map_widget.get_position()
        self.pi_marker.append(self.map_widget.set_marker(self.pi_position[0], self.pi_position[1]))
        self.go_to_location(self.pi_position[0], self.pi_position[1], 20)

    def sent_data_to_pi(self):
        #change it to send data fucntion.
        self.string = 'Processing...'
        # self.text_widget.delete(0.0, 'end')
        # self.text_widget.insert(0.0, text=self.string)
        location_list = [self.get_pi_address()]
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        # lct_lst,distance = gwp.get_direct(self.pi_position[0],self.pi_position[1],current_position[0],current_position[1])
        # for i in range (len(lct_lst)-1):
        #     if distance[i] > 1500000:
        #         print('hehe' ,lct_lst)
        #         print('huhu' ,lct_lst[i][0],lct_lst[i][1],lct_lst[i+1][0],lct_lst[i+1][1])
        #         gps_lst = ggwp.get_way_point(lct_lst[i][0],lct_lst[i][1],lct_lst[i+1][0],lct_lst[i+1][1])
        #         gps_lst = ggwp.get_way_point(21.00335, 105.82004, 21.02755, 105.7996)
        #
        #         for j in gps_lst:
        #
        #             location_list.append(j)
        #     else:
        #         location_list.append(lct_lst[i+1])
        # self.path = self.map_widget.set_path(lct_lst)# change to waypoint

        #   self.path = self.map_widget.set_path(location_list)# change to waypoint

        #    with open(self.file_path,'w') as file:
        #        file.write(str(self.pi_position[0])+',' + str(self.pi_position[1])+ '\n')
        #        for i in range (0,len(lct_lst)):
        #            file.write(str(lct_lst[i][0])+','+str(lct_lst[i][1])+'\n')

        with open(self.file_path, 'w') as file:
            file.write(str(self.pi_position[0]) + ',' + str(self.pi_position[1]) + '\n')
            for i in range(0, len(self.coord_list)):
                file.write(str(self.coord_list[i][0]) + ',' + str(self.coord_list[i][1]) + '\n')

        self.client_socket.send('send_waypoint'.encode())
        with open(self.file_path, 'rb') as file:
            waypoint_data = file.read()
            self.client_socket.sendall(waypoint_data)
        print("Waypoint file sent successfully.")

        self.string = 'Car started.\nTracking car position...'
        # self.text_widget.delete(0.0, 'end')
        # self.text_widget.insert(0.0, text=self.string)

    def show_marker_set(self):
        pass
        # for marker in self.debug_marker:
        #     marker.delete()
        #
        # photo = PhotoImage(file="dot.png")
        # x = 0
        # y = 0
        # with open('set.txt', 'r') as file:
        #     for line in file:
        #         fields = line.strip().split(' ')
        #         lat = float(fields[0])
        #         long = float(fields[1])
        #         marker = self.map_widget.set_marker(lat, long, icon=photo)
        #         x, y = lat, long
        #         self.debug_marker.append(marker)

        # self.go_to_location(x, y, 30)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        photo = PhotoImage(file="dot.png")
        current_position = self.map_widget.get_position()
        marker = self.map_widget.set_marker(current_position[0], current_position[1], icon=photo)
        self.marker_list.append(marker)

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()
        for marker in self.debug_marker:
            marker.delete()
        for coord in self.coord_list:
            try:
                coord.delete()
            except Exception as e:
                print(e)

    def forward(self):
        direction = "MNL_" + "Forward"
        self.client_socket.send(direction.encode())

    def reverse(self):
        direction = "MNL_" + "Reverse"
        self.client_socket.send(direction.encode())

    def left(self):
        direction = "MNL_" + "Left"
        self.client_socket.send(direction.encode())

    def right(self):
        direction = "MNL_" + "Right"
        self.client_socket.send(direction.encode())

    def halt(self):
        direction = "MNL_" + "Halt"
        self.client_socket.send(direction.encode())

    def mecha_steer_left(self):
        direction = "MNL_" + "StLeft"
        self.client_socket.send(direction.encode())

    def mecha_steer_right(self):
        direction = "MNL_" + "StRight"
        self.client_socket.send(direction.encode())

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

def main_task(queue):
    app = App(queue)
    app.start()


if __name__ == "__main__":


    # Start customtkinter app in a separate thread
    main_thread = threading.Thread(target=main_task, args=(frame_queue,))
    main_thread.daemon = True
    main_thread.start()

    # Start WebRTC process in a separate thread

    rtc_thread.start()

    main_thread.join()
    # rtc_thread.join()



