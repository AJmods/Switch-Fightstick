import serial

from serial.tools import list_ports

from pynput import keyboard

isUpPressed = False
isDownPressed = False
isLeftPressed = False
isRightPressed = False

def get_port_from_user():
	port_list = list(list_ports.grep(""))
	if len(port_list) == 0:
		raise LookupError("Unable to detect Serial Device.")
	#index_port_list_str = [f"Index: {index}, Port: {port.device}, Description: {port.description}"
						  # for index, port in enumerate(port_list)]
	#print(index_port_list_str)
	while True:
		ind = input("What port index should be used? ")
		if not (0 <= int(ind) < len(port_list)):
			print("Value given is not an index in the list")
		else:
			return port_list[int(ind)].device

frequency = 2500
duration = 33
ser = serial.Serial(get_port_from_user(),38400)

def on_press(key):
	global isUpPressed
	global isDownPressed
	global isLeftPressed
	global isRightPressed
	try:
		if key.char == b'a':
			b = b'l'
			ser.write(b)
			isRightPressed = True
			print("A PRESSED")
		if key.char == b'w':
			b = b'u'
			ser.write(b)
			isUpPressed = True
			print("W PRESSED")
		if key.char == b's':
			b = b'd'
			ser.write(b)
			isDownPressed = True
			print("S PRESSED")
		if key.char == b'd':
			b = b'r'
			ser.write(b)
			isLeftPressed = True
			print("D PRESSED")
		print (key.char + "IS CHAR PRESSED")
	except:
		print("INVALID KEY")
		if key == keyboard.Key.space:
			b=b'a'
			ser.write(b)
			print("SPACE")
		if key == keyboard.Key.ctrl_l:
			b = b'b'
			ser.write(b)
			print("ctrl_l pressed")
	#if keyboard.key.space:
	#	b='a'
	#	ser.write(b)
		#print("SPACE PRESSED")
	#if keyboard.key.backspace:
	#	b=b'b'
		#ser.write(b)
		#print("BACKSPACE PRESSED")


def onRelease(key):
	print("relaseed")
	global isUpPressed
	global isDownPressed
	global isLeftPressed
	global isRightPressed
	try:
	#	if key.char == b'd' or key.char == b'a' or key.char == b'w' or key.char == b's' :
	#		ser.write(b'z')
	#		print("STOPPED MOVING")
		if key.char == b'a':
			isRightPressed = False
			print("A PRESSED")
		if key.char == b'w':
			isUpPressed = False
			#print("W PRESSED")
		if key.char == b's':
			isDownPressed = False
			#print("S PRESSED")
		if key.char == b'd':
			isLeftPressed = False
			#print("D REPRESSED")
	except:
		print("error")
		if key == keyboard.Key.esc:
			ser.close()
			return False

	try:
		if not isUpPressed and not isDownPressed and not isLeftPressed and not isRightPressed:
			b = b'z'
			ser.write(b)
			print ("STOPPED MOVING")
	except:
		print("UPPRRESSED EROR")

with keyboard.Listener(
        on_press=on_press,
        on_release=onRelease) as listener:
    listener.join()

#try:
    #ser = serial.Serial(get_port_from_user(),38400)
    #while True:
        #input("Type Something")
        #b=b'c'
        #ser.write(b)
        #print("Attepting To Connect")
        #input("type Something to push A")
        #b=b'a'
        #ser.write(b)
        #print("Attepting to push a")
#finally:
    #print("Closing up shop")
