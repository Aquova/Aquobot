# A program that will find out the number of days until a given date, from the current date.
# Written by Austin Bricker, 2015-2017

import datetime

def main(target):
    m = int(target[:2])
    d = int(target[3:5])
    y = int(target[6:10])
    future = datetime.date(y, m, d)
    today = datetime.date.today()

    delta = future - today
    return delta.days
