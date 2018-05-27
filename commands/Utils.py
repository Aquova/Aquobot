# Some utility functions for the Aquobot program
# Written by Austin Bricker, 2018

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)

def startswith(phrase, substring):
    subLength = len(substring)
    if len(phrase) < subLength:
        return False
    if substring.upper() == phrase[:subLength].upper():
        return True
    return False
