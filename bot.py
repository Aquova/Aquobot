# Unnamed Discord Bot
# Written by aquova, 2019

import asyncio, discord, json, random, sqlite3
import Search

# Read values from config file
with open('private/config.json') as config_file:
    cfg = json.load(config_file)

discordKey = cfg['discord']
client = discord.Client()

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)

"""
On Ready

Occurs when bot is first brought online
"""
@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)

"""
On Message

Occurs when a user posts a message
"""
@client.event
async def on_message(message):
    # Don't react to own messages
    if message.author.id == client.user.id:
        return

    if message.content.startswith('.choose'):
        choices = remove_command(message.content)
        choice = choices.split(",")
        await message.channel.send(str(random.choice(choice)))
    elif message.content.startswith('.g'):
        q = remove_command(message.content)
        out = await Search.google(q)
        await message.channel.send(out)
    elif message.content.startswith('.img'):
        q = remove_command(message.content)
        out = await Search.images(q)
        await message.channel.send(out)
    elif message.content.startswith('.roll'):
        q = remove_command(message.content)
        val = q.split(" ")
        try:
            n = int(val[0])
            die = [x for x in range(n)]
            await message.channel.send(random.choice(die) + 1)
        except ValueError:
            await message.channel.send("That is not a number.")

client.run(discordKey)
