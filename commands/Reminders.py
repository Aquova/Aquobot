# Functions to remind the user to do a task
# Written by Austin Bricker, 2018

import asyncio, discord
from datetime import timedelta
from commands.Utils import remove_command

class Reminder:
    # Conversion rate into seconds: seconds, minutes, hours, days, weeks, years
    units = [1, 60, 3600, 86400, 604800, 31540000]

    def __init__(self, message):
        self.raw = message
        self.diff = self.calcWaitTime()

    def calcWaitTime(self):
        time = self.raw.split(" ")[0]
        self.message = " ".join(self.raw.split(" ")[1:])
        # Convert the given time into seconds
        vals = time.split(":")
        self.seconds = 0
        for i in range(len(vals)):
            try:
                currUnit = int(vals[::-1][i])
                self.seconds += currUnit * self.units[i]
            except ValueError:
                return None

        return timedelta(seconds=self.seconds)

async def main(client, message):
    delta = Reminder(remove_command(message.content))
    if delta != None:
        await asyncio.sleep(delta.diff.seconds)
        await client.send_message(message.channel, delta.message)
