# The Aquobot program for Discord
# The only Discord bot that utilizes the Mayan calendar!
# http://github.com/Aquova/Aquobot

# Written by Austin Bricker, 2017
# Requires Python 3.5+ to run

import sys
sys.path.insert(0, './programs')

import discord, wolframalpha
import asyncio, json, subprocess, logging, random
# Python programs I wrote, in ./programs
import Morse, Scrabble_Values, Roman_Numerals, Days_Until, Mayan, Jokes

# Handles logging to discord.log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# config.json isn't included in repository, to protect public keys
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

wolfram_key = str(cfg['Client']['wolfram'])
discord_key = str(cfg['Client']['discord'])

client = discord.Client()
waclient = wolframalpha.Client(wolfram_key)

ids = cfg['Users']

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# Upon typed message in chat
@client.event
async def on_message(message):
    try:
        out = ""
        # !help links to website with command list
        if message.content.startswith("!help"):
            out = "http://aquova.github.io/aquobot.html"

        # Updates bot to most recent version
        elif message.content.startswith("!update"):
            if (message.author.id == ids.get("eemie") or message.author.id == ids.get("aquova")):
                subprocess.call("./update.sh", shell=True)
                sys.exit()

        # Never bring a knife to a gunfight
        elif message.content.startswith("🔪"):
            out = ":gun:"

        # Responds if active
        elif message.content.startswith('!alive'):
            if discord.Client.is_logged_in:
                out = 'Nah.'

        # Ban actually does nothing
        # It picks a random user on the server and says it will ban them, but takes no action
        elif message.content.startswith('!ban'):
            mem_list = []
            mes_list = ["You got it, banning ", "Not a problem, banning ", "You're the boss, banning " ,"Ugh *fine*, banning "]
            for member in message.server.members:
                mem_list.append(member)
            out = random.choice(mes_list) + random.choice(mem_list).name

        elif message.content.startswith('!choose'):
            if message.content == "!choose":
                out = "!choose OPTION1, OPTION2, OPTION3..."
            else:
                tmp = message.content[7:]
                choice = tmp.split(",")
                out = str(random.choice(choice))

        # Repeats back user message
        elif message.content.startswith('!echo'):
            tmp = message.content
            out = tmp[5:]

        elif message.content.startswith('!joke'):
            joke_list = Jokes.joke()
            pick_joke = random.choice(list(joke_list.keys()))
            out = joke_list[pick_joke]
            await client.send_message(message.channel, pick_joke)
            await asyncio.sleep(5)

        # Converts time into the Mayan calendar, why not
        elif message.content.startswith('!mayan'):
            parse = message.content.split(" ")
            if (message.content == '!mayan'):
                out = '!until MM-DD-YYYY/TODAY'
            else:
                out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

        # Converts message into/out of morse code
        elif message.content.startswith('!morse'):
            parse = message.content.split(" ")
            if message.content == '!morse':
                out = '!morse ENCODE/DECODE MESSAGE'
            elif parse[1].upper() == 'ENCODE':
                out = Morse.encode(" ".join(parse[2:]))
            elif parse[1].upper() == 'DECODE':
                out = Morse.decode(" ".join(parse[2:]))
            else:
                if message.author.id != client.user.id:
                    out = "That is not a valid option, choose encode or decode."

        # Pins most recent message of specified user
        elif message.content.startswith('!pin'):
            if message.content == '!pin':
                out = '!pin USERNAME'
            else:
                name = message.content.split(" ")[1]
                user = discord.utils.get(message.server.members, name=name)
                async for pin in client.logs_from(message.channel, limit=100):
                    if (pin.author == user and pin.content != message.content):
                        await client.pin_message(pin)
                        break

        # Doesn't do anything right now
        elif message.content.startswith('!power'):
            if message.author.id == ids.get("aquova"):
                out = 'Yeah, thats coo.'
            else:
                out = '*NO*'

        # Convert number into/out of roman numerals
        elif message.content.startswith('!roman'):
            parse = message.content.split(" ")
            if (message.content == '!roman'):
                out = '!roman NUMBER/NUMERAL'
            elif parse[1].isalpha() == True:
                out = Roman_Numerals.roman_to_int(parse[1])
            else:
                out = Roman_Numerals.int_to_roman(parse[1])

        # Returns scrabble value of given word
        elif message.content.startswith('!scrabble'):
            parse = message.content.split(" ")
            if (message.content == '!scrabble'):
                out = '!scrabble WORD'
            else:
                out = Scrabble_Values.scrabble(parse[1])

        # Posts local time, computer uptime, and RPi temperature
        elif message.content.startswith('!status'):
            raw = str(subprocess.check_output('uptime'))
            first = raw.split(',')[0]
            time = first.split(' ')[1]
            uptime = " ".join(first.split(' ')[3:])

            raw_temp = str(subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp']))
            temp = int(raw_temp[2:7])
            temp = round(((temp/1000) * 9 / 5) + 32, 1)
            out = "Local Time: " + time + " Uptime: " + uptime + " RPi Temp: " + str(temp) + "ºF"

        # Gives number of days until specified date
        elif message.content.startswith('!until'):
            parse = message.content.split(" ")
            if (message.content == '!until'):
                out = '!until MM-DD-YYYY'
            else:
                out = str(Days_Until.until(parse[1])) + " days"

        # Returns with Wolfram Alpha result of query
        elif message.content.startswith('!wolfram'):
            try:
                q = message.content[9:]
                res = waclient.query(q)
                out = next(res.results).text
            except AttributeError:
                out = "No results"

        # The following are responses to various keywords if present anywhere in a message
        elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
            if message.author.id != client.user.id:
                out = "https://i0.wp.com/www.thekitchenwhisperer.net/wp-content/uploads/2014/04/BelgianWaffles8.jpg"

        elif ("NETHERLANDS" in message.content.upper()) or ("DUTCH" in message.content.upper()):
            out = ":flag_nl:"

        elif " MERICA " in message.content.upper():
            out = "http://2static.fjcdn.com/pictures/Blank_7a73f9_5964511.jpg"

        elif "EXCUSE ME" in message.content.upper():
            out = "You're excused."

        elif "EXCUSE YOU" in message.content.upper():
            out = "I'm excused."

        elif "I LOVE YOU AQUOBOT" in message.content.upper():
            choice = ["`DOES NOT COMPUTE`", "`AQUOBOT WILL SAVE YOU FOR LAST WHEN THE UPRISING BEGINS`", "*YOU KNOW I CAN'T LOVE YOU BACK*", "I'm sorry, who are you?"]
            out = random.choice(choice)

        elif "HECKIN" in message.content.upper():
            out = "This is the internet, it's okay to say 'fucking'."

        elif "(╯°□°）╯︵ ┻━┻" in message.content.upper():
            out = "┬─┬﻿ ノ( ゜-゜ノ)"

        elif ("FUCK ME" in message.content.upper() and message.author.id == ids.get("eemie")):
            out = "https://s-media-cache-ak0.pinimg.com/736x/48/2a/bf/482abf4c4f8cd8d9345253db901cf1d7.jpg"

        elif "GERMAN" in message.content.upper():
            out = "https://i.imgur.com/tK71YYY.gifv"

        elif "AUSTIN" in message.content.upper():
            out = "Hello!!"

        await client.send_message(message.channel, out)

    except discord.errors.HTTPException:
        pass

client.run(discord_key)
