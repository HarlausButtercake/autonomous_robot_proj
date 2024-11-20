import socket
import subprocess
import threading
import time

import serial

# Define host and port
HOST = 'localhost'  # Remove localhost
PORT = 4010  # Changed from 12345
ARDUINO_PORT = '/dev/ttyACM0'
DEFAULT_PW = 150


def move_robot(arduino_ser, direction, pulse_w):
    if direction == "Forward":
        command = "FM\r\n"
    elif direction == "Reverse":
        command = "BM\r\n"
    elif direction == "Left":
        command = "LM\r\n"
    elif direction == "Right":
        command = "RM\r\n"
    else:
        command = "H0\r\n"
    arduino_ser.write(command.encode('ascii'))
    print(command)


if __name__ == "__main__":
    status = 0
    while True:
        while True:
            try:
                arduino = serial.Serial(ARDUINO_PORT, 115200, timeout=2)
                print("Arduino found! Stand by for 3 seconds!")
                break
            except Exception as e:
                if status == 0:
                    print(f"An error occurred: {e}\n")
                    status = 1
        time.sleep(3)  # a MUST
        arduino.flushInput()
        arduino.flushOutput()
        cmd_check = "ARU_ENGN\r\n" # Are you part of the engine block ?
        arduino.write(cmd_check.encode('ascii'))
        response = arduino.readline().decode('ascii').strip()
        if response == "Y":
            print("This Arduino is the correct one!\n")
            break
        else:
            print("This Arduino is not controlling the engines!\n")
            time.sleep(2)


    arduino_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    arduino_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    arduino_socket.connect((HOST, PORT))
    while True:
        try:
            # client_socket, addr = arduino_socket.accept()
            print("Connection established with Middleman")
            while True:
                # Receive data from the client
                data = arduino_socket.recv(1024).decode()

                if not data:
                    break

                if data.startswith("MNL_"):
                    # arduino_command = data[4:]
                    print(data)
                    move_robot(arduino, data[4:], DEFAULT_PW)
                else:
                    move_robot(arduino, "Halt", DEFAULT_PW)
                    print()

            arduino_socket.close()

        except Exception as e:
            print(f"An error occurred: {e}\nAwaiting new middleman...")

    server_socket.close()







