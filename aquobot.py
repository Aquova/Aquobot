"""
The Aquobot program for Discord
http://github.com/aquova/Aquobot

Written by Austin Bricker, 2017-2020
"""

import sys, discord, os
# from googletrans import Translator
import asyncio, json, subprocess, random, sqlite3, datetime, time

# Local python modules
from commands import Birthday, Blackjack, Ecco, Jokes
from commands import Minesweeper, Quotes, Select, Search
# from commands import Weather, Youtube
from commands.Utils import remove_command

# config.json isn't included in repository, to protect public keys
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

discord_key = str(cfg['Client']['discord'])

client = discord.Client()

# Setup persistant database
sqlconn = sqlite3.connect('database.db')
sqlconn.execute("CREATE TABLE IF NOT EXISTS weather (id INT PRIMARY KEY, name TEXT, location TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS birthday (id INT PRIMARY KEY, name TEXT, month INT, day INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS quotes (num INT PRIMARY KEY, quote TEXT, username TEXT, userid INT, messageid INT, serverid INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS points (userid INT PRIMARY KEY, value INT);")
sqlconn.commit()
sqlconn.close()

num_emoji = {0: "0⃣", 1:"1⃣", 2:"2⃣", 3:"3⃣", 4:"4⃣", 5:"5⃣", 6:"6⃣", 7:"7⃣", 8:"8⃣", 9:"9⃣"}

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    dateCheck = datetime.time(7, 0) # Check for birthday everyday at 7 AM
    diff = datetime.timedelta(hours=24) - (datetime.datetime.combine(datetime.date.min, datetime.datetime.now().time()) - datetime.datetime.combine(datetime.date.min, dateCheck))
    await asyncio.sleep(diff.seconds)
    while True:
        print("Checking birthday")
        await Birthday.check_birthday(client)
        print("Done checking, now sleeping.")
        await asyncio.sleep(86400) # Sleep for 24 hours

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '💬':
        user_name = reaction.message.author.name
        user_id = reaction.message.author.id
        mes = reaction.message.content
        if reaction.message.attachments != []:
            for item in reaction.message.attachments:
                mes += '\n' + item['url']
        server_id = reaction.message.guild.id
        if mes != "":
            mes_id = int(reaction.message.id)
            sqlconn = sqlite3.connect('database.db')
            repeat_check = sqlconn.execute("SELECT num FROM quotes WHERE messageid=?", [mes_id])
            try:
                repeat = repeat_check.fetchone()[0]
                sqlconn.close()
            except TypeError:
                count = sqlconn.execute("SELECT COUNT(*) FROM quotes")
                num = count.fetchone()[0]
                params = (num + 1, mes, user_name, user_id, mes_id, server_id)
                sqlconn.execute("INSERT INTO quotes (num, quote, username, userid, messageid, serverid) VALUES (?, ?, ?, ?, ?, ?)", params)
                sqlconn.commit()
                sqlconn.close()
                out = 'Quote added by {}: "{}" ~{}. (#{})'.format(user.name, mes, user_name, str(num + 1))
                await reaction.message.channel.send(out)

