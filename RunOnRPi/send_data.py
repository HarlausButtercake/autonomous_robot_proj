import socket
import subprocess
import threading
import time

import serial

# Define host and port
HOST = ''  # Remove localhost
PORT = 5000 #Changed from 12345
ARDUINO_PORT = 4010
# ARDUINO_PORT = '/dev/ttyACM0'
DEFAULT_PW = 150
GPS_ENABLE = False
arduino_cmd = "H0\r\n"
stop_event = threading.Event()



def read_gps_coordinates(gps_data):
    if GPS_ENABLE:
        process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output.strip() and output.strip() != "Invalid":
                try:
                    lat, lon = map(float, output.strip().split())
                    gps_data['lat'] = lat
                    gps_data['lon'] = lon
                    print(f"GPS Data: {lat}, {lon}")
                except ValueError:
                    print(f"Invalid line received: {output.strip()}")
            time.sleep(1)


def arduino_task():
    prev_cmd = ''




def main_task():
    arduino_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    arduino_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    arduino_socket.bind((HOST, ARDUINO_PORT))
    arduino_socket.listen(5)
    print("Waiting for Arduino service...")
    global glob_ard_socket
    while True:
        try:
            # arduino_socket.settimeout(2.0)

            glob_ard_socket, addr = arduino_socket.accept()
            print("Connected to Arduino service!")
            break
            # while True:
            #     if arduino_cmd != prev_cmd:
            #         client_socket.send(arduino_cmd.encode())
            #         prev_cmd = arduino_cmd
        except Exception as e:
            print(f"(Arduino) An error occurred: {e}\nAwaiting new connection...")


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
            client_socket, addr = server_socket.accept()
            print("Connection established with", addr)
            global arduino_cmd
            while True:
                # Receive data from the client
                data = client_socket.recv(1024).decode()

                if not data:
                    break

                if data == 'pi_location':
                    lat = gps_data.get('lat', None)
                    lon = gps_data.get('lon', None)

                    if lat is not None and lon is not None:
                        status_data = f"{lat}, {lon}"
                        gps_prev = status_data
                    else:
                        status_data = gps_prev

                    # else:
                    #     status_data = "No GPS data available"

                    client_socket.send(status_data.encode())
                elif data == 'send_waypoint':
                    # Receive waypoint file from PC
                    with open('waypoint.txt', 'wb') as file:

                        waypoint_data = client_socket.recv(1024)
                        if not waypoint_data:
                            break
                        file.write(waypoint_data)
                    print("Waypoint file received successfully.")
                elif data.startswith("MNL_"):
                    arduino_cmd = data
                    glob_ard_socket.send(arduino_cmd.encode())
                    # print(arduino_cmd)
                    # move_robot(arduino_ser, data[4:], DEFAULT_PW)
                else:
                    print("Invalid command:", data)

            client_socket.close()

        except Exception as e:
            print(f"(Main) An error occurred: {e}\nAwaiting new connection...")
            # Continue to listen for new connection s
        # finally:
        #     stop_event.set()

    # stop_event.set()
    # print("done")
    server_socket.close()


if __name__ == "__main__":
    # Create threads for concurrent execution
    gps_data = {'lat': 21.0382788, 'lon': 105.7824572}
    gps_prev = gps_data

    gps_thread = threading.Thread(target=read_gps_coordinates, args=(gps_data,))
    arduino_thread = threading.Thread(target=arduino_task)
    main_thread = threading.Thread(target=main_task)

    # Start both threads
    gps_thread.start()
    arduino_thread.start()
    main_thread.start()

    # Join threads to wait for them to complete (though they are infinite loops)
    # gps_thread.join()
    # arduino_thread.join()
    # main_thread.join()
    try:
        # Join threads to wait for them to complete
        gps_thread.join()
        arduino_thread.join()
        main_thread.join()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Shutting down...")
        stop_event.set()


