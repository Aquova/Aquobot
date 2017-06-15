# The Aquobot program for discord
# http://github.com/Aquova/aquobot

# Written by Austin Bricker, 2017
# Requires Python 3.5+ to run

import sys
sys.path.insert(0, './programs')

import discord, wolframalpha
import asyncio, json, subprocess, logging, random
import Morse, Scrabble_Values, Roman_Numerals, Days_Until

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

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    print(message.author.name + ": " + message.content)
    if message.content.startswith("!help"):
        out = "http://aquova.github.io/aquobot.html"
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith("🔪"):
        out = ":gun:"
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!ban'):
        mem_list = []
        mes_list = ["You got it, banning ", "Not a problem, banning ", "You're the boss, banning " ,"Ugh *fine*, banning "]
        for member in message.server.members:
            mem_list.append(member)
        out = random.choice(mes_list) + random.choice(mem_list).name
        await client.send_message(message.channel, out)

    elif message.content.startswith('!alive'):
        if discord.Client.is_logged_in:
            out = 'Nah.'
            print(out)
            await client.send_message(message.channel, out)

    elif message.content.startswith('!status'):
        raw = str(subprocess.check_output('uptime'))
        first = raw.split(',')[0]
        time = first.split(' ')[0]
        uptime = first.split(' ')[2:]

        raw_temp = str(subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp']))
        temp = int(raw_temp[2:7])
        temp = ((temp/1000) * 9 / 5) + 32
        out = "Local Time: " + time + "Uptime: " + uptime + " Temp: " + str(temp[0:5]) + "ºF"
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!echo'):
        tmp = message.content
        out = tmp[5:]
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!morse'):
        parse = message.content.split(" ")
        if message.content == '!morse':
            out = '!morse ENCODE/DECODE MESSAGE'
        elif parse[1].upper() == 'ENCODE':
            out = Morse.encode(" ".join(parse[2:]))
        elif parse[1].upper() == 'DECODE':
            print(" ".join(parse[2:]))
            out = Morse.decode(" ".join(parse[2:]))
        else:
            if message.author.id != client.user.id:
                out = "That is not a valid option, choose encode or decode."

        await client.send_message(message.channel, out)

    elif message.content.startswith('!pin'):
        if message.content == '!pin':
            await client.send_message(message.channel, '!pin USERNAME')
        else:
            name = message.content.split(" ")[1]
            user = discord.utils.get(message.server.members, name=name)
            async for pin in client.logs_from(message.channel, limit=100):
                if (pin.author == user and pin.content != message.content):
                    await client.pin_message(pin)
                    break

    elif message.content.startswith('!power'):
        if message.author.id == ids.get("aquova"):
            out = 'Yeah, thats coo.'
            print(out)
            await client.send_message(message.channel, out)
        else:
            out = '*NO*'
            print(out)
            await client.send_message(message.channel, out)

    elif message.content.startswith('!roman'):
        parse = message.content.split(" ")
        if (message.content == '!roman'):
            out = '!roman NUMBER/NUMERAL'
        elif parse[1].isalpha() == True:
            out = Roman_Numerals.roman_to_int(parse[1])
        else:
            out = Roman_Numerals.int_to_roman(parse[1])
        await client.send_message(message.channel, out)

    elif message.content.startswith('!scrabble'):
        parse = message.content.split(" ")
        if (message.content == '!scrabble'):
            out = '!scrabble WORD'
        else:
            out = Scrabble_Values.scrabble(parse[1])
        await client.send_message(message.channel, out)

    elif message.content.startswith('!until'):
        parse = message.content.split(" ")
        if (message.content == '!until'):
            out = '!until MM-DD-YYYY'
        else:
            out = str(Days_Until.until(parse[1])) + " days"
        await client.send_message(message.channel, out)

    elif message.content.startswith('!wolfram'):
        q = message.content[9:]
        res = waclient.query(q)
        out = next(res.results).text
        print(out)
        await client.send_message(message.channel, out)

    elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
        if message.author.id != client.user.id:
            out = "https://i0.wp.com/www.thekitchenwhisperer.net/wp-content/uploads/2014/04/BelgianWaffles8.jpg"
            print(out)
            await client.send_message(message.channel, out)

    elif ("NETHERLANDS" in message.content.upper()) or ("DUTCH" in message.content.upper()):
        out = ":flag_nl:"
        print(out)
        await client.send_message(message.channel, out)

    elif "MERICA" in message.content.upper():
        out = "http://2static.fjcdn.com/pictures/Blank_7a73f9_5964511.jpg"
        print(out)
        await client.send_message(message.channel, out)

    elif "EXCUSE ME" in message.content.upper():
        out = "You're excused."
        print(out)
        await client.send_message(message.channel, out)

    elif "EXCUSE YOU" in message.content.upper():
        out = "I'm excused."
        print(out)
        await client.send_message(message.channel, out)

client.run(discord_key)
