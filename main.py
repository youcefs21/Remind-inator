import threading
from random import shuffle
import time

from pynput import keyboard
import sqlite3


class EventHandler:
    def __init__(self):
        self.p_flag = threading.Event()
        self.n_flag = threading.Event()
        self.n_flag.set()
        self.current_item = {}

        # turn on the database
        self.conn = sqlite3.connect('TODO.db')
        self.db = self.conn.cursor()

        self.db.execute("SELECT task,timeUsed FROM tasks WHERE priority=1")

        self.list_t = self.db.fetchall()
        self.list_t = [{'task': i[0], 'timeUsed': i[1]} for i in self.list_t]

        # tell the user that there are no things to do and end program
        if len(self.list_t) < 1:
            print("there is no more items left")
            exit(1)

    def main_loop(self):
        while self.n_flag.is_set():
            self.p_flag.wait()
            time.sleep(1)

    def toggle_pause(self):
        if self.p_flag.is_set():
            # pause
            print("paused at: ", int(time.time()))
            #TODO add to history table
            self.p_flag.clear()
        else:
            # unpause
            self.p_flag.set()
            print("started at: ", int(time.time()))

    def next_task(self):
        self.n_flag.clear()


handler = EventHandler()

my_hotkeys = {
    '<ctrl>+<alt>+p': handler.toggle_pause,
    '<ctrl>+<alt>+n': handler.next_task,
}

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    while True:
        try:
            shuffle(handler.list_t)
            for todo_item in handler.list_t:
                handler.n_flag.set()
                handler.p_flag.clear()
                handler.current_item = todo_item
                print("coming up...", todo_item['task'])
                handler.main_loop()
        except KeyboardInterrupt:
            handler.conn.close()
        time.sleep(1)

