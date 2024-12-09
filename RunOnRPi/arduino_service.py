import math
import socket
import subprocess
import threading
import time
from vector import *
import serial
from numpy import atan2, pi


# Define host and port
HOST = 'localhost'  # Remove localhost
PORT = 4010  # Changed from 12345
ARDUINO_PORT = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2'
                , '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
PORT_LIMIT = 3
ULTRASONIC_CONFIRM = "AU\r\n"
ENGINE_CONFIRM = "AR\r\n"

PORT_NUM = 0
DEFAULT_PW = 150

ANGLE = 2*pi - 1.5*pi - atan2(20/3, 5)

stop_event = threading.Event()

def if_in_range(val):
    if 4 < val < 70:
        return True
    else:
        return False

def in_reverse_range(val):
    if val < 20:
        return True
    else:
        return False

# def bearing_task(shared_bearing):
#     process = subprocess.Popen(['python', '-u', 'piccompass.py'], stdout=subprocess.PIPE, text=True)
#
#     while not stop_event.is_set():
#         output = process.stdout.readline()
#         if output == '' and process.poll() is not None:
#             break
#         if output.strip() and output.strip() != "Invalid":
#             buf = None
#             try:
#                  buf = float(output.strip())
#                  shared_bearing['main'] = buf
#                  # print(shared_bearing['main'])
#                  # print(f"{shared_sonar_data['front']} {shared_sonar_data['left']} {shared_sonar_data['right']}")
#             except ValueError:
#                 print(f"Invalid value received: {output.strip()}")
        # time.sleep(1)

def toggle_port(port):
    port += 1
    if port >= PORT_LIMIT:
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

def sonar_task(shared_sonar_data):
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
        arduino_son.write(ULTRASONIC_CONFIRM.encode('ascii'))
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
            shared_sonar_data['front'], shared_sonar_data['left'], shared_sonar_data['right'], shared_sonar_data['rear'] = map(int, data.strip().split())
            to_send_data = f"{shared_sonar_data['front']} {shared_sonar_data['left']} {shared_sonar_data['right']}"
            arduino_socket.send(to_send_data.encode())



def engine_task(shared_sonar_data, bear):
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
        arduino_eng.write(ENGINE_CONFIRM.encode('ascii'))
        response = arduino_eng.readline().decode('ascii').strip()
        if response == "Y":
            print("This Arduino is controlling the engines!\n")
            break
        else:
            print(f"{ARDUINO_PORT[engine_port]} is not controlling the engines!\n")
            engine_port = toggle_port(engine_port)
            time.sleep(2)
    global arduino_socket
    arduino_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    arduino_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    arduino_socket.connect((HOST, PORT))
    while True:
        try:
            # client_socket, addr = arduino_socket.accept()
            print("Connection established with Middleman")
            while True:
                # Receive data from the client
                # print(bear['main']

                data = arduino_socket.recv(1024).decode()

                if not data:
                    break

                if data.startswith("MNL_"):
                    print(data)
                    if data.startswith("MNL_F"):
                        # move_robot(arduino_eng, data[4:], DEFAULT_PW)

                        if if_in_range(shared_sonar_data['front']) or if_in_range(shared_sonar_data['left']) or if_in_range(shared_sonar_data['right']):
                        # if shared_sonar_data['front'] != 0 or shared_sonar_data['left'] != 0 or shared_sonar_data['right'] != 0:
                            if in_reverse_range(shared_sonar_data['front']) and in_reverse_range(shared_sonar_data['left']) and in_reverse_range(shared_sonar_data['right']):
                                move_robot(arduino_eng, "Reverse", DEFAULT_PW)
                            else:
                                coll_vector = [coll_vector_gen(shared_sonar_data['front'])
                                               , coll_vector_gen(shared_sonar_data['left'])
                                               , coll_vector_gen(shared_sonar_data['right'])]
                                buf_mag, buf_rad = sum2vec(400, 0, coll_vector[0], pi)
                                # print(f"bug mag: {buf_mag}    buf rad: {buf_rad}")
                                buf_mag, buf_rad = sum2vec(buf_mag, buf_rad, coll_vector[1], pi - ANGLE)
                                # print(f"bug mag: {buf_mag}    buf rad: {buf_rad}")
                                buf_mag, buf_rad = sum2vec(buf_mag, buf_rad, coll_vector[2], pi + ANGLE)
                                # print(f"bug mag: {buf_mag}    buf rad: {buf_rad}")

                                buf_rad = wrapto2pi(buf_rad)
                                buf_rad = math.degrees(buf_rad)
                                print(buf_rad)
                                if 0 < buf_rad < 180:
                                    move_robot(arduino_eng, "StRight", DEFAULT_PW)
                                else:
                                    move_robot(arduino_eng, "StLeft", DEFAULT_PW)


                                # print(f"buff degree: {math.degrees(buf_rad)}")
                                # buf_dest_rad = math.radians(bear['main']) + buf_rad
                                # buf_dest_rad = wrapto2pi(buf_dest_rad)
                                # dest_deg = math.degrees(buf_dest_rad)
                                # print(f"dest degree: {dest_deg}    bear: {bear['main']}")
                                # if abs(to_dest_deg(dest_deg, bear['main'])) > 5:
                                #     if to_dest_deg(dest_deg, bear['main']) > 0:
                                #         move_robot(arduino_eng, "StRight", DEFAULT_PW)
                                #     else:
                                #         move_robot(arduino_eng, "StLeft", DEFAULT_PW)
                        else:
                            move_robot(arduino_eng, data[4:], DEFAULT_PW)
                    else:
                        move_robot(arduino_eng, data[4:], DEFAULT_PW)
                else:
                    move_robot(arduino_eng, "Halt", DEFAULT_PW)


            arduino_socket.close()

        except Exception as e:
            print(f"An error occurred: {e}\nAwaiting new middleman...")

    server_socket.close()




if __name__ == "__main__":
    shared_sonar_data = {'front': 0, 'left': 0, 'right': 0, 'rear': 0}
    shared_bearing = {'main': 0.0, 'not': 0}

    # bearing_thread = threading.Thread(target=bearing_task, args=(shared_bearing,) )
    engine_thread = threading.Thread(target=engine_task, args=(shared_sonar_data, shared_bearing))
    sonar_thread = threading.Thread(target=sonar_task, args=(shared_sonar_data,))

    # Start both threads
    # bearing_thread.start()
    engine_thread.start()
    sonar_thread.start()


    # bearing_thread.join()
    engine_thread.join()
    sonar_thread.join()
