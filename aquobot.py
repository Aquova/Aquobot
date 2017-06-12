#!/usr/bin/python
# Requires Python 3.5+ to run
# Written by Austin Bricker, 2017

import discord
import asyncio
import wolframalpha
import json
import subprocess
import logging

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

    elif message.content.startswith('!wolfram'):
        q = message.content[9:]
        res = waclient.query(q)
        out = next(res.results).text
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!alive'):
        if discord.Client.is_logged_in:
            out = 'Nah.'
            print(out)
            await client.send_message(message.channel, out)

    elif message.content.startswith('!status'):
        raw = str(subprocess.check_output('uptime'))
        uptime = raw.split(',')[0]
        uptime = uptime.split(' ')[-1]

        raw_temp = str(subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp']))
        temp = int(raw_temp[2:7])
        temp = ((temp/1000) * 9 / 5) + 32
        out = "Uptime: " + uptime + " Temp: " + str(temp) + "ºF"
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!echo'):
        tmp = message.content
        out = tmp[5:]
        print(out)
        await client.send_message(message.channel, out)

    elif message.content.startswith('!power'):
        if message.author.id == ids.get("aquova"):
            out = 'Yeah, thats coo.'
            print(out)
            await client.send_message(message.channel, out)
        else:
            out = '*NO*'
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

    elif "EXCUSE ME" in message.content.upper():
        out = "You're excused."
        print(out)
        await client.send_message(message.channel, out)

client.run(discord_key)
