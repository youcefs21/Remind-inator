import threading
from random import shuffle
import time

from pynput import keyboard
import sqlite3
from notifypy import Notify


class EventHandler:
    def __init__(self):
        self.p_flag = threading.Event()
        self.n_flag = threading.Event()
        self.n_flag.set()
        self.current_item = {}
        self.start_time = 0
        self.current_session_time = 0

        # turn on the database
        self.conn = sqlite3.connect('TODO.db')
        self.db = self.conn.cursor()

        self.list_t = self.refresh_list()

        if len(self.list_t) < 1:
            print("there is no more items left")
            exit(1)

    def refresh_list(self):
        self.db.execute("SELECT task,timeUsed FROM tasks WHERE priority=1")

        list_t = self.db.fetchall()
        return [{'task': i[0], 'timeUsed': i[1]} for i in list_t]

    def update_task(self, updated_task):
        pass

    def update_history(self, end_time):
        pass

    def main_loop(self):
        while self.n_flag.is_set():
            self.p_flag.wait()
            time.sleep(1)

    def toggle_pause(self):
        p_notif = Notify()
        if self.p_flag.is_set():
            # set up pause notification
            p_notif.title = "Pausing Task..."
            p_notif.message = self.current_item['task']

            # do time calculations and update history
            pause_time = int(time.time())
            self.current_session_time += pause_time - self.start_time
            self.update_history(pause_time)

            # pause main_loop
            self.p_flag.clear()
        else:
            # set up unpause notification
            p_notif.title = "Continuing Task..."
            p_notif.message = f"{self.current_item['task']}\n" + \
                              f"current session is {self.current_session_time} seconds long"
            if self.current_session_time == 0:
                p_notif.title = "Starting Task..."
                p_notif.message = self.current_item['task']

            # update start time
            self.start_time = int(time.time())

            # unpause main_loop
            self.p_flag.set()
        # send notification
        p_notif.send(block=False)

    def next_task(self):
        self.n_flag.clear()


handler = EventHandler()

my_hotkeys = {
    '<alt>+p': handler.toggle_pause,
    '<alt>+n': handler.next_task,
}

c_notif = Notify()

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    while True:
        try:
            shuffle(handler.list_t)
            for todo_item in handler.list_t:
                handler.n_flag.set()
                handler.p_flag.clear()
                handler.current_item = todo_item
                c_notif.title = "Coming up..."
                c_notif.message = todo_item['task']
                c_notif.send(block=False)
                print("coming up...", todo_item['task'])
                handler.main_loop()
        except KeyboardInterrupt:
            handler.conn.close()
        time.sleep(1)
