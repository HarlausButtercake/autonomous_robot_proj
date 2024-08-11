import customtkinter
from PIL import Image, ImageTk
import tkinter as tk
from customtkinter import CTkImage, CTkLabel
import get_direct as gwp
import get_way_point as ggwp # =)))))) real funni me go haha
from tkintermapview import TkinterMapView
import socket
import ast
from tkinter import PhotoImage

customtkinter.set_default_color_theme("blue")



class App(customtkinter.CTk):
    APP_NAME = "Control panel"
    WIDTH = 800
    HEIGHT = 600
    HOST = 'localhost' #piminer/localhost
    PORT = 5000
    file_path = "waypoint.txt"
    # file_path = r"C:\Users\phima\Desktop\final\Control_server\DesktopApp\waypoint.txt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pi_marker = []
        self.debug_marker = []
        self.marker_list = []
        self.coord_list = []

        self.string = ''
        self.client_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)





        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(5, weight=1)

        # self.button_1 = customtkinter.CTkButton(master=self.frame_left,
        #                                         text="Set Marker",
        #                                         command=self.set_marker_event)
        # self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)
        
        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Markers",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Center on robot",
                                                command= self.get_pi_address)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        self.button_6 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Go",
                                                # width=90,
                                                command=self.sent_data_to_pi)
        self.button_6.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)

        self.button_7 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Show marker set",
                                                command=self.show_marker_set)
        self.button_7.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)

        self.text_widget = customtkinter.CTkTextbox(master=self.frame_left, height=120)
        self.text_widget.insert(text='click "Go" button to start the car', index=0.0)
        self.text_widget.grid(padx=(20, 20), pady=(20, 0), row=5, column=0)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Map Types", anchor="w") #Tile Server
        self.map_label.grid(row=6, column=0, padx=(20, 20), pady=(20, 0))

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["Default view", "Satellite view"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=7, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)
        
        self.map_widget = TkinterMapView(self.frame_right, corner_radius=100)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 20), pady=(20, 20))

        #21.0368116 105.7820678;;; VNU main gate
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

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
        # READ THIS YOU GREMLIN BEFORE IT READS YOU
        # https://github.com/TomSchimansky/TkinterMapView
        # https://customtkinter.tomschimansky.com/documentation/
        #####################################################################

        # Set default values
        self.map_widget.set_address("Dai hoc cong nghe")
        self.map_option_menu.set("Default view")
        self.appearance_mode_optionemenu.set("Light")

        self.go_to_location(21.0368116, 105.7820678, 18)
        self.clear_marker_event()
        #######################

        self.map_widget.add_right_click_menu_command(label="Add waypoint",
                                                command=self.add_marker_event,
                                                pass_coords=True)

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
        return(ast.literal_eval(str_position))


    def get_pi_address(self):
        for marker in self.pi_marker:
            marker.delete()

        self.pi_position = self.fetch_robot_location()
        print(self.pi_position)
        #self.pi_position = self.map_widget.get_position()
        self.pi_marker.append(self.map_widget.set_marker(self.pi_position[0],self.pi_position[1]))
        self.go_to_location(self.pi_position[0],self.pi_position[1], 20)

    def sent_data_to_pi(self):
        #change it to send data fucntion.
        self.string = 'Processing...'
        self.text_widget.delete(0.0,'end')
        self.text_widget.insert(0.0, text=self.string) 
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


        with open(self.file_path,'w') as file:
            file.write(str(self.pi_position[0])+',' + str(self.pi_position[1])+ '\n')
            for i in range (0, len(self.coord_list)):
                file.write(str(self.coord_list[i][0])+','+str(self.coord_list[i][1])+'\n')
        
        self.client_socket.send('send_waypoint'.encode())       
        with open(self.file_path,'rb') as file:
            waypoint_data = file.read()
            self.client_socket.sendall(waypoint_data)
        print("Waypoint file sent successfully.")

        self.string = 'Car started.\nTracking car position...'
        self.text_widget.delete(0.0,'end')
        self.text_widget.insert(0.0, text=self.string)

    def show_marker_set(self):
        for marker in self.debug_marker:
            marker.delete()

        photo = PhotoImage(file="dot.png")
        x = 0
        y = 0
        with open('set.txt', 'r') as file:
            for line in file:
                fields = line.strip().split(' ')
                lat = float(fields[0])
                long = float(fields[1])
                marker = self.map_widget.set_marker(lat, long, icon=photo)
                x, y = lat, long
                self.debug_marker.append(marker)

        self.go_to_location(x, y, 30)


    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())
        

    def set_marker_event(self):
        #self.after(100, self.set_marker_event) 
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
            coord.delete()


    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "Default view":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Satellite view":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()

   
