# Functions to remind the user to do a task
# Written by Austin Bricker, 2018

import discord, asyncio, datetime

class Reminder:
    def __init__(self, author, message):
        self.user = author
        self.message = message

    def calcWaitTime(time, units):
        if units == "SECONDS":
            self.diff = datetime.timedelta(seconds=time)
        elif units == "MINUTES":
            self.diff = datetime.timedelta(minutes=time)
        elif units == "HOURS":
            self.diff = datetime.timedelta(hours=time)
        else:
            self.diff = None

def main(message):
    parse = message.split(" ")
    try:
        timeLength = int(parse[0])
        if parse[1].upper() in ["SECONDS", "MINUTES", "HOURS", "DAYS", "WEEKS"]:
            remind = Reminder(message.author, " ".join(parse[2:]))
            remind.calcWaitTime(timeLength, parse[1].upper())

    except ValueError:
        return "That message was invalid"

