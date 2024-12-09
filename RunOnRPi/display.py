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

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.top_frame = customtkinter.CTkFrame(master=self, width=App.WIDTH, corner_radius=10, fg_color="White")
        self.top_frame.grid(pady=(0, 10), padx=(0, 0), row=0, column=0, sticky="nsew")

        image_path = "Resource/delivering.png"
        image = Img.open(image_path)
        sphoto = ImageTk.PhotoImage(image)
        label = customtkinter.CTkLabel(master=self.top_frame, image=sphoto, text="")
        label.place(relwidth=1, relheight=1)
        self.top_frame.image = sphoto

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

        self.dumb_button = customtkinter.CTkButton(master=self.bottom_frame, fg_color="Gray", height=60, width=60, text="")
        self.dumb_button.grid(row=0, column=2, sticky="e")

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



