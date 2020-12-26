from random import shuffle
import csv
import time
import os
from threading import Thread
import sqlite3

"""
TODO:
- add a quit option
- mention number of hours if minsLeft > 60
- once all tasks of priority 1 are done, all tasks are move up in priority (2 -> 1, 3 -> 2, etc)
- repeating daily tasks that add on time every time it's a new day
- a move up tag to move up tasks in priority that are just waiting for a prior task 
  to be done but are equally as important
- add due dates and increase the probability of tasks with a higher hoursLeft/TimeTilldueDate
  (if random number above threashold,switch first task with the task that has a higher 
  ratio of hoursLeft/TimeTilldueDate)
"""

stop = True

def stopper():
    global stop
    while input() != "":
        stop = False
    stop = True

	
if __name__ == '__main__':


	# turn on the database
	conn = sqlite3.connect('TODO.db')
	db = conn.cursor()

	db.execute("SELECT task,timeLeft FROM tasks WHERE priority=1")

	listT = db.fetchall()
	listT = [list(i) for i in listT]
	shuffle(listT)

	# tell the user that there are no things to do and end program
	if len(listT) < 1:
		print("there is no more items left")
		exit(1)


	notDone = True
	# while not done all tasks, loop
	while notDone:
		notDone = False
		# go through every task that is not done
		itemIndex = 0
		for item in listT:

			if item[1] > 0:
				doneTask = False

				# ask if the user wants to do the following task
				print("\n\n"+item[0])
				inpt = input("\n\nis it possible to do the task above right now?\n")

				# do the task if the user wants to, otherwise skip
				if inpt == "yes":
					
					# start the stopper if it's not on already
					if stop:
						stop = False
						Thread(target = stopper).start()

					# using a while loop here instead of a for loop because
					# for range() loop doesn't allow me to extend it 
					t = 0
					while t <= item[1]*60:

						# wait one second
						time.sleep(1)

						# big space
						for _ in range(10):
							print("\n")
						
						# calculate time left
						minsLeft = int(((item[1]*60)-t)/60)
						secondsLeft = ((item[1]*60)-t)%60

						# print out how much time left
						print(item[0] + "\n\n" + str(minsLeft) + " mins and "+ str(secondsLeft) + " seconds, press Entre to stop")

						# if Entre was pressed, break
						if stop:
							for _ in range(10):
								print("\n")
							stopOptions = input("press Enter to continue, 'n' for next, and 'd' for done\n\n")

							if stopOptions == "n":
								break
							elif stopOptions == "d":
								doneTask = True
								break
							else:
								stop = False
								Thread(target = stopper).start()

							

						# if time is a mutiple of 5 mins, announce it out loud
						if ((item[1]*60)-t)%300 == 0:
							os.system('spd-say " ' + str((item[1])-int(t/60)) + ' minutes" -i -80 -t child_female')


						


						# if time is up, beeep, and say that out loud
						if (item[1]*60)-t == 0:

							# big space
							for _ in range(10):
								print("\n")

							os.system('play -nq -t alsa synth {} sine {} vol -20dB'.format(1, 440))
							os.system('spd-say "time is up" -i -20 -t child_female')

							print("time is up, press Enter to continue\n\n")

							extraTime = int(input("\n\nenter the number of minutes needed to complete the task, 0 if already complete:\n"))
							
							# adding extraTime, then continue with task
							item[1]+=extraTime

							if extraTime == 0:
								doneTask = True
							else:
								stop = False
								Thread(target = stopper).start()

						t+=1
							
						

					# get current timeUsed and timeLeft
					db.execute("SELECT timeUsed FROM tasks WHERE task=?",(item[0],))
					timeUsed = int(db.fetchone()[0])


					
					# update timeUsed and timeLeft
					timeUsed += listT[itemIndex][1]-minsLeft
					timeLeft = minsLeft

					if doneTask:
						timeLeft = 0
					
					listT[itemIndex][1] = timeLeft

					db.execute("UPDATE tasks SET timeLeft = ?, timeUsed = ? WHERE task=?",(timeLeft,timeUsed,item[0]))


					# commit the changes
					conn.commit()
				
				else:
					# big space
					for _ in range(10):
						print("\n")

				
				
				# if any item still has time in it, keep looping
				notDone = True

			itemIndex+=1

		# reshuffle the list every time we loop through it
		shuffle(listT)


	# close the database after done using it
	conn.close()