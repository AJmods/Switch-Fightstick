from wiiboard import wiiboard
import pygame
import time
import ButtonNames


def main():
    board = wiiboard.Wiiboard()

    pygame.init()

    address = board.discover()
    board.connect(address)  # The wii board must be in sync mode at this time

    time.sleep(0.1)
    board.setLight(True)
    done = False

    b = b'z'
    while not done:
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == wiiboard.WIIBOARD_MASS:
		print "--Mass event--   Total weight: " + `event.mass.totalWeight` + ". Top left: " + `event.mass.topLeft`
                if event.mass.totalWeight > 0:  # 10KG. otherwise you would get alot of useless small events!
                    
                    # leanThreadhold = event.mass.totalWeight / 3.5
                    # bottomLeadThreshhold = event.mass.totalWeight / 1.5
                    leanPercent = 1.5
                    attackPercent = 5
                    leftMass = event.mass.topLeft + event.mass.bottomLeft + .001
                    rightMass = event.mass.topRight + event.mass.bottomRight + .001
                    topMass = event.mass.topLeft + event.mass.topRight + .001
                    bottomMass = event.mass.bottomLeft + event.mass.bottomRight + .001

                    if b == ButtonNames.LEFT_STICK_UP:
                        b = b'z'
                        print "Stopping jump"
                    elif leftMass / rightMass > attackPercent:
                        print "ATTACK from the LEFT"
                    elif rightMass / leftMass > attackPercent:
                        print "ATTACK from the LEFT"
                    elif leftMass / rightMass > leanPercent:
                        print "LEANING LEFT"
                        percentLeaning = 100 - (rightMass / leftMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif rightMass / leftMass > leanPercent:
                        print "LEANING RIGHT"
                        percentLeaning = 100 - (leftMass / rightMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif topMass / bottomMass > leanPercent:
                        print "LEANING UP"
                        percentLeaning = 100 - (bottomMass / topMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    elif bottomMass / topMass > leanPercent:
                        print "LEANING DOWN"
                        percentLeaning = 100 - (bottomMass / topMass * 100)
                        print "PERCENT LEANING: " + str(percentLeaning)
                    else:
                        print "STOPPING"

                else:
                    b = ButtonNames.LEFT_STICK_UP
                    print "JUMPING"

                # etc for topRight, bottomRight, bottomLeft. buttonPressed and buttonReleased also available but
                # easier to use in seperate event

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
