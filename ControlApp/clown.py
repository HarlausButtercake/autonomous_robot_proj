import customtkinter
from PIL import Image, ImageTk
import tkinter as tk
from customtkinter import CTkImage, CTkLabel
import get_direct as gwp
import get_way_point as ggwp # =)))))) 
from tkintermapview import TkinterMapView
import socket
import ast

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):


    APP_NAME = "Control desktop"
    WIDTH = 800
    HEIGHT = 500
    HOST = 'localhost'
    PORT = 12345
    file_path = "Resources/waypoint.txt"
    # file_path = r"C:\Users\phima\Desktop\final\Control_server\DesktopApp\waypoint.txt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string = ''
        self.client_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.pi_marker = []
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(3, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Set Marker",
                                                command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)
        
        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Markers",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Get Pi Location",
                                                command= self.get_pi_address)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)
        self.text_widget = customtkinter.CTkTextbox(master=self.frame_left,height= 120)
        self.text_widget.insert(text='click "Go" button to start the car',index= 0.0)
        self.text_widget.grid(padx= (20,20), pady= (20,0),row = 3, column= 0 )
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)
        
        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)
        #self.bind("<ButtonRelease>",lambda event: self.set_marker_event2())
        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)
        
        self.button_6 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Go",
                                                width=90,
                                                command=self.sent_data_to_pi) #change it to go function
        self.button_6.grid(row=0, column=2, sticky="w", padx=(12, 0), pady=12)
        

        # Set default values
        self.map_widget.set_address("Dai hoc cong nghe")
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("Dark")
    def get_pi_address(self):
        #change to get_pi_address code
        for marker in self.pi_marker:
            marker.delete()
        self.client_socket.send('pi_location'.encode())
        
        str_position =  self.client_socket.recv(1024).decode()
        self.pi_position = ast.literal_eval(str_position)
        #self.pi_position = self.map_widget.get_position()
        self.pi_marker.append(self.map_widget.set_marker(self.pi_position[0],self.pi_position[1]))
    def sent_data_to_pi(self):
        #change it to send data fucntion.
        self.string = 'Processing...'
        self.text_widget.delete(0.0,'end')
        self.text_widget.insert(0.0, text=self.string) 
        location_list = [self.pi_position]
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        lct_lst,distance = gwp.get_direct(self.pi_position[0],self.pi_position[1],current_position[0],current_position[1])
        # for i in range (len(lct_lst)-1):
        #     if distance[i] > 1500000: 
        #         #print('hehe' ,lct_lst)
        #         #print('huhu' ,lct_lst[i][0],lct_lst[i][1],lct_lst[i+1][0],lct_lst[i+1][1])
        #         # gps_lst = ggwp.get_way_point(lct_lst[i][0],lct_lst[i][1],lct_lst[i+1][0],lct_lst[i+1][1])
        #         #gps_lst = ggwp.get_way_point(21.00335, 105.82004, 21.02755, 105.7996)
               
        #         # for j in gps_lst: 
                  
        #         #     location_list.append(j)
        #     else:
        #         location_list.append(lct_lst[i+1])
        self.path = self.map_widget.set_path(lct_lst)# change to waypoint 
     
     #   self.path = self.map_widget.set_path(location_list)# change to waypoint 
        with open(self.file_path,'w') as file:
            file.write(str(self.pi_position[0])+',' + str(self.pi_position[1])+ '\n')
            for i in range (0,len(lct_lst)):  
                file.write(str(lct_lst[i][0])+','+str(lct_lst[i][1])+'\n')
        
        self.client_socket.send('send_waypoint'.encode())       
        with open(self.file_path,'rb') as file:
            waypoint_data = file.read()
            self.client_socket.sendall(waypoint_data)
        print("Waypoint file sent successfully.")

        self.string = 'Car started.\nTracking car position...'
        self.text_widget.delete(0.0,'end')
        self.text_widget.insert(0.0, text=self.string)        

        #print(wx,wy)
    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())
        

    def set_marker_event(self):
        #self.after(100, self.set_marker_event) 

        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        #print(current_position[0], current_position[1])
    def set_marker_event2(self):
        #self.after(100, self.set_marker_event) 
        self.marker_list[-1].delete()
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))
        #print(current_position[0], current_position[1])
    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.set_marker_event()
    app.start()

   
