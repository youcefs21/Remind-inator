from pynput import keyboard


def toggle_pause():
    print("pause triggered")


def next_task():
    print("next task triggered")


my_hotkeys = {
    '<ctrl>+<alt>+p': toggle_pause,
    '<ctrl>+<alt>+n': next_task,
}

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    h.join()

