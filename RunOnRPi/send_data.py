import json
import socket
import subprocess
import sys
import threading
import time

import serial
from dns.rdtypes.ANY.NINFO import NINFO
from future.backports.datetime import datetime

# Define host and port
HOST = ''  # Remove localhost
PORT = 5000 #Changed from 12345
ARDUINO_PORT = 4010
DEFAULT_PW = 150
GPS_ENABLE = True
COMPASS_ENABLE = True
arduino_cmd = "H0\r\n"
stop_event = threading.Event()
begin_status = threading.Event()
process = None
buffer_bear = 0
client_socket = None
ARDUINO_SET = True
cargo_lock_status = True

def bearing_task(shared_bearing):
    if not COMPASS_ENABLE:
        while not stop_event.is_set():
            global buffer_bear
            buffer_bear += 1
            if buffer_bear >= 360:
                buffer_bear -= 360
            shared_bearing['main'] = buffer_bear
            time.sleep(1)
    else:
        bear_process = subprocess.Popen(['python', '-u', 'piccompass.py'], stdout=subprocess.PIPE, text=True)

        while not stop_event.is_set():
            output = bear_process.stdout.readline()
            if output == '' and bear_process.poll() is not None:
                break
            if output.strip() and output.strip() != "Invalid":
                buf = None
                try:
                     buf = float(output.strip())
                     shared_bearing['main'] = buf
                     # print(shared_bearing['main'])
                     # print(f"{shared_sonar_data['front']} {shared_sonar_data['left']} {shared_sonar_data['right']}")
                except ValueError:
                    print(f"Invalid value received: {output.strip()}")

def read_gps_coordinates(gps_data):
    if GPS_ENABLE:
        process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)

        while not stop_event.is_set():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output.strip() and output.strip() != "Invalid":
                try:
                    qual, lat, lon = map(float, output.strip().split())
                    gps_data['qual'] = qual
                    gps_data['lat'] = lat
                    gps_data['lon'] = lon
                    # print(f"GPS Data: {lat}, {lon}")
                except ValueError:
                    print(f"Invalid line received: {output.strip()}")
            time.sleep(1)
    else:
        process = subprocess.Popen(['python', '-u', 'gps.py'] + ['testmode'], stdout=subprocess.PIPE, text=True)

        while not stop_event.is_set():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output.strip() and output.strip() != "Invalid":
                try:
                    qual, lat, lon = map(float, output.strip().split())
                    gps_data['qual'] = qual
                    gps_data['lat'] = lat
                    gps_data['lon'] = lon
                    # print(f"GPS Data: {lat}, {lon}")
                except ValueError:
                    print(f"Invalid line received: {output.strip()}")
            time.sleep(1)

def main_task(shared_bearing, cargo_lock_status):
    if len(sys.argv) > 1:
        print("Running without Arduino")
        global ARDUINO_SET
        ARDUINO_SET = False
    else:
        arduino_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        arduino_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        arduino_socket.bind((HOST, ARDUINO_PORT))
        arduino_socket.listen(5)
        print("Waiting for Arduino service...")
        global glob_ard_socket, process
        while not stop_event.is_set():
            try:
                # arduino_socket.settimeout(2.0)
                # ard_process = subprocess.Popen(['python', '-u', 'arduino_service.py'], stdout=subprocess.PIPE, text=True)
                glob_ard_socket, addr = arduino_socket.accept()
                # disp_process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)
                print("Connected to Arduino service!")
                break
                # while True:
                #     if arduino_cmd != prev_cmd:
                #         client_socket.send(arduino_cmd.encode())
                #         prev_cmd = arduino_cmd
            except Exception as e:
                print(f"(Arduino) An error occurred: {e}\nAwaiting new connection...")

    global client_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen(2)
    print("Waiting for connection...")
    while not stop_event.is_set():
        try:
            # Accept incoming connection
            # server_socket.settimeout(2.0)
            global client_socket
            client_socket, addr = server_socket.accept()
            begin_status.set()
            print("Connection established with", addr)
            global arduino_cmd
            while not stop_event.is_set():
                # Receive data from the client
                data = client_socket.recv(1024).decode().strip()

                print(data)
                if not data:
                    break

                if data == 'STATUS':
                    pass
                    # client_socket.send(status_data.encode())
                elif data == 'send_waypoint':
                    # Receive waypoint file from PC
                    with open('waypoint.txt', 'wb') as file:

                        waypoint_data = client_socket.recv(1024)
                        if not waypoint_data:
                            break
                        file.write(waypoint_data)
                    print("Waypoint file received successfully.")
                elif data.startswith("MNL_") and ARDUINO_SET:
                    arduino_cmd = data
                    glob_ard_socket.send(arduino_cmd.encode())
                elif data.startswith("DELI_"):
                    if data[5:] == "DESTREACHED":
                        display_client_socket.send(data.encode())
                elif data.startswith("CARGO_"):
                    if data[6:] == "LOCK":
                        arduino_cmd = data
                        glob_ard_socket.send(arduino_cmd.encode())
                        # print("Locking cargo")
                        cargo_lock_status['main'] = True
                    elif data[6:] == "UNLOCK":
                        arduino_cmd = data
                        glob_ard_socket.send(arduino_cmd.encode())
                        print("Unlocking cargo")
                        cargo_lock_status['main'] = False
                    else:
                        pass
                elif data.startswith("CAM_"):
                    if data[4:] == "START":
                        process = subprocess.Popen(['python', '-u', 'cam_rtc.py'],)
                    elif data[4:] == "STOP":
                        print("Stopping WebRTC")
                        try:
                            process.terminate()
                        except Exception as e:
                            print(e)
                    else:
                        pass
                # elif data.startswith("DESTINATION_REACHED"):
                    # arduino_cmd = data
                    # glob_ard_socket.send(arduino_cmd.encode())
                    # print(arduino_cmd)
                    # move_robot(arduino_ser, data[4:], DEFAULT_PW)
                else:
                    print("Invalid command:", data)

            client_socket.close()

        except Exception as e:
            print(f"(Main) An error occurred: {e}\nAwaiting new connection...")
            print("Stopping WebRTC")
            try:
                begin_status.clear()
                process.terminate()
            except Exception as e:
                print(e)
            # Continue to listen for new connection s
        # finally:
        #     stop_event.set()

    # stop_event.set()
    # print("done")
    server_socket.close()

