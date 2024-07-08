import socket

# Define host and port
HOST = ''  # Remove localhost
PORT = 5000 #Changed from 12345

# Create socket object
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
                # Respond to request 1 with status data
                status_data = "21.0382788, 105.7824572"
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
