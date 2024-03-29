from collections import defaultdict
import logging
import threading
from random import shuffle
import time

from pynput import keyboard
import sqlite3
from notifypy import Notify


logging.basicConfig(format='%(threadName)s - %(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)



class EventHandler:
    def __init__(self):
        # event flags
        self.go_flag = threading.Event()
        self.n_flag = threading.Event()
        self.quit_flag = threading.Event()

        # time tracking variables
        self.start_time = 0  # a variable that holds the unix time of the most recent unpause
        self.pause_time = int(time.time())  # a variable that holds the unix time of the most recent pause
        self.current_session_time = 0  # a variable that holds time spent on task till the most recent pause
        self.current_split_time = 0  # a variable that holds time since last unpause
        self.dayEnd = calcDayEnd()
        
        self.current_item = {}  # a variable that holds {task, time} exclusive of current session time
        self.today_times = defaultdict(int)  # a variable that holds {task, time} where time is the time spent today, exclusive of current split

        # turn on the database
        self.conn = sqlite3.connect('TODO.db')
        self.db = self.conn.cursor()

        self.list_t = self.refresh_list()

        if len(self.list_t) < 1:
            logging.warning("there is no more items left")
            exit(1)

    def refresh_list(self):
        self.db.execute("SELECT task,timeUsed FROM tasks WHERE priority<=1")

        list_t = self.db.fetchall()
        logging.info("refreshed list from database")
        return [{'task': i[0], 'time': i[1]} for i in list_t]

    def get_s_time(self):
        logging.debug("retrieving s_time")
        if not self.go_flag.is_set() or self.n_flag.is_set():
            logging.debug(f"currently paused, s_time is {self.current_session_time}")
            return self.current_session_time
        if self.start_time == 0:
            logging.debug("start_time is 0, start_time has been set to now")
            self.start_time = int(time.time())
        s_time = self.current_session_time + int(time.time()) - self.start_time
        logging.debug(f"s_time is {s_time}")
        return s_time

    def update_task(self):
        logging.info("updating tasks table")
        s_time = self.get_s_time()
        total_time = self.current_item["time"] + s_time
        logging.debug(f"total time for {self.current_item['task']} is {total_time}")
        self.db.execute("UPDATE tasks SET timeUsed=? WHERE task=?", (total_time, self.current_item["task"]))
        self.conn.commit()

    def reminder(self):
        # reminder notification
        logging.info(f"sending reminder for {self.current_item['task']}")
        s_time = self.get_s_time()
        total_time = self.current_item["time"] + s_time
        logging.debug(f"total time is {total_time}")
        r_notif = Notify()
        r_notif.message = f"{self.current_item['task']}\n"
        logging.debug(f"go flag is {self.go_flag.is_set()}")
        if self.go_flag.is_set():
            r_notif.title = "Stay on task"
            r_notif.message += f"current split: {hours_minutes(self.current_split_time)}\n"
        else:
            r_notif.title = f"Paused: {hours_minutes( int(time.time()) - self.pause_time )}"
        r_notif.message += f"Today: {hours_minutes(self.today_times[self.current_item['task']] + self.current_split_time)}"
        r_notif.send(block=False)

    def update_history(self, end_time):
        # need to open a new object since the obj in self is in a different thread
        logging.info(f"updating history for {self.current_item['task']}")
        logging.debug(f"start time: {self.start_time}, end time: {end_time}")
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
        logging.info("in main loop")
        while not self.n_flag.is_set():
            self.go_flag.wait()
            if self.go_flag.is_set(): # make sure to not undo split reset
                self.current_split_time = int(time.time()) - self.start_time
            time.sleep(0.1)
        logging.debug("exiting main loop")

    def toggle_pause(self):
        p_notif = Notify()
        if self.go_flag.is_set():
            # set up pause notification
            logging.info("pausing " + self.current_item['task'])
            p_notif.title = "Pausing Task..."
            p_notif.message = self.current_item['task']

            # do time calculations and update history
            pause_time = int(time.time())
            self.current_session_time += pause_time - self.start_time
            self.update_history(pause_time)

            self.pause_time = int(time.time())

            self.today_times[self.current_item['task']] += self.current_split_time
            self.current_split_time = 0

            # pause main_loop
            self.go_flag.clear()
        else:
            # set up unpause notification
            logging.info(f"continuing " + self.current_item['task'])
            p_notif.title = "Continuing Task..."
            p_notif.message = f"{self.current_item['task']}\n" + \
                              f"current session: {hours_minutes(self.current_session_time)}"
            if self.current_session_time == 0:
                logging.info("this is the start of a new session")
                p_notif.title = "Starting Task..."
                p_notif.message = self.current_item['task']

            # update start time
            self.start_time = int(time.time())

            # reset split time
            self.current_split_time = 0

            # unpause main_loop
            self.go_flag.set()
        # send notification
        p_notif.send(block=False)

    def next_task(self):
        logging.info("next flag and go flag are set")
        # if the timer is going, trigger pause event before going to next
        if self.go_flag.is_set():
            self.toggle_pause()

        self.n_flag.set()
        self.go_flag.set()


def calcDayEnd():
    time_n = int(time.time())
    timeNow = time.localtime(time_n)
    dayStart = time_n - (timeNow.tm_hour*3600 + timeNow.tm_min*60 + timeNow.tm_sec)
    return dayStart + 3600*24

def r_clock(handler_obj: EventHandler):
    logging.info("started clock")
    t = int(time.time())
    last_reminder = t
    while True:
        if handler_obj.quit_flag.is_set():
            logging.info("breaking out of clock")
            break
        time.sleep(0.5)
        if handler_obj.n_flag.is_set():
            logging.debug("next flag is set, delaying reminder")
            continue

        t = int(time.time())
        if t >= handler_obj.dayEnd:
            logging.info(f"day has ended! {str(handler_obj.today_times)}")
            handler_obj.reminder()
            
            # reset for new day
            handler_obj.dayEnd = calcDayEnd()
            if handler_obj.go_flag.is_set():
                handler_obj.toggle_pause()
            handler_obj.current_split_time = 0
            handler_obj.today_times = defaultdict(int) 

        if (t - last_reminder > 60 and handler_obj.go_flag.is_set()) or (t - last_reminder > 1200):
            handler_obj.reminder()
            last_reminder = t


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
    '<alt>+<ctrl>+b': handler.reminder
}

