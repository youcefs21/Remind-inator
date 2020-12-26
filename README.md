# Remind-inator!

**Version Alpha_0.1.1**

for those moments when you really need something to keep you going, behold the Reminder-inator!

The goal of this project is to provide a simple tool that forces you to do what needs to be done. This is my first ever project that I am planning to commit to long term.

---

## Usage:

#### Step 1:
Fill in the given TODO.csv by using a text editor, or uploading it to a google sheet, and then redownload it after it's filled in
#### Step 2:
run sqlSetup.py
#### Step 3:
run main.py when ever you need to use it. There is currently no exit function, so you'll just have to terminate the program during the prompt that asks you if you can do the given task. Terminating at any other point will cause lose in data.

the program is currently meant to be run in a linux terminal, and is not expected to work anywhere else. It will eventually be converted to a website when out of alpha.

---

## Change logs

### Alpha_0.1.1:

#### main.py:

- Fixed: Stopper no longer turns on if user skips a task
- Changed: Task is considered over when there is 0 seconds left, it was 1 seconds left before
- Changed: When the user asks for extra time, the task now continues with the additional time instead of going on to the next task
- Fixed: The new timeUsed no longer overwrites old timeUsed
- Added: The console now clears after a task is skipped because it looks a bit nicer that way

#### README.md:
- Added: Version number
- Added: goal of the project
- Added: usage steps
- Added: change logs
- Added: Contributors and License & copyright

### Alpha_0.1.0:

#### sqlSetup.py:
- Added: converts the TODO.csv file into a SQL database

#### main.py:
- Added: Randomly shuffles priority one tasks and gives them to the user one at a time 
- Added: the user has the ability to pause tasks, skip tasks, and mark tasks as complete 
- Added: the user also has the ability to ask for more time if they run out of time

---

## Contributors

- Youcef Boumar (<youcefsboumar@gmail.com>)

---

## License & copyright

© Youcef Boumar