# This is a program that will compare birthday values stored in a SQL table against the current date
# If it's any user's birthday, the program will respond
# Written by Austin Bricker, 2017

import datetime, sqlite3, os

def birthday_check(db_path):
    sqlconn = sqlite3.connect(db_path)
    birthdays = sqlconn.execute("SELECT name, month, day FROM birthday")
    items = birthdays.fetchall()
    d = datetime.date.today()
    month = d.month
    day = d.day
    today_bdays = []
    for i in items:
        try:
            if (month == int(i[1]) and day == int(i[2])):
                today_bdays.append(i)
        except ValueError:
            pass
    return today_bdays
