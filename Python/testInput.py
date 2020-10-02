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
    # index_port_list_str = [f"Index: {index}, Port: {port.device}, Description: {port.description}"
    # for index, port in enumerate(port_list)]
    # print(index_port_list_str)
    while True:
        ind = input("What port index should be used? ")
        if not (0 <= int(ind) < len(port_list)):
            print("Value given is not an index in the list")
        else:
            return port_list[int(ind)].device


frequency = 2500
duration = 33
ser = serial.Serial(get_port_from_user(), 38400)


# write an uppercase letter represents pushing the button, while a lower case button represents releasing a button
# on_press(key) only writes uppercase letters and onRelease(key) only writes lowercase letters

def on_press(key):
    # check keys.  Try loop will catch and go to except if a special key is pressed (Ex. Space, ctrl, shift)
    try:
        if key.char == b'a':
            b = b'L'
            ser.write(b)
            print("A PRESSED")
        if key.char == b'w':
            b = b'U'
            ser.write(b)
            print("W PRESSED")
        if key.char == b's':
            b = b'D'
            ser.write(b)
            print("S PRESSED")
        if key.char == b'd':
            b = b'R'
            ser.write(b)
            print("D PRESSED")
        print (key.char + "IS CHAR PRESSED")
    except:
        print("INVALID KEY")
        if key == keyboard.Key.space:
            b = b'A'
            ser.write(b)
            print("SPACE")
        if key == keyboard.Key.ctrl_l:
            b = b'B'
            ser.write(b)
            print("ctrl_l pressed")
        if key == keyboard.Key.enter:
            b = b'c'
            ser.write(b)
            print("ENTER PRESSED")


def onRelease(key):
    # check keys.  Try loop will catch and go to except if a special key is pressed (Ex. Space, ctrl, shift)
    print("released")
    try:
        if key.char == b'a':
            b = b'l'
            ser.write(b)
            print("A RELEASED")
        if key.char == b'w':
            b = b'u'
            ser.write(b)
            print("W RELEASED")
        if key.char == b's':
            b = b'd'
            ser.write(b)
            print("S RELEASED")
        if key.char == b'd':
            b = b'r'
            ser.write(b)
            print("D RELEASED")
    except:
        print("INVALID KEY")
        if key == keyboard.Key.space:
            b = b'a'
            ser.write(b)
            print("SPACE RELEASED")
        if key == keyboard.Key.ctrl_l:
            b = b'b'
            ser.write(b)
            print("ctrl_l RELEASED")
        if key == keyboard.Key.esc:
            b=b'z'
            ser.write(b)
            print("Quiting")
            quit()


with keyboard.Listener(
        on_press=on_press,
        on_release=onRelease) as listener:
    listener.join()

# try:
# ser = serial.Serial(get_port_from_user(),38400)
# while True:
# input("Type Something")
# b=b'c'
# ser.write(b)
# print("Attepting To Connect")
# input("type Something to push A")
# b=b'a'
# ser.write(b)
# print("Attepting to push a")
# finally:
# print("Closing up shop")
