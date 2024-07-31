import subprocess
import time


def read_time(time_data):
    process = subprocess.Popen(['python', '-u', 'get_time.py'], stdout=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip() and output.strip() != "Invalid":
            try:
                time_data = output
                print(f"Time 2: {time_data}")
            except ValueError:
                print(f"Invalid line received: {output.strip()}")


if __name__ == "__main__":
    time_data = 100
    read_time(time_data)