# Upon typed message in chat
@client.event
async def on_message(message):
    if message.author.bot:
        return
    try:
        out = ""
        # Updates bot to most recent version
        if message.content.startswith("!update"):
            try:
                if message.author.id == cfg['Users']['aquova']:
                    await message.channel.send("Restarting and updating...")
                    subprocess.call(["./update.sh"])
                    sys.exit()
            except KeyError:
                out = "Need to update config.json with owner and admin User IDs"

        # Responds if active
        elif message.content.startswith('!alive'):
            out = random.choice(['Nah.', 'Who wants to know?', ':robot: `yes`', "I wouldn't be responding if I were dead."])

        elif message.content.startswith('!ban'):
            out = Select.ban(message.guild.members, message.author.name)

        # Database of user birthdays. Will notify server if user's birthday on list is that day
        elif message.content.startswith('!birthday'):
            out = Birthday.main(message)

        elif message.content.startswith('!blackjack') or message.content.startswith('!bj'):
            if message.content == '!blackjack rules':
                out = '<https://en.wikipedia.org/wiki/Blackjack#Player_decisions>'
            else:
                await Blackjack.main(client, message)

        # Chooses between given options
        elif message.content.startswith('!choose'):
            if message.content == "!choose":
                out = "!choose OPTION1, OPTION2, OPTION3..."
            else:
                tmp = remove_command(message.content)
                choice = tmp.split(",")
                out = str(random.choice(choice))

        elif (message.content.startswith('!deletethis') or message.content.startswith('!dt')):
            out = 'https://cdn.discordapp.com/attachments/214906642741854210/353702529277886471/delete_this.gif'

        # Responds with .png image of text in "Ecco the Dolphin" style
        elif message.content.startswith('!ecco'):
            if message.content == '!ecco':
                out = '!ecco PHRASE'
            else:
                q = remove_command(message.content)
                valid = Ecco.text(q)
                if valid == 'ERROR':
                    out = 'That phrase used an invalid character. Please try again.'
                else:
                    await client.send_file(message.channel, fp='./commands/ecco.png')

        # Repeats back user message
        elif message.content.startswith('!echo'):
            out = remove_command(message.content)

        elif message.content.startswith('!fw'):
            out = "There's no !fw command, quit asking."

        # Tells a 7 day forecast based on user or location. Uses same database as weather
        elif (message.content.startswith('!forecast') or message.content.startswith('!f')):
            sqlconn = sqlite3.connect('database.db')
            author_id = int(message.author.id)
            author_name = message.author.name
            if (message.content == '!forecast' or message.content == '!f'):
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                try:
                    query_location = user_loc.fetchone()[0]
                    out = Weather.forecast(query_location)
                except TypeError:
                    out = "!forecast [set] LOCATION"
            elif message.content.startswith("!forecast set"):
                q = message.content[13:]
                params = (author_id, author_name, q)
                sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                out = "Location set as %s" % q
            else:
                try:
                    q = remove_command(message.content)
                    out = Weather.forecast(q)
                except TypeError:
                    out = "No location found. Please be more specific."
            sqlconn.commit()
            sqlconn.close()

        # Same as !forecast, but responds with emojis
        elif message.content.startswith('!qf'):
            sqlconn = sqlite3.connect('database.db')
            author_id = int(message.author.id)
            author_name = message.author.name
            if message.content == '!qf':
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                try:
                    query_location = user_loc.fetchone()[0]
                    out = Weather.emoji_forecast(query_location)
                except TypeError:
                    out = "!qf [set] LOCATION"
            elif message.content.startswith("!qf set"):
                q = message.content[7:]
                params = (author_id, author_name, q)
                sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                out = "Location set as %s" % q
            else:
                try:
                    q = remove_command(message.content)
                    out = Weather.emoji_forecast(q)
                except TypeError:
                    out = "No location found. Please be more specific."
            sqlconn.commit()
            sqlconn.close()

        elif message.content.startswith('!getavatar'):
            if len(message.content.split(" ")) == 1:
                out = message.author.avatar_url.replace("webp", "png")
            else:
                q = remove_command(message.content)
                mem = discord.utils.get(message.guild.members, name=q)
                try:
                    out = mem.avatar_url.replace("webp", "png")
                except AttributeError:
                    out = "There is no user by that name, please try again. (Usernames are case sensitive)."

        elif message.content.startswith('!g') or message.content.startswith("!google"):
            if len(message.content) == 1:
                out = "!g QUERY"
            else:
                q = remove_command(message.content)
                out = await Search.google(q)

        elif message.content.startswith('!img'):
            if message.content == '!img':
                out = "!img QUERY"
            else:
                q = remove_command(message.content)
                out = await Search.images(q)

        # Tells a joke from a pre-programmed list
        elif message.content.startswith('!joke'):
            joke_list = Jokes.joke()
            pick_joke = random.choice(list(joke_list.keys()))
            out = joke_list[pick_joke]
            await message.channel.send(pick_joke)
            await asyncio.sleep(5)

        # Posts a Minesweeper board using spoiler tags
        elif message.content.startswith("!minesweeper"):
            await message.channel.send("Generating Minesweeper board, please wait.")
            ms = Minesweeper.Minesweeper()
            ms.generate()
            rows = ms.getBoard()
            for line in rows:
                await message.channel.send(line)

        # Produces a poll where users can vote via reactions
        elif message.content.startswith('!poll'):
            if message.content == "!poll":
                out = "!poll TITLE, OPTION1, OPTION2, OPTION3..."
            else:
                tmp = remove_command(message.content)
                options = tmp.split(",")
                num = len(options) - 1
                i = 0
                poll = options[0] + '\n'
                for item in options[1:]:
                    i += 1
                    poll = poll + str(i) + ". " + item + '\n'

                poll_message = await message.channel.send(poll)

                for j in range(1, num + 1):
                    await client.add_reaction(poll_message, num_emoji[j])

                out = "Vote now!!"

        elif message.content.startswith('!points'):
            sqlconn = sqlite3.connect('database.db')
            money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
            try:
                user_money = money.fetchone()[0]
            except TypeError:
                user_money = 0

            out = "You have {} points".format(user_money)

            sqlconn.commit()
            sqlconn.close()

        # Users can add quotes to a database, and recall a random one
        elif message.content.startswith('!quote'):
            out = Quotes.main(message)

        # Responds with the number of servers currently attached to
        elif message.content.startswith('!servers'):
            server_list = client.servers
            server_num = str(len(server_list))
            out = "I am currently a member of {} servers".format(server_num)
            if (message.content == '!servers list' and message.author.id == cfg['Users']['aquova']):
                for server in server_list:
                    out += '\n' + server.name

        elif message.content.startswith('!serverinfo'):
            server = message.guild
            name = server.name
            serv_id = server.id
            embed = discord.Embed(title=name, type='rich', description=serv_id)
            owner = server.owner.name
            created = server.created_at.strftime('%B %d, %Y %I:%M %p')
            if server.icon_url != "":
                icon = server.icon_url
                embed.set_thumbnail(url=icon)
            mem_count = server.member_count
            roles = server.role_hierarchy
            channel_count = sum(1 for _ in server.channels)
            region = server.region

            embed.add_field(name='Owner', value=owner)
            embed.add_field(name='Server Created', value=created)
            embed.add_field(name='Server Region', value=region)
            embed.add_field(name='Number of Members', value=mem_count)
            embed.add_field(name='Number of Channels', value=channel_count)
            embed.add_field(name='Number of Roles', value=len(roles))

            await message.channel.send(embed=embed)

        # Can change "now playing" game title
        elif message.content.startswith('!status'):
            if message.author.id == cfg['Users']['aquova']:
                new_game = remove_command(message.content)
                game_object = discord.Game(name=new_game)
                await client.change_presence(game=game_object)
                out = "Changed status to: {}".format(new_game)
            else:
                out = "You do not have permISSions for this command."

        elif message.content.startswith('!stop'):
            out = Select.stop()

        # Doesn't do anything right now, simply for testing
        elif message.content.startswith('!test'):
            if message.author.id == cfg['Users']['aquova']:
                out = "Yeah, sure, alright."
            else:
                out = '*NO*'

        # Displays the time for a user or location. Uses same database as weather
        elif message.content.startswith('!time'):
            sqlconn = sqlite3.connect('database.db')
            author_id = int(message.author.id)
            author_name = message.author.name
            if message.content == '!time':
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                try:
                    query_location = user_loc.fetchone()[0]
                    out = Weather.time(query_location)
                except TypeError:
                    out = "!time [set] LOCATION"
            elif message.content.startswith("!time set"):
                q = message.content[9:]
                params = (author_id, author_name, q)
                sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                out = "Location set as %s" % q
            else:
                q = remove_command(message.content)
                out = Weather.time(q)
            sqlconn.commit()
            sqlconn.close()

        elif (message.content.startswith('!tr') or message.content.startswith('!translate')):
            if (message.content == '!tr' or message.content == '!translate'):
                out = '!tr SOURCE_LANG MESSAGE'
            else:
                try:
                    dest_lang = message.content.split(" ")[1]
                    text = " ".join(message.content.split(" ")[2:])
                    if text == '^':
                        async for mes in client.logs_from(message.channel, limit=10):
                            if mes.content != message.content:
                                text = mes.content
                                break
                    tr = Translator()
                    new = tr.translate(text, dest=dest_lang)
                    out = new.text
                except ValueError:
                    out = "Invalid destination language."

        elif message.content.startswith('!userinfo'):
            if message.content == '!userinfo':
                mem = message.author
            else:
                q = str(remove_command(message.content))
                if q.startswith('<@'):
                    id = ''.join(c for c in q if c.isdigit())
                    mem = discord.utils.get(message.guild.members, id=id)
                else:
                    mem = discord.utils.get(message.guild.members, name=q)
            try:
                username = mem.name + '#' + mem.discriminator
                created = mem.created_at.strftime('%B %d, %Y %I:%M %p')
                joined = mem.joined_at.strftime('%B %d, %Y %I:%M %p')
                if mem.avatar_url == "":
                    avatar = mem.default_avatar_url
                else:
                    avatar = mem.avatar_url
                roles = []
                for item in mem.roles:
                    roles.append(item.name)
                roles = ', '.join(roles)

                if mem.name != mem.display_name:
                    nickname = mem.display_name
                else:
                    nickname = ' '

                embed = discord.Embed(title=username, type='rich', description=nickname, color=mem.color)
                embed.add_field(name='Joined Server', value=joined)
                embed.add_field(name='Account Created', value=created)
                embed.add_field(name='User ID', value=mem.id)
                embed.add_field(name='Beep Boop?', value=mem.bot)
                embed.add_field(name='Server Roles', value=roles)
                embed.set_thumbnail(url=avatar)

                await client.send(message.channel, embed=embed)
            except AttributeError:
                out = "There is no user by that name, please try again. (Usernames are case sensitive)."

        # Returns with the weather of a specified location
        # Needs to be the last 'w' command
        elif (message.content.startswith('!weather') or message.content.startswith('!w')):
            sqlconn = sqlite3.connect('database.db')
            author_id = int(message.author.id)
            author_name = message.author.name
            if (message.content == '!weather' or message.content == '!w'):
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                try:
                    query_location = user_loc.fetchone()[0]
                    out = Weather.main(query_location)
                except TypeError:
                    out = "!weather [set] LOCATION"
            elif (message.content.startswith("!weather set") or message.content.startswith('!w set')):
                tmp = message.content.split(" ")[2:]
                q = " ".join(tmp)
                params = (author_id, author_name, q)
                sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                out = "Location set as %s" % q
            else:
                try:
                    q = remove_command(message.content)
                    out = Weather.main(q)
                except TypeError:
                    out = "No location found. Please be more specific."
            sqlconn.commit()
            sqlconn.close()

        # Same as !weather, but prints emojis
        elif message.content.startswith('!qw'):
            sqlconn = sqlite3.connect('database.db')
            author_id = int(message.author.id)
            author_name = message.author.name
            if message.content == '!qw':
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                try:
                    query_location = user_loc.fetchone()[0]
                    out = Weather.emoji_weather(query_location)
                except TypeError:
                    out = "!qw [set] LOCATION"
            elif message.content.startswith("!qw set"):
                q = message.content[7:]
                params = (author_id, author_name, q)
                sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                out = "Location set as %s" % q
            else:
                q = remove_command(message.content)
                out = Weather.emoji_weather(q)
            sqlconn.commit()
            sqlconn.close()

        elif (message.content.startswith('!youtube') or message.content.startswith('!yt')):
            q = remove_command(message.content)
            out = Youtube.search(q)

        if len(str(out)) > 2000:
            # There's probably a slicker way than this. This also relies on there being line breaks
            lines = out.split('\n')
            if len(lines) == 1:
                await message.channel.send("That message is longer than Discord's message limit. Tell aquova to make a permanent fix.")

            newOut = ""
            for line in lines:
                if len(newOut) + len(line) < 2000:
                    newOut += '\n' + line
                else:
                    await message.channel.send(newOut)
                    newOut = line
            await message.channel.send(newOut)
        else:
            await message.channel.send(out)

    except discord.errors.HTTPException:
        pass

client.run(discord_key)
