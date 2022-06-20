from pynput import keyboard
# noinspection PyProtectedMember
from pynput.keyboard._xorg import Listener, Controller


def on_activate():
    print('Global hotkey activated!')


def onkeydown(key):
    print('down', key)
    hotkey.press(listener.canonical(key))


def onkeyup(key):
    print('up', key)
    # controller.release(key)
    hotkey.release(listener.canonical(key))


controller: Controller = keyboard.Controller()

hotkey = keyboard.HotKey(keyboard.HotKey.parse('<ctrl>+<alt>+h'), on_activate)
with keyboard.Listener(on_press=onkeydown, on_release=onkeyup, suppress=False) as listener:
    listener: Listener
    listener.join()
