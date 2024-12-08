import subprocess
import time

process = subprocess.Popen(['python', '-u', 'timebase.py'], stdout=subprocess.PIPE, text=True)

while True:
    output = process.stdout.readline()
    if output == '' and process.poll() is not None:
        break
    if output.strip() and output.strip() != "Invalid":
        try:

            print(output + "sex")
        except ValueError:
            print(f"Invalid line received: {output.strip()}")
    time.sleep(1)