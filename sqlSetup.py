import sqlite3
import csv


def setupDatabase():
    # Create and open Database
    conn = sqlite3.connect('TODO.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE tasks (task text, timeLeft int, priority int, subject text, timeUsed int)''')

    # Open csv File and put data into data base
    with open("TODO_prod.csv", "r") as file:
        todo = csv.DictReader(file)
        for row in todo:
            c.execute(
                'INSERT INTO tasks VALUES (?,?,?,?,?)', (
                          row["task"],
                          int(row["timeLeft"]),
                          int(row["priority"]),
                          row["subject"],
                          int(row["timeUsed"])
                )
            )

    # commit the changes
    conn.commit()

    # close the database after done using it
    conn.close()


if __name__ == '__main__':
    setupDatabase()
