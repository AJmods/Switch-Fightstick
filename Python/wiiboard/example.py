import wiiboard
import pygame
import time

def main():
	board = wiiboard.Wiiboard()

	pygame.init()

	address = board.discover()
	board.connect(address) #The wii board must be in sync mode at this time

	time.sleep(0.1)
	board.setLight(True)
	done = False

	leanThreadhold = 20
	bottomLeadThreshhold = 50
	attackNumber = 80

	while (not done):
		time.sleep(0.05)
		for event in pygame.event.get():
			if event.type == wiiboard.WIIBOARD_MASS:
				if (event.mass.totalWeight > 10):   #10KG. otherwise you would get alot of useless small events!
					print "--Mass event--   Total weight: " + `event.mass.totalWeight` + ". Top left: " + `event.mass.topLeft`
					leanThreadhold = event.mass.totalWeight / 3.5
					bottomLeadThreshhold = event.mass.totalWeight / 1.5
					leftMass = event.mass.topLeft + event.mass.bottomLeft
					rightMass = event.mass.topRight + event.mass.bottomRight
					topMass = event.mass.topLeft + event.mass.topRight
					bottomMass = event.mass.bottomLeft + event.mass.bottomRight
					if leftMass > rightMass + leanThreadhold :
						print "LEANING LEFT"
					elif rightMass > leftMass + leanThreadhold :
						print "LEANING RIGHT"
					if topMass > bottomMass + leanThreadhold :
						print "LEANING UP"
					elif bottomMass > topMass + bottomLeadThreshhold :
						print "LEANING DOWN"

					if (event.mass.totalWeight > attackNumber) :
						print "ATTACK"
				else :
					print "JUMPING"

				#etc for topRight, bottomRight, bottomLeft. buttonPressed and buttonReleased also available but easier to use in seperate event

			elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
				print "Button pressed!"

			elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
				print "Button released"
				done = True

			#Other event types:
			#wiiboard.WIIBOARD_CONNECTED
			#wiiboard.WIIBOARD_DISCONNECTED

	board.disconnect()
	pygame.quit()

#Run the script if executed
if __name__ == "__main__":
	main()
