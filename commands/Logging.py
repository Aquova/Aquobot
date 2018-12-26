# Logging functionality

import os, discord, datetime

def setup(servers):
    year = datetime.datetime.today().year
    if not os.path.isdir("logs"):
        os.makedirs("logs")
        for server in servers:
            folder = "logs/{}/{}".format(year, server.name)
            os.makedirs(folder)
    else:
        for server in servers:
            try:
                folder = "logs/{}/{}".format(year, server.name)
                if not os.path.isdir(folder):
                    os.makedirs(folder)
            except TypeError: # I'm not sure what causes this tbh
                pass

def renameServer(old, new):
    year = datetime.datetime.today().year
    oldFolder = "logs/{}/{}".format(year, old.name)
    newFolder = "logs/{}/{}".format(year, new.name)
    os.rename(oldFolder, newFolder)
    for channel in new.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, new.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("The server {} has been renamed to {}\n".format(old.name, new.name))

def write(message):
    year = datetime.datetime.today().year
    if message.channel.type == discord.ChannelType.text:
        f = "logs/{}/{}/#{}.log".format(year, message.server.name, message.channel.name)
        ts = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        mes = message.content
        if message.attachments != []:
            for item in message.attachments:
                mes += ' ' + item['url']
        try:
            if message.author.nick == None:
                name = message.author.name
            else:
                name = message.author.nick
        except AttributeError:
            name = message.author.name
        with open(f, 'a', encoding='utf-8') as openFile:
            openFile.write("{} <{}> {}\n".format(ts, name, mes))

def changeNick(old, new, server):
    year = datetime.datetime.today().year
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} is now known as {}\n".format(old.name, old.discriminator, new))

def changedRole(role, name, server, gained):
    year = datetime.datetime.today().year
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, server.name, channel.name)
            with open(f, 'a') as openFile:
                if gained:
                    openFile.write("{} has gained the role {}\n".format(name, role))
                else:
                    openFile.write("{} has lost the role {}\n".format(name, role))

def memberJoined(member, server):
    year = datetime.datetime.today().year
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has joined the server\n".format(member.name, member.discriminator))

def memberLeave(member, server):
    year = datetime.datetime.today().year
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has left the server\n".format(member.name, member.discriminator))

def ban(member):
    year = datetime.datetime.today().year
    for channel in member.server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/{}/#{}.log".format(year, member.server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has been banned.\n".format(member.name, member.discriminator))

