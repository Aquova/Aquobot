#!/usr/bin/python
# Requires Python 3.5+ to run
# Written by Austin Bricker, 2017

import discord
import asyncio
import wolframalpha
import json

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
    if message.content.startswith("!help"):
        await client.send_message(message.channel, "http://aquova.github.com/aquobot.html")

    elif message.content.startswith("🔪"):
        await client.send_message(message.channel, ":gun:")

    elif message.content.startswith('!wolfram'):
        q = message.content[9:]
        res = waclient.query(q)
        out = next(res.results).text
        await client.send_message(message.channel, out)

    # if message.content.startswith('!test'):
    #     counter = 0
    #     tmp = await client.send_message(message.channel, 'Calculating messages...')
    #     async for log in client.logs_from(message.channel, limit=100):
    #         if log.author == message.author:
    #             counter += 1
    #
    #     await client.edit_message(tmp, 'You have {} messages.'.format(counter))

    elif message.content.startswith('!alive'):
        if discord.Client.is_logged_in:
            await client.send_message(message.channel, 'Nah.')

    elif message.content.startswith('!echo'):
        tmp = message.content
        tmp = tmp[5:]
        await client.send_message(message.channel, tmp)

    elif message.content.startswith('!power'):
        if message.author.id == ids.get("aquova"):
            await client.send_message(message.channel, 'Yeah, thats coo.')
        else:
            await client.send_message(message.channel, '*NO*')

    elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
        if message.author.id != client.user.id:
            await client.send_message(message.channel, "https://i0.wp.com/www.thekitchenwhisperer.net/wp-content/uploads/2014/04/BelgianWaffles8.jpg")

    elif ("NETHERLANDS" in message.content.upper()) or ("DUTCH" in message.content.upper()):
        await client.send_message(message.channel, ":flag_nl:")

    elif "EXCUSE ME" in message.content.upper():
        await client.send_message(message.channel, "You're excused.")

client.run(discord_key)
