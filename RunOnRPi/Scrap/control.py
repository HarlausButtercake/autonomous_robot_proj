import serial 
import time
arduino_port = serial.Serial('COM9', baudrate=9600, timeout=1)
# banh trai la dang sau , banh phai dang truoc 


	# print('input pwm, dir? \n ')
	# command = input()

pwml = 200 
pwmr = 200 
dirr = 1
dirl = 1 
start_byte = 'a'
command = f"{start_byte} {pwmr} {pwmr} {dirr} {dirl}\n"
print(command)
starttime = time.time()




while True:
	arduino_port.write(command.encode('ascii'))
	print('run')
	time.sleep(1)	
	arduino_port.write(b"a 0 0 1 1\n")
	print('stop')

	time.sleep(1)

# starttime = time.time()
# while True:
#    
#     
#     if currentime - starttime > 1 : break 


print('stop')
# arduino_port.write(command.encode())
# arduino_port.write('\n'.encode())




# if(input() == '1' ): 
# 	
# arduino_port.write(command.encode())
	

	

#chay 3 m ve phia truoc : 
# command = "180 180 1 1"
# arduino_port.write(command.encode())
# time.sleep(6)
# command = "0 0 1 1"
# arduino_port.write(command.encode())
# 
