# Remind-inator!

**Version Alpha_0.1.3**

For those moments when you really need something to keep you going, behold the Remind-inator!

The goal of this project is to provide a simple tool that forces you to do what needs to be done. 

For me at least, I find it very hard to chose what to do. It can be overwhelming to look at a long to do list and not know where to start. Remind-inator is a helpful tool that helps keep the stress of looking at a to do list far away and focuses on individual tasks, reminding you periodicly what you should be focusing on right now. 

---

## Usage:

#### Step 1:
Fill in the given TODO.csv using a text editor, or upload it into a Google Sheets, and then redownload it after it's filled in
#### Step 2:
Run sqlSetup.py (the filled in TODO.csv must be called exactly that, and must be in the same directory as the sqlSetup.py)
#### Step 3:
In a terminal, `pip install pyttsx3`
#### Step 4:
Run main.py whenever you need to use it. You can pause a task at anytime by pressing Entre in the terminal running main.py. Quit using the quit option when a task is paused.

#### Debugging:
##### linux:
If running main.py returns an error, then `sudo apt update && sudo apt install espeak ffmpeg libespeak1` in a terminal
##### pyttsx3 install error
If you get installation errors , make sure you first upgrade your wheel version using :
`pip install --upgrade wheel`


---

## Change logs

### Alpha_0.1.3:

#### main.py:
- Added: Windows support! 
- Added: Quit option when a task is paused to safely save progress, and terminate the program
- Changed: If the number of minutes left is larger than 60, the program now mentions the number of hours left

#### README.md:
- Added: New debugging section under Usage
- Fixed: Updated outdated information

### Alpha_0.1.2:

#### README.md:
- Fixed: Corrected grammar/orthographic errors

### Alpha_0.1.1:

#### main.py:

- Fixed: Stopper no longer turns on if user skips a task
- Changed: Task is considered over when there are 0 seconds left. Before, it was considered over when there was 1 second left
- Changed: When the user asks for extra time, the task now continues with the additional time instead of proceeding to the next task
- Fixed: The new timeUsed no longer overwrites old timeUsed
- Added: The console now clears after a task is skipped for aesthetic purposes

#### README.md:
- Added: Version number
- Added: Goal of the project
- Added: Usage steps
- Added: Change logs
- Added: Contributors and License & copyright

### Alpha_0.1.0:

#### sqlSetup.py:
- Added: Converts the TODO.csv file into a SQL database

#### main.py:
- Added: Randomly shuffles priority one tasks and gives them to the user one at a time 
- Added: The user has the ability to pause tasks, skip tasks, and mark tasks as complete 
- Added: The user also has the ability to ask for more time if they run out of time

---

## Contributors

- Youcef Boumar (<youcefsboumar@gmail.com>)

---

## License & copyright

© Youcef Boumar