def status_task(gps_data, shared_bearing, cargo_lock_status):
    forw = 0
    left = 20
    right = 40
    while not stop_event.is_set():
        while begin_status.is_set():
            time.sleep(1)
            try:
                dist_recv = glob_ard_socket.recv(1024).strip().decode()
                dist_recv = dist_recv.split('\n')
                dist_recv = dist_recv[-2]

                if ARDUINO_SET:
                    forw, left, right = map(int, dist_recv.split())
            except Exception as e:
                print(e)
            lat = gps_data.get('lat', None)
            lon = gps_data.get('lon', None)
            status_data = {
                # "time": datetime.now(),
                "cargo_lock": cargo_lock_status['main'],
                "lat": lat,
                "lon": lon,
                "gps_qual": 1,
                "bearing": shared_bearing['main'],
                "forw": forw,
                "left": left,
                "right": right,
            }
            # print(status_data)
            # Convert the dictionary to a JSON string
            status_json = json.dumps(status_data)

            # Send the JSON data as a byte-encoded string
            client_socket.send(status_json.encode())
            if not ARDUINO_SET:
                forw += 15
                if forw > 150:
                    forw = 0
                left += 15
                if left > 150:
                    left = 0
                right += 15
                if right > 150:
                    right = 0
            # time.sleep(1)

def display_task():
    display_host = 'localhost'
    display_port = 1353
    display_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    display_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    display_socket.bind((display_host, display_port))
    local_process = subprocess.Popen(['python', '-u', 'display.py'])
    # Listen for incoming connections
    display_socket.listen(2)
    print("Waiting for display...")
    while not stop_event.is_set():
        try:
            global display_client_socket
            display_client_socket, addr = display_socket.accept()
            print("Connection established with display")

        except Exception as e:
            print(f"(Display) An error occurred: {e}\nAwaiting new connection...")
#
if __name__ == "__main__":
    # Create threads for concurrent execution
    gps_data = {'qual': 0, 'lat': 21.0382788, 'lon': 105.7824572}
    shared_bearing = {'main': 0.0, 'not': 0}
    cargo_lock_status = {'main': True, 'not': 0}

    gps_prev = gps_data

    gps_thread = threading.Thread(target=read_gps_coordinates, args=(gps_data,))
    main_thread = threading.Thread(target=main_task, args=(shared_bearing, cargo_lock_status,))
    bearing_thread = threading.Thread(target=bearing_task, args=(shared_bearing,))
    status_thread = threading.Thread(target=status_task, args=(gps_data, shared_bearing, cargo_lock_status,))
    display_thread = threading.Thread(target=display_task,)

    # Start both threads
    gps_thread.start()
    main_thread.start()
    bearing_thread.start()
    status_thread.start()
    display_thread.start()
    # Join threads to wait for them to complete (though they are infinite loops)
    # gps_thread.join()
    # arduino_thread.join()
    # main_thread.join()
    try:
        # Join threads to wait for them to complete
        gps_thread.join()
        status_thread.join()
        main_thread.join()
        bearing_thread.join()
        display_thread.join()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Shutting down...")
        stop_event.set()


