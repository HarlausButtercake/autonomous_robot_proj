import asyncio
import json
import multiprocessing
import subprocess
import threading
import time
from PIL import Image, ImageTk
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

shutdown_status = threading.Event()


class App(customtkinter.CTk):
    APP_NAME = "Control panel"
    WIDTH = 1280
    HEIGHT = 800
    HOST = 'piminer'  #piminer/localhost
    PORT = 5000
    file_path = "waypoint.txt"
    CTRL_BUTTON_SIZE = 80



    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.in_test_mode = False
        self.bind("<KeyPress-p>", lambda event: self.test_mode())

        self.queue = queue
        self.pi_marker = []
        self.debug_marker = []
        self.marker_list = []
        self.coord_list = []
        self.pi_lat = None
        self.pi_lon = None
        self.pi_cargo_lock = True

        self.prev_mecha_cmd = ''
        self.feed_process = ''
        self.feed_thread = None
        self.feed_status = 0
        self.focus_status = False

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.bind("<Command-q>", self.on_closing)
        # self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.resizable(False, False)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        self.robot_icon = PhotoImage(file="Resource/bot_ico.png")

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=700, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_rowconfigure(1, weight=1)

        update_status_thread = threading.Thread(target=self.update_status)
        update_status_thread.daemon = True
        update_status_thread.start()

        # ============ subframe_left_upper ============

        self.subframe_left_upper = customtkinter.CTkFrame(master=self.frame_left, corner_radius=10)
        self.subframe_left_upper.grid(pady=(0, 0), padx=(10, 10), row=0, column=0)
        self.subframe_left_upper.grid_rowconfigure(5, weight=0)
        self.subframe_left_upper.grid_columnconfigure(1, weight=0)

        self.live_feed_window = customtkinter.CTkCanvas(master=self.subframe_left_upper, height=200)

        self.live_feed_window.grid(pady=(10, 0), padx=(20, 20), row=0, column=0)
        simage = cv2.imread("Resource/nonesig.png")
        sframe_rgb = cv2.cvtColor(simage, cv2.COLOR_BGR2RGB)
        simage = Img.fromarray(sframe_rgb)
        sphoto = ImageTk.PhotoImage(simage)
        self.live_feed_window.create_image(190, 100, image=sphoto, anchor="center")
        self.live_feed_window.image = sphoto
        self.button_1 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Live feed\nSTART",
                                                command=self.show_feed)
        self.button_1.grid(pady=(10, 0), padx=(20, 20), row=1, column=0)



        self.button_3 = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Center on robot",
                                                corner_radius=0, width=200,
                                                command=self.zoom_to_pi
                                                )
        self.button_3.grid(pady=(10, 0), padx=(20, 20), row=2, column=0)

        self.button_3_status = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="GPS quality: N/A",
                                                corner_radius=0, width=200,
                                                command=self.zoom_to_pi)
        self.button_3_status.grid(pady=(0, 0), padx=(20, 20), row=3, column=0)

        self.cargo_button = customtkinter.CTkButton(master=self.subframe_left_upper,
                                                text="Unlock cargo\n", width=200, height=50,
                                                command=self.cargo_handler)
        self.cargo_button.grid(pady=(10, 10), padx=(20, 20), row=4, column=0)

        # ============ subframe_left_lower ============

        self.subframe_left_lower = customtkinter.CTkFrame(master=self.frame_left, corner_radius=10)
        self.subframe_left_lower.grid(pady=(20, 0), padx=(10, 10), row=1, column=0)

        # self.video_frame = customtkinter.CTkLabel(master=self.subframe_left_lower)
        # self.video_frame.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, columnspan=3)

        self.dist_left = customtkinter.CTkButton(master=self.subframe_left_lower, width=self.CTRL_BUTTON_SIZE)
        self.dist_left.grid(pady=(10, 0), padx=(0, 0), row=0, column=0)

        self.dist_forw = customtkinter.CTkButton(master=self.subframe_left_lower, width=self.CTRL_BUTTON_SIZE)
        self.dist_forw.grid(pady=(10, 0), padx=(0, 0), row=0, column=1)

        self.dist_right = customtkinter.CTkButton(master=self.subframe_left_lower, width=self.CTRL_BUTTON_SIZE)
        self.dist_right.grid(pady=(10, 0), padx=(0, 0), row=0, column=2)

        self.forward_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                      text="Forward",
                                                      width=self.CTRL_BUTTON_SIZE,
                                                      height=self.CTRL_BUTTON_SIZE)
        self.forward_button.grid(pady=(0, 5), padx=(0, 0), row=1, column=1)
        self.forward_button.bind("<ButtonPress-1>", lambda event: self.mecha_forward())
        self.forward_button.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())
        self.bind("<KeyPress-w>", lambda event: self.mecha_forward())
        self.bind("<KeyRelease-w>", lambda event: self.mecha_halt())

        self.reverse_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                      text="Reverse",
                                                      width=self.CTRL_BUTTON_SIZE,
                                                      height=self.CTRL_BUTTON_SIZE)
        self.reverse_button.grid(pady=(5, 20), padx=(0, 0), row=3, column=1)
        self.reverse_button.bind("<ButtonPress-1>", lambda event: self.mecha_reverse())
        self.reverse_button.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())
        self.bind("<KeyPress-s>", lambda event: self.mecha_reverse())
        self.bind("<KeyRelease-s>", lambda event: self.mecha_halt())

        self.left_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Left",
                                                   # command=self.left,
                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.left_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=0)
        self.left_button.bind("<ButtonPress-1>", lambda event: self.mecha_left())
        self.left_button.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())
        self.bind("<KeyPress-a>", lambda event: self.mecha_left())
        self.bind("<KeyRelease-a>", lambda event: self.mecha_halt())

        self.right_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                    text="Right",
                                                    width=self.CTRL_BUTTON_SIZE,
                                                    height=self.CTRL_BUTTON_SIZE)
        self.right_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=2)
        self.right_button.bind("<ButtonPress-1>", lambda event: self.mecha_right())
        self.right_button.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())
        self.bind("<KeyPress-d>", lambda event: self.mecha_right())
        self.bind("<KeyRelease-d>", lambda event: self.mecha_halt())

        self.halt_button = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Halt",
                                                   command=self.mecha_halt,
                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.halt_button.grid(pady=(5, 5), padx=(5, 5), row=2, column=1)

        self.steer_left = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                    text="Steer Left",
                                                    command=self.mecha_steer_left,
                                                    width=self.CTRL_BUTTON_SIZE,
                                                    height=self.CTRL_BUTTON_SIZE)
        self.steer_left.grid(pady=(5, 5), padx=(5, 5), row=1, column=0)
        self.steer_left.bind("<ButtonPress-1>", lambda event: self.mecha_steer_left())
        self.steer_left.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())

        self.steer_right = customtkinter.CTkButton(master=self.subframe_left_lower,
                                                   text="Steer Right",

                                                   width=self.CTRL_BUTTON_SIZE,
                                                   height=self.CTRL_BUTTON_SIZE)
        self.steer_right.grid(pady=(5, 5), padx=(5, 5), row=1, column=2)
        self.steer_right.bind("<ButtonPress-1>", lambda event: self.mecha_steer_right())
        self.steer_right.bind("<ButtonRelease-1>", lambda event: self.mecha_halt())

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

    # def toggle_auto_center(self):
    #     if self.focus_status:
    #         self.focus_status = False
    #         self.button_3.configure(text="Start centering on robot")
    #     else:
    #         self.focus_status = True
    #         self.button_3.configure(text="Stop centering on robot")

    def test_mode(self):
        cmd = "DELI_DESTREACHED"
        self.client_socket.send(cmd.encode())

    def cargo_handler(self):
        if self.pi_cargo_lock:
            cmd = "CARGO_UNLOCK"
            self.client_socket.send(cmd.encode())
        else:
            cmd = "CARGO_LOCK"
            self.client_socket.send(cmd.encode())

    def change_dist_button(self, button, value):
        if 0 < value < 20:
            color = "Red"
            textcolor = "White"
            text_content = f"{value} cm"
        elif 20 <= value < 80:
            color = "#E5C100"
            textcolor = "White"
            text_content = f"{value} cm"
        elif value >= 80:
            color = "Green"
            textcolor = "White"
            text_content = f"{value} cm"
        else:
            color = "Gray"
            textcolor = "Black"
            text_content = "N/A"
        button.configure(fg_color=color, text_color=textcolor, hover_color=color,
                                         border_color=color, text=text_content)

    def show_frame(self):
        while not shutdown_status.is_set():
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
            self.button_1.configure(text="Please wait...")
            cmd = "CAM_START"
            self.client_socket.send(cmd.encode())

            time.sleep(5)
            try:
                rtc_thread.start()
            except Exception as e:
                pass
            shutdown_status.clear()
            update_frame_thread = threading.Thread(target=self.show_frame)
            update_frame_thread.daemon = True
            update_frame_thread.start()

            self.button_1.configure(text="Live feed\nSTOP")

            self.feed_status = 1
        else:
            shutdown_status.set()

            cmd = "CAM_STOP"
            self.client_socket.send(cmd.encode())


            simage = cv2.imread("Resource/nonesig.png")
            sframe_rgb = cv2.cvtColor(simage, cv2.COLOR_BGR2RGB)
            simage = Img.fromarray(sframe_rgb)
            sphoto = ImageTk.PhotoImage(simage)
            self.live_feed_window.delete("all")
            self.live_feed_window.create_image(190, 100, image=sphoto, anchor="center")
            self.live_feed_window.image = sphoto

            self.button_1.configure(text="Live feed\nSTART")
            self.feed_status = 0

    def update_status(self):
        self.pi_lat = 21.0368116
        self.pi_lon = 105.7820678
        bear = 0
        while True:
            try:
                data = self.client_socket.recv(1024)
                status_json = data.decode()
                print(status_json)
                status_data = json.loads(status_json)
                self.pi_lat = status_data.get("lat")  # Returns "Connection successful"
                self.pi_lon = status_data.get("lon")  # Returns 200
                # self.pi_marker[0] = lat
                # self.pi_marker[1] = lat
                bear = status_data.get("bearing")
                bear = int(float(bear))
                forw = int(status_data.get("forw"))
                left = int(status_data.get("left"))
                right = int(status_data.get("right"))
                self.change_dist_button(self.dist_forw, forw)
                self.change_dist_button(self.dist_left, left)
                self.change_dist_button(self.dist_right, right)
                self.pi_cargo_lock = status_data.get("cargo_lock")
                if not self.pi_cargo_lock:
                    self.cargo_button.configure(fg_color="Red", text_color="White", hover_color="Red",
                                                   border_color="Red", text="Cargo UNLOCKED\nClick to lock")
                else:
                    self.cargo_button.configure(fg_color="Green", text_color="White", hover_color="Green",
                                                border_color="Green", text="Cargo locked\nClick to unlock")

                gps_quality = int(status_data.get("gps_qual"))
                if gps_quality <= 0:
                    self.button_3_status.configure(fg_color="Red", text_color="White", hover_color="Red",
                                     border_color="Red", text="GPS Quality: POOR")
                elif gps_quality == 1:
                    self.button_3_status.configure(fg_color="#E5C100", text_color="White", hover_color="#E5C100",
                                     border_color="#E5C100", text="GPS Quality: MEDIOCRE")
                elif gps_quality > 1:
                    self.button_3_status.configure(fg_color="Green", text_color="White", hover_color="Green",
                                     border_color="Green", text="GPS Quality: GOOD")

            except Exception as e:
                print(e)
            original_image = Img.open("Resource/bot_ico.png").convert('RGBA')
            # rotated_image = original_image.rotate(-240, expand=True)  # -240 degrees for clockwise rotation
            rotated_image = original_image.rotate(-bear, expand=True)

            rotated_image_tk = ImageTk.PhotoImage(rotated_image)

            for marker in self.pi_marker:
                marker.delete()
            self.pi_marker.append(self.map_widget.set_marker(self.pi_lat, self.pi_lon, icon=rotated_image_tk))
            time.sleep(1)

    def add_marker_event(self, coords):
        print("Add marker:", coords)
        self.marker_list.append(self.map_widget.set_marker(coords[0], coords[1]))
        self.coord_list.append(coords)

    def change_view(self, new_map: str):
        if new_map == "Map view":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Live camera feed":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def go_to_location(self, x, y, zoom):
        self.map_widget.set_position(x, y)  # 21.0368116 105.7820678;;; VNU main gate
        self.map_widget.set_zoom(zoom)

    def fetch_robot_location(self):
        self.client_socket.send('pi_location'.encode())
        str_position = self.client_socket.recv(1024).decode()
        return ast.literal_eval(str_position)

    def zoom_to_pi(self):
        self.go_to_location(self.pi_lat, self.pi_lon, 20)
        # for marker in self.pi_marker:
        #     marker.delete()
        #
        # self.pi_position = self.fetch_robot_location()
        # print(self.pi_position)
        # #self.pi_position = self.map_widget.get_position()
        # self.pi_marker.append(self.map_widget.set_marker(self.pi_position[0], self.pi_position[1]))
        # self.go_to_location(self.pi_position[0], self.pi_position[1], 20)

    def sent_data_to_pi(self):
        pass
        # location_list = [self.get_pi_address()]
        # current_position = self.map_widget.get_position()
        # self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        #
        # with open(self.file_path, 'w') as file:
        #     file.write(str(self.pi_position[0]) + ',' + str(self.pi_position[1]) + '\n')
        #     for i in range(0, len(self.coord_list)):
        #         file.write(str(self.coord_list[i][0]) + ',' + str(self.coord_list[i][1]) + '\n')
        #
        # self.client_socket.send('send_waypoint'.encode())
        # with open(self.file_path, 'rb') as file:
        #     waypoint_data = file.read()
        #     self.client_socket.sendall(waypoint_data)
        # print("Waypoint file sent successfully.")


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

    def is_mecha_cmd_can_repeat(self, cmd): # idc grammer
        return cmd == "MNL_" + "Forward" and cmd == "MNL_" + "Halt"

    def mecha_post(self, cmd):
        # DISABLE = False
        # if self.is_mecha_cmd_can_repeat(cmd):
        #     self.client_socket.send(cmd.encode())
        # else:
        #     if cmd == self.prev_mecha_cmd:
        #         pass
        #     else:
        #         self.client_socket.send(cmd.encode())
        self.prev_mecha_cmd = cmd
        self.client_socket.send(cmd.encode())





    def mecha_forward(self):
        direction = "MNL_" + "Forward"
        self.mecha_post(direction)

    def mecha_reverse(self):
        direction = "MNL_" + "Reverse"
        self.mecha_post(direction)

    def mecha_left(self):
        direction = "MNL_" + "Left"
        self.mecha_post(direction)

    def mecha_right(self):
        direction = "MNL_" + "Right"
        self.mecha_post(direction)

    def mecha_halt(self):
        direction = "MNL_" + "Halt"
        self.mecha_post(direction)

    def mecha_steer_left(self):
        direction = "MNL_" + "StLeft"
        self.mecha_post(direction)

    def mecha_steer_right(self):
        direction = "MNL_" + "StRight"
        self.mecha_post(direction)

    def on_closing(self, event=0):
        cmd = "CAM_STOP"
        self.client_socket.send(cmd.encode())
        shutdown_status.set()
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



    main_thread.join()
    # rtc_thread.join()