c_notif = Notify()

with keyboard.GlobalHotKeys(my_hotkeys) as h:
    threading.Thread(target=r_clock, args=(handler,)).start()
    while True:
        shuffle(handler.list_t)
        logging.debug("list shuffled")
        try:
            for i, todo_item in enumerate(handler.list_t):
                # turn off next flag and go to next item
                handler.current_session_time = 0
                handler.start_time = 0
                handler.current_split_time = 0
                logging.debug("current session time and start time set to 0")
                handler.current_item = todo_item
                logging.debug(f"current item is now {todo_item}")
                handler.n_flag.clear()
                handler.go_flag.clear()
                logging.debug("next flag and go flag cleared")

                # coming up notification
                logging.info(f"Coming up... ({i+1}/{len(handler.list_t)})")
                c_notif.title = f"Coming up... ({i+1}/{len(handler.list_t)})"
                c_notif.message = todo_item['task']
                c_notif.send(block=False)

                # start the task loop
                handler.main_loop()
                handler.update_task()
            # refresh list after going through all the tasks
            handler.list_t = handler.refresh_list()
        except KeyboardInterrupt:
            handler.quit_flag.set()
            if handler.start_time == 0:
                logging.debug("haven't started a new task yet, nothing to be saved")
                break
            handler.update_task()
            if handler.go_flag.is_set():
                handler.update_history(int(time.time()))
            handler.conn.close()
            break

