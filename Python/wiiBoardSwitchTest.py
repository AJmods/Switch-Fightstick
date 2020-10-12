from wiiboard import wiiboard
import pygame
import time
import ButtonNames

import serial

from serial.tools import list_ports


def get_port_from_user():
    port_list = list(list_ports.grep(""))
    if len(port_list) == 0:
        raise LookupError("Unable to detect Serial Device.")
    index_port_list_str
    for index, port in enumerate(port_list):
        print "Index: " + index + ", Port: " + port.device + "Description: " + port.description

    while True:
        ind = input("What port index should be used? ")
        if not (0 <= int(ind) < len(port_list)):
            print("Value given is not an index in the list")
        else:
            return port_list[int(ind)].device


def main():
    ser = serial.Serial(get_port_from_user(), 38400)

    board = wiiboard.Wiiboard()

    pygame.init()

    address = board.discover()
    board.connect(address)  # The wii board must be in sync mode at this time

    time.sleep(0.1)
    board.setLight(True)
    done = False

    leanThreadhold = 20
    bottomLeadThreshhold = 50
    attackNumber = 80

    b = b'z'
    lastB = b'0'

    while not done:
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == wiiboard.WIIBOARD_MASS:
                if event.mass.totalWeight > 10:  # 10KG. otherwise you would get alot of useless small events!
                    print "--Mass event--   Total weight: " + `event.mass.totalWeight` + ". Top left: " + `event.mass.topLeft`
                    leanThreadhold = event.mass.totalWeight / 3.5
                    bottomLeadThreshhold = event.mass.totalWeight / 1.5
                    leftMass = event.mass.topLeft + event.mass.bottomLeft
                    rightMass = event.mass.topRight + event.mass.bottomRight
                    topMass = event.mass.topLeft + event.mass.topRight
                    bottomMass = event.mass.bottomLeft + event.mass.bottomRight
                    if b == ButtonNames.LEFT_STICK_UP:
                        print "Stopping jump"
                        b = ButtonNames.LEFT_STICK_UP_STOP
                    elif leftMass > rightMass + leanThreadhold:
                        print "LEANING LEFT"
                        b = ButtonNames.LEFT_STICK_LEFT
                    elif rightMass > leftMass + leanThreadhold:
                        print "LEANING RIGHT"
                        b = ButtonNames.LEFT_STICK_RIGHT
                    elif topMass > bottomMass + leanThreadhold:
                        print "LEANING UP"
                    elif bottomMass > topMass + bottomLeadThreshhold:
                        print "LEANING DOWN"
                    else:
                        b = ButtonNames.LEFT_STICK_LEFT_STOP
                        print "STOPPING"

                    if event.mass.totalWeight > attackNumber:
                        print "ATTACK"
                else:
                    b = ButtonNames.LEFT_STICK_UP
                    print "JUMPING"
                if lastB != b:
                    ser.write(b)
                    print "State changed, writing " + b + ", lastB: " + lastB
                    lastB = b
                    print ("last b now " + lastB)

                # etc for topRight, bottomRight, bottomLeft. buttonPressed and buttonReleased also available but easier to use in seperate event

            elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
                print "Button pressed!"

            elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
                print "Button released"
                done = True

            # Other event types:
            # wiiboard.WIIBOARD_CONNECTED
            # wiiboard.WIIBOARD_DISCONNECTED

    board.disconnect()
    pygame.quit()


# Run the script if executed
if __name__ == "__main__":
    main()
