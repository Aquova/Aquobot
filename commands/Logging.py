# Better logging functionality for Aquobot

import os, discord

def setup(servers):
    if not os.path.isdir("logs"):
        os.makedirs("logs")
        # TODO: Add check for if server is edited
        for server in servers:
            folder = "logs/" + server.name
            os.makedirs(folder)
    else:
        for server in servers:
            folder = "logs/" + server.name
            if not os.path.isdir(folder):
                os.makedirs(folder)

def write(message):
    if message.channel.type == discord.ChannelType.text:
        f = "logs/{}/#{}.log".format(message.server.name, message.channel.name)
        with open(f, 'a') as openFile:
            ts = str(message.timestamp).split('.')[0]
            if message.author.nick == None:
                name = message.author.name
            else:
                name = message.author.nick
            openFile.write("{} <{}> {}\n".format(ts, name, message.content))

def changeNick(old, new, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{} is now known as {}\n".format(old, new))

# TODO: These two could probs be combined
def lostRole(role, name, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{} has lost the role {}".format(name, role))

def gainedRole(role, name, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{} has gained the role {}".format(name, role))
