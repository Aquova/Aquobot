# Prints out the calendar for the month
# Written by Austin Bricker, 2017-2018

import platform, discord, subprocess
from Utils import remove_command

# OS X doesn't support -h flag, but Linux requires it, so every command needs a Mac and non-Mac version
def main(message):
    if len(message.content.split(" ")) == 1:
        if platform.system() == "Darwin":
            out = "```bash" + '\n' + subprocess.run(['cal'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
        else:
            out = "```bash" + '\n' + subprocess.run(['cal', '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
    elif len(message.content.split(" ")) == 2:
        try:
            q = int(remove_command(message.content))
            if 0 < q and q <= 12:
                q = str(q) # The cal command requires a string. This is kinda dumb, I know
                if platform.system() == "Darwin":
                    out = "```bash" + '\n' + subprocess.run(['cal', '-m', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                else:
                    out = "```bash" + '\n' + subprocess.run(['cal', '-hm', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
        except ValueError:
            months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
            q = remove_command(message.content)
            if q.upper() in months:
                if platform.system() == "Darwin":
                    out = "```bash" + '\n' + subprocess.run(['cal', '-m', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                else:
                    out = "```bash" + '\n' + subprocess.run(['cal', '-hm', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
            else:
                out = "Usage: !cal"
    else:
        out = "Usage: !cal"

    return out