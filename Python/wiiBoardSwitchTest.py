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

    for index, port in enumerate(port_list):
        print "Index: " + str(index) + ", Port: " + str(port.device) + "Description: " + str(port.description)

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
                    leftMass = event.mass.topLeft + event.mass.bottomLeft + .0001
                    rightMass = event.mass.topRight + event.mass.bottomRight + .0001
                    topMass = event.mass.topLeft + event.mass.topRight + .0001
                    bottomMass = event.mass.bottomLeft + event.mass.bottomRight + .0001
                    print "LEFT MASS: " + `leftMass` + " RIGHT MASS: " + `rightMass`
                    leanPercent = 2.5
                    bottomLeanPercent = 5
                    attackPercent = 7
                    attackMaxMass = 15
                    if b == ButtonNames.LEFT_STICK_UP:
                        print "Stopping jump"
                        b = ButtonNames.LEFT_STICK_UP_STOP
                    elif b == ButtonNames.A_PRESS and rightMass > attackMaxMass:
                        b = ButtonNames.A_RELEASE
                        print ("Stopping left attack")
                    elif b == ButtonNames.B_PRESS and leftMass > attackMaxMass:
                        b = ButtonNames.B_RELEASE
                        print "Stopping right attack"
                    elif rightMass < attackMaxMass:
                        b = ButtonNames.A_PRESS
                        print "ATTACK from the LEFT"
                    elif leftMass < attackMaxMass:
                        b = ButtonNames.B_PRESS
                        print "ATTACK from the RIGHT"
                    elif leftMass / rightMass > leanPercent:
                        b = ButtonNames.LEFT_STICK_LEFT
                        print "LEANING LEFT"
                        percentLeaning = 100 - (rightMass / leftMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif rightMass / leftMass > leanPercent:
                        b = ButtonNames.LEFT_STICK_RIGHT
                        print "LEANING RIGHT"
                        percentLeaning = 100 - (leftMass / rightMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif topMass / bottomMass > leanPercent:
                        print "LEANING UP"
                        percentLeaning = 100 - (bottomMass / topMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif bottomMass / topMass > bottomLeanPercent:
                        print "LEANING DOWN"
                        percentLeaning = 100 - (bottomMass / topMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
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
