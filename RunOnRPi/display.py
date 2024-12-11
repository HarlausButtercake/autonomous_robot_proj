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



class App(customtkinter.CTk):
    APP_NAME = "Control panel"
    WIDTH = 1024
    HEIGHT = 600
    HOST = 'localhost'  #piminer/localhost
    PORT = 1353



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attributes('-fullscreen', True)

        self.pi_marker = []
        self.debug_marker = []
        self.marker_list = []
        self.coord_list = []

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.resizable(False, False)

        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.connect((self.HOST, self.PORT))

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=0)

        self.top_frame = customtkinter.CTkFrame(master=self, width=App.WIDTH, corner_radius=10, fg_color="White")
        self.top_frame.grid(pady=(0, 10), padx=(0, 0), row=0, column=0, sticky="nsew")

        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_rowconfigure(0, weight=1)

        self.top_left_frame = customtkinter.CTkFrame(master=self.top_frame, width=500, corner_radius=10, fg_color="Red")
        self.top_left_frame.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, sticky="nsew")

        self.top_left_frame.grid_columnconfigure(0, weight=1)
        self.top_left_frame.grid_rowconfigure(0, weight=1)

        # Create a canvas
        self.top_left_canvas = Canvas(self.top_left_frame, highlightthickness=0, width=500, height=500)
        self.top_left_canvas.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, sticky="nsew")

        # Load the image
        image = Img.open('Resource/order_info.png')

        # Resize the image to fit the frame (500x500)
        frame_width = 500
        frame_height = 500
        image = image.resize((frame_width, frame_height))

        # Convert the resized image to PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Place the resized image in the center of the canvas
        self.top_left_canvas.create_image(0, 0, anchor="nw", image=photo)

        # Keep a reference to the image to avoid garbage collection
        self.top_left_canvas.image = photo



        # self.top_left_frame.grid_columnconfigure(0, weight=0)
        # self.top_left_frame.grid_rowconfigure(0, weight=0)
        #
        #
        # self.top_left_canvas = Canvas(self.top_left_frame)
        # self.top_left_canvas.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, sticky="nsew")
        # # self.top_left_canvas.pack()
        #
        # image = Img.open('Resource/order_info.png')
        # # image = image.resize((500, 500))
        # photo = ImageTk.PhotoImage(image)
        # photo = ImageTk.PhotoImage(image)
        #
        # # Place the resized image in the center of the canvas
        # self.top_left_canvas.create_image(0, 0, anchor="nw", image=photo)
        #
        # # Keep a reference to the image to avoid garbage collection
        # self.top_left_canvas.image = photo

        # self.top_right_frame = customtkinter.CTkFrame(master=self.top_frame, width=500, corner_radius=10,
        #                                              fg_color="White")
        # self.top_right_frame.grid(pady=(0, 10), padx=(0, 0), row=0, column=0, sticky="nsew")
        # self.top_right_canvas = Canvas(self.top_left_frame, width=500, height=500)
        # self.top_right_canvas.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, sticky="nsew")
        #
        # image = Img.open('Resource/order_info.png')
        # photo = ImageTk.PhotoImage(image)
        # image = image.resize((500, 500))
        # self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
        # self.top_right_canvas.image = photo

        # image_path = "Resource/delivering.png"
        # image = Img.open(image_path)
        # sphoto = ImageTk.PhotoImage(image)
        # label = customtkinter.CTkLabel(master=self.top_frame, image=sphoto, text="")
        # label.place(relwidth=1, relheight=1)
        # self.top_frame.image = sphoto

        self.bottom_frame = customtkinter.CTkFrame(master=self, corner_radius=10, fg_color="Gray",)
        self.bottom_frame.grid(pady=(0, 10), padx=(5, 5), row=1, column=0, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=0)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(2, weight=0)

        self.button_debug_exit = customtkinter.CTkButton(master=self.bottom_frame,
                                                         text="", font=("Arial", 8), height=60, width=60,
                                                         fg_color="Gray",
                                                         command=self.on_closing)
        self.button_debug_exit.grid(row=0, column=0, sticky="ew")
        # self.button_debug_exit.configure(fg_color="White", text_color="White", hover_color="White", border_color="White")

        self.button_1 = customtkinter.CTkButton(master=self.bottom_frame,
                                                text="Property of LOREM IPSUM GmbH. Do not tamper!", font=("Arial", 26), height=60,
                                                fg_color="Red",
                                                command=self.dumb)
        self.button_1.grid(pady=(5, 5), padx=(0, 0), row=0, column=1, )

        self.dumb_button = customtkinter.CTkButton(master=self.bottom_frame,
                                                   fg_color="Gray",
                                                   command=self.iconify,
                                                   height=60, width=60, text="")
        self.dumb_button.grid(row=0, column=2, sticky="e")

    #     process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)
    # def
    #
    #     while True:
    #         output = process.stdout.readline()
    #         if output == '' and process.poll() is not None:
    #             break
    #         if output.strip() and output.strip() != "Invalid":
    #             try:
    #                 qual, lat, lon = map(float, output.strip().split())
    #             except ValueError:
    #                 print(f"Invalid line received: {output.strip()}")
    #         time.sleep(1)

    def set_image(self, frame, image_path):
        pass

    def dumb(self):
        pass

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()



if __name__ == "__main__":
    app = App()
    app.start()
    # rtc_thread.join()



