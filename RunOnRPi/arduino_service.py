import socket
import subprocess
import threading
import time

import serial

# Define host and port
HOST = 'localhost'  # Remove localhost
PORT = 4010  # Changed from 12345
ARDUINO_PORT = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
# , '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5'
PORT_NUM = 0
DEFAULT_PW = 150


def toggle_port(port):
    port += 1
    if port >= 6:
        return 0
    else:
        return port

def move_robot(arduino_ser, direction, pulse_w):
    if direction == "Forward":
        command = "FM\r\n"
    elif direction == "Reverse":
        command = "BM\r\n"
    elif direction == "Left":
        command = "LM\r\n"
    elif direction == "Right":
        command = "RM\r\n"
    elif direction == "StLeft":
        command = "lM\r\n"
    elif direction == "StRight":
        command = "rM\r\n"
    else:
        command = "H0\r\n"
    arduino_ser.write(command.encode('ascii'))
    print(command)

def sonar_task():
    sonar_port = 1
    sonar_status = 0
    while True:
        while True:
            try:
                arduino_son = serial.Serial(ARDUINO_PORT[sonar_port], 115200, timeout=2)
                print("Arduino found! Stand by for 3 seconds!")
                break
            except serial.serialutil.SerialException:
                sonar_port = toggle_port(sonar_port)
            except Exception as e:
                if sonar_status == 0:
                    print(f"(Ultrasonic) An error occurred: {e}\n")
                    # print(f"Error type: {type(e)}")
                    sonar_status = 1
        time.sleep(3)  # a MUST
        arduino_son.flushInput()
        arduino_son.flushOutput()
        cmd_check = "AU\r\n" # Are you part of the sonar block ?
        arduino_son.write(cmd_check.encode('ascii'))
        response = arduino_son.readline().decode('ascii').strip()
        if response == "Y":
            print("This Arduino is controlling the sensors!\n")
            break
        else:
            print(f"{ARDUINO_PORT[sonar_port]} is NOT controlling the sonar!\n")
            sonar_status = toggle_port(sonar_status)
            time.sleep(2)

    while True:
        if arduino_son.in_waiting > 0:  # Check if data is available
            data = arduino_son.readline().decode('utf-8').strip()
            print(data)



def engine_task():
    engine_port = 0
    engine_status = 0
    while True:
        while True:
            try:
                arduino_eng = serial.Serial(ARDUINO_PORT[engine_port], 115200, timeout=2)
                print("Arduino found! Stand by for 3 seconds!")
                break
            except serial.serialutil.SerialException:
                engine_port = toggle_port(engine_port)
            except Exception as e:
                if engine_status == 0:
                    print(f"(Engine) An error occurred: {e}\n")
                    # print(f"Error type: {type(e)}")
                    engine_status = 1
        time.sleep(3)  # a MUST
        arduino_eng.flushInput()
        arduino_eng.flushOutput()
        cmd_check = "AR\r\n"  # Are you part of the engine block ?
        arduino_eng.write(cmd_check.encode('ascii'))
        response = arduino_eng.readline().decode('ascii').strip()
        if response == "Y":
            print("This Arduino is the correct one!\n")
            break
        else:
            print(f"{ARDUINO_PORT[engine_port]} is not controlling the engines!\n")
            engine_port = toggle_port(engine_port)
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
                    move_robot(arduino_eng, data[4:], DEFAULT_PW)
                else:
                    move_robot(arduino_eng, "Halt", DEFAULT_PW)
                    print()

            arduino_socket.close()

        except Exception as e:
            print(f"An error occurred: {e}\nAwaiting new middleman...")

    server_socket.close()


if __name__ == "__main__":
    engine_thread = threading.Thread(target=engine_task)
    # sonar_thread = threading.Thread(target=sonar_task)

    # Start both threads
    engine_thread.start()
    # sonar_thread.start()

    # Join threads to wait for them to complete (though they are infinite loops)
    engine_thread.join()
    # sonar_thread.join()
    # main_thread.join()
