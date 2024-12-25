import asyncio
import json
import multiprocessing
import os
import subprocess
import threading
import time
from tkinter import messagebox
import customtkinter
import cv2
import numpy as np
from PIL import ImageTk
from PIL import Image as Img
from tkintermapview import TkinterMapView
import socket
import ast
from tkinter import *
# from playsound import playsound
import pygame
customtkinter.set_default_color_theme("blue")

break_event = threading.Event()

class App(customtkinter.CTk):
    APP_NAME = "Control panel"
    WIDTH = 1024
    HEIGHT = 600
    HOST = 'localhost'  #piminer/localhost
    PORT = 1353


    # QR code detection object




    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attributes('-fullscreen', True)

        self.status = "Delivering"
        self.debug_marker = []
        self.marker_list = []
        self.qr_val = None

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        pygame.mixer.init()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.resizable(False, False)



        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))



        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=0)

        self.top_frame = customtkinter.CTkFrame(master=self, width=App.WIDTH, corner_radius=10, fg_color="White")
        self.top_frame.grid(pady=(0, 10), padx=(0, 0), row=0, column=0, sticky="nsew")

        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_rowconfigure(0, weight=1)


        self.top_left_frame = customtkinter.CTkFrame(master=self.top_frame, width=512)
        self.top_left_frame.grid(pady=(0, 0), padx=(0, 0), row=0, column=0, sticky="nsew")
        self.top_left_frame.grid_columnconfigure(0, weight=1)
        self.top_left_frame.grid_rowconfigure(0, weight=1)

        self.top_left_canvas = Canvas(self.top_left_frame, highlightthickness=0, width=512, height=500)
        self.top_left_canvas.grid(pady=(10, 0), padx=(0, 0), row=0, column=0, sticky="nsew")


        self.top_right_frame = customtkinter.CTkFrame(master=self.top_frame, width=512)
        self.top_right_frame.grid(pady=(0, 0), padx=(0, 0), row=0, column=1, sticky="nsew")
        self.top_right_frame.grid_columnconfigure(0, weight=1)
        self.top_right_frame.grid_rowconfigure(0, weight=1)

        self.top_right_canvas = Canvas(self.top_right_frame, highlightthickness=0, width=512, height=500)
        self.top_right_canvas.grid(pady=(10, 0), padx=(0, 0), row=0, column=0, sticky="nsew")


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

        self.button_1.grid(pady=(5, 5), padx=(0, 0), row=0, column=1, )
        self.dumb_button.configure(fg_color="Gray",
                                   text="",
                                   command=self.iconify,
                                   height=60, width=60)

        image = Img.open('Resource/order_info.png')

        frame_width = 512
        frame_height = 500
        image = image.resize((frame_width, frame_height))
        photo = ImageTk.PhotoImage(image)
        self.top_left_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.top_left_canvas.image = photo

        image = Img.open('Resource/delivering.png')
        frame_width = 512
        frame_height = 500
        image = image.resize((frame_width, frame_height))
        photo = ImageTk.PhotoImage(image)
        self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.top_right_canvas.image = photo

        update_status_thread = threading.Thread(target=self.thread_update)
        update_status_thread.daemon = True
        update_status_thread.start()

    def thread_update(self):
        while True:
            data = self.client_socket.recv(1024).decode()

            if data == "DELI_TOGGLE":
                # playsound("Resource/Audio/bell.mp3")
                pygame.mixer.Sound('Resource/Audio/bell.mp3').play()
                # print("toggle")
                self.status = "Reached"
                self.button_1.grid_forget()

                image = Img.open('Resource/order_info.png')
                image = image.resize((512, 500))
                photo = ImageTk.PhotoImage(image)
                self.top_left_canvas.create_image(0, 0, anchor="nw", image=photo)
                self.top_left_canvas.image = photo

                image = Img.open('Resource/dest_reached.png')
                image = image.resize((512, 500))
                photo = ImageTk.PhotoImage(image)
                self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
                self.top_right_canvas.image = photo
                self.dumb_button.configure(fg_color="Green",
                                           text="Confirm", font=("Arial", 26),
                                           command=self.init_qr,
                                           corner_radius=10,
                                           height=60, width=512)
                self.dumb_button.grid(pady=(5, 5), row=0, column=2, sticky="e")

            # if self.status == "Delivering":

    def init_qr(self):
        image = Img.open('Resource/qr_prompt.png')
        image = image.resize((512, 500))
        photo = ImageTk.PhotoImage(image)
        self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.top_right_canvas.image = photo
        self.dumb_button.grid_forget()
        thread = threading.Thread(target=self.scan_qr)
        thread.start()

    def scan_qr(self):
        process = subprocess.Popen(['python', 'qr_scan.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pygame.mixer.Sound('Resource/Audio/ask_qr.mp3').play()
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                data = output.decode().strip()
                if data == "USER_CONFIRM_20020320":
                    print("confirmed")
                    cmd = 'UNLOCK'
                    self.client_socket.send(cmd.encode())
                    pygame.mixer.Sound('Resource/Audio/success_qr.mp3').play()
                    image = Img.open('Resource/qr_done.png')
                    image = image.resize((512, 500))
                    photo = ImageTk.PhotoImage(image)
                    self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
                    self.top_right_canvas.image = photo

                    self.dumb_button.configure(
                                               text="Click here to finish the delivery", font=("Arial", 26),
                                               command=self.confirm_finish,
                                               corner_radius=10,
                                               height=60, width=512)
                    self.dumb_button.grid(pady=(5, 5), row=0, column=2, sticky="e")
                elif data == "NO_QR_SCANNED":
                    messagebox.showinfo("Notification", "QR scan timed out!")
                    image = Img.open('Resource/dest_reached.png')
                    image = image.resize((512, 500))
                    photo = ImageTk.PhotoImage(image)
                    self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
                    self.top_right_canvas.image = photo
                    self.dumb_button.configure(fg_color="Green",
                                               text="Confirm", font=("Arial", 26),
                                               command=self.init_qr,
                                               corner_radius=10,
                                               height=60, width=512)
                    self.dumb_button.grid(pady=(5, 5), row=0, column=2, sticky="e")
                else:
                    messagebox.showinfo("Notification", "Credential doesn't match!\nPlease try again")
                    self.dumb_button.configure(fg_color="Green",
                                               text="Confirm", font=("Arial", 26),
                                               command=self.init_qr,
                                               corner_radius=10,
                                               height=60, width=512)
                    self.dumb_button.grid(pady=(5, 5), row=0, column=2, sticky="e")
                    image = Img.open('Resource/dest_reached.png')
                    image = image.resize((512, 500))
                    photo = ImageTk.PhotoImage(image)
                    self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
                    self.top_right_canvas.image = photo

    def confirm_finish(self):
        self.dumb_button.grid_forget()
        self.button_1.grid(pady=(5, 5), padx=(0, 0), row=0, column=1, )
        image = Img.open('Resource/thank2.png')
        image = image.resize((512, 500))
        photo = ImageTk.PhotoImage(image)
        self.top_right_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.top_right_canvas.image = photo

        image = Img.open('Resource/thank1.png')
        image = image.resize((512, 500))
        photo = ImageTk.PhotoImage(image)
        self.top_left_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.top_left_canvas.image = photo
        pygame.mixer.Sound('Resource/Audio/thank.mp3').play()
        cmd = 'LOCK'
        self.client_socket.send(cmd.encode())





    def dumb(self):
        pass

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

def main_task():
    app = App()
    app.start()

if __name__ == "__main__":
    main_thread = threading.Thread(target=main_task, )
    main_thread.daemon = True
    main_thread.start()

    main_thread.join()



