import sqlite3
import csv


def setupDatabase():
    # Create and open Database
    conn = sqlite3.connect('TODO.db')
    c = conn.cursor()

    # Create table
    c.execute("CREATE TABLE tasks (task text, priority int, timeUsed int)")
    c.execute("CREATE TABLE history (task text, startTime int, endTime int)")

    # Open csv File and put data into database
    with open("TODO_prod.csv", "r") as file:
        todo = csv.DictReader(file)
        for row in todo:
            c.execute(
                'INSERT INTO tasks VALUES (?,?,?)', (
                          row["task"],
                          int(row["priority"]),
                          int(row["timeUsed"])
                )
            )

    # commit the changes
    conn.commit()

    # close the database after done using it
    conn.close()


if __name__ == '__main__':
    setupDatabase()
