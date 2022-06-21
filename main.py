import threading
from random import shuffle
import time

from pynput import keyboard
import sqlite3


class EventHandler:
    def __init__(self):
        self.flag = threading.Event()

        # turn on the database
        conn = sqlite3.connect('TODO.db')
        db = conn.cursor()

        db.execute("SELECT task,timeUsed FROM tasks WHERE priority=1")

        list_t = db.fetchall()
        list_t = [list(i) for i in list_t]
        shuffle(list_t)

        # tell the user that there are no things to do and end program
        if len(list_t) < 1:
            print("there is no more items left")
            exit(1)

    def toggle_pause(self):
        if self.flag.is_set():
            self.flag.clear()
        else:
            self.flag.set()

    def next_task(self):
        pass


handler = EventHandler()

my_hotkeys = {
    '<ctrl>+<alt>+p': handler.toggle_pause,
    '<ctrl>+<alt>+n': handler.next_task,
}

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    while True:
        time.sleep(1)

