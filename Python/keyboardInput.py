from pynput import keyboard

def on_press(key):
    if key.char == b'a' or key.char == b'A':
        print "A PRESSED"


def onRelease(key):
    print("relaseed")
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(
        on_press=on_press,
        on_release=onRelease) as listener:
    listener.join()
