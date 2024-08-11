import socket
import subprocess
import threading
import time

# Define host and port
HOST = ''  # Remove localhost
PORT = 5000 #Changed from 12345

def read_gps_coordinates(gps_data):
    # process = subprocess.Popen(['python', '-u', 'gps.py'], stdout=subprocess.PIPE, text=True)
    #
    # while True:
    #     output = process.stdout.readline()
    #     if output == '' and process.poll() is not None:
    #         break
    #     if output.strip() and output.strip() != "Invalid":
    #         try:
    #             lat, lon = map(float, output.strip().split())
    #             gps_data['lat'] = lat
    #             gps_data['lon'] = lon
    #             print(f"GPS Data: {lat}, {lon}")
    #         except ValueError:
    #             print(f"Invalid line received: {output.strip()}")
    #     time.sleep(1)
    a = 0

def main_task():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen(2)
    print("Waiting for connection...")
    while True:
        try:
            # Accept incoming connection
            client_socket, addr = server_socket.accept()
            print("Connection established with", addr)

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
                else:
                    print("Invalid command:", data)

            client_socket.close()

        except Exception as e:
            print(f"An error occurred: {e}\nAwaiting new connection...")
            # Continue to listen for new connection s

    server_socket.close()


if __name__ == "__main__":
    # Create threads for concurrent execution
    gps_data = {'lat': 21.0382788, 'lon': 105.7824572}
    gps_prev = gps_data

    # Start the GPS reading thread
    gps_thread = threading.Thread(target=read_gps_coordinates, args=(gps_data,))

    main_thread = threading.Thread(target=main_task)

    # Start both threads
    gps_thread.start()
    main_thread.start()

    # Join threads to wait for them to complete (though they are infinite loops)
    gps_thread.join()
    main_thread.join()


