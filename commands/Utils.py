# Some utility functions for the Aquobot program
# Written by Austin Bricker, 2018

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)