import threading
from random import shuffle
import time

from pynput import keyboard
import sqlite3
from notifypy import Notify


class EventHandler:
    def __init__(self):
        self.go_flag = threading.Event()
        self.n_flag = threading.Event()
        self.current_item = {}  # a variable that holds {task, time} exclusive of current session time
        self.start_time = 0  # a variable that holds the unix time of the most recent unpause
        self.current_session_time = 0  # a variable that holds time spent on task till the most recent pause

        # turn on the database
        self.conn = sqlite3.connect('TODO.db')
        self.db = self.conn.cursor()

        self.list_t = self.refresh_list()

        if len(self.list_t) < 1:
            print("there is no more items left")
            exit(1)

    def refresh_list(self):
        self.db.execute("SELECT task,timeUsed FROM tasks WHERE priority<=1")

        list_t = self.db.fetchall()
        return [{'task': i[0], 'time': i[1]} for i in list_t]

    def get_s_time(self):
        if not self.go_flag.is_set():
            self.start_time = int(time.time())
        return self.current_session_time + int(time.time()) - self.start_time

    def update_task(self):
        s_time = self.get_s_time()
        total_time = self.current_item["time"] + s_time
        self.db.execute("UPDATE tasks SET timeUsed=? WHERE task=?", (total_time, self.current_item["task"]))
        self.conn.commit()

    def reminder(self):
        # reminder notification
        s_time = self.get_s_time()
        total_time = self.current_item["time"] + s_time
        r_notif = Notify()
        if self.go_flag.is_set():
            r_notif.title = "Stay on task"
        else:
            r_notif.title = "Currently Paused..."
        r_notif.message = f"{self.current_item['task']}\n" + \
                          f"current session: {hours_minutes(s_time)} seconds\n" + \
                          f"total time: {hours_minutes(total_time)} seconds"
        r_notif.send(block=False)

    def update_history(self, end_time):
        # need to open a new object since the obj in self is in a different thread
        conn = sqlite3.connect('TODO.db')
        db = conn.cursor()
        db.execute(
            "INSERT INTO history VALUES (?,?,?)",
            (
                self.current_item['task'],
                self.start_time,
                end_time
            )
        )
        conn.commit()
        conn.close()

    def main_loop(self):
        while not self.n_flag.is_set():
            self.go_flag.wait()
            time.sleep(0.1)

    def toggle_pause(self):
        p_notif = Notify()
        if self.go_flag.is_set():
            # set up pause notification
            p_notif.title = "Pausing Task..."
            p_notif.message = self.current_item['task']

            # do time calculations and update history
            pause_time = int(time.time())
            self.current_session_time += pause_time - self.start_time
            self.update_history(pause_time)

            # pause main_loop
            self.go_flag.clear()
        else:
            # set up unpause notification
            p_notif.title = "Continuing Task..."
            p_notif.message = f"{self.current_item['task']}\n" + \
                              f"current session is {hours_minutes(self.current_session_time)} seconds long"
            if self.current_session_time == 0:
                p_notif.title = "Starting Task..."
                p_notif.message = self.current_item['task']

            # update start time
            self.start_time = int(time.time())

            # unpause main_loop
            self.go_flag.set()
        # send notification
        p_notif.send(block=False)

    def next_task(self):
        self.n_flag.set()
        self.go_flag.set()


def r_clock(handler_obj: EventHandler):
    t = int(time.time())
    last_reminder = t
    while True:
        if handler_obj.n_flag.is_set():
            continue

        t = int(time.time())
        if t - last_reminder > 300:
            handler_obj.reminder()
            last_reminder = t

        time.sleep(0.5)


def hours_minutes(total_seconds):
    sec = total_seconds % 60
    mint = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    out = ""
    if hours > 0:
        out += f"{hours} hours, "
    if mint > 0:
        out += f"{mint} minutes, "
    if hours == 0:
        out += f"{sec} seconds"

    return out


handler = EventHandler()

my_hotkeys = {
    '<alt>+<ctrl>+p': handler.toggle_pause,
    '<alt>+<ctrl>+n': handler.next_task,
}

c_notif = Notify()

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    threading.Thread(target=r_clock, args=(handler,)).start()
    try:
        while True:
            shuffle(handler.list_t)
            for todo_item in handler.list_t:
                # turn off next flag and go to next item
                handler.n_flag.clear()
                handler.go_flag.clear()
                handler.current_item = todo_item

                # coming up notification
                c_notif.title = "Coming up..."
                c_notif.message = todo_item['task']
                c_notif.send(block=False)

                # start the task loop
                handler.main_loop()
                handler.update_task()
                handler.current_session_time = 0
            # refresh list after going through all the tasks
            handler.list_t = handler.refresh_list()
    except KeyboardInterrupt:
        handler.update_task()
        handler.conn.close()
