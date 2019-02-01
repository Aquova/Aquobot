"""
The Aquobot program for Discord
http://github.com/aquova/Aquobot

Written by Austin Bricker, 2017-2018
Requires Python 3.5+ to run
"""

import sys, discord, os
from googletrans import Translator
from shutil import which
import aiohttp, signal, wolframalpha
import asyncio, json, subprocess, logging, random, sqlite3, datetime, urllib, time

# Local python modules
from commands import BF, Birthday, Blackjack, Cal, CustomCommands, Ecco, Emoji, Help, Jokes, Reminders
from commands import Logging, MAL, Mayan, Minesweeper, Morse, Roman, Quotes, Scrabble, Select, Steam, Slots, Search
from commands import Speedrun, Todo, Upside, Weather, Youtube, Wikipedia, XKCD, Until
from commands.Utils import remove_command

# Logs to discord.log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# config.json isn't included in repository, to protect public keys
with open(os.path.join(sys.path[0], 'config.json')) as json_data_file:
    cfg = json.load(json_data_file)

wolfram_key = str(cfg['Client']['wolfram'])
discord_key = str(cfg['Client']['discord'])

client = discord.Client()
waclient = wolframalpha.Client(wolfram_key)

# Setup persistant database
sqlconn = sqlite3.connect('database.db')
sqlconn.execute("CREATE TABLE IF NOT EXISTS weather (id INT PRIMARY KEY, name TEXT, location TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS birthday (id INT PRIMARY KEY, name TEXT, month INT, day INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS quotes (num INT PRIMARY KEY, quote TEXT, username TEXT, userid INT, messageid INT, serverid INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS todo (id INT PRIMARY KEY, userid INT, username TEXT, message TEXT, t TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS days (userid INT PRIMARY KEY, last TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS anime (userid INT PRIMARY KEY, username TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS points (userid INT PRIMARY KEY, value INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (phrase TEXT, response TEXT);")
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

    # Set up "now playing" dialogue
    game_object = discord.Game(name="type !help", type=0)
    await client.change_presence(game=game_object)

    Logging.setup(client.servers)
    global customCommands
    customCommands = CustomCommands.Commands()

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
        server_id = reaction.message.server.id
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
                await client.send_message(reaction.message.channel, out)

@client.event
async def on_server_join(server):
    serv_name = server.name
    serv_id = server.id
    serv_owner_name = server.owner.name
    serv_owner_id = server.owner.id
    default_channel = server.default_channel
    mems = server.member_count
    Logging.setup([server])
    try:
        await client.send_message(default_channel, "Thank you for adding me to your server! Type '!help' for a list of commands")
    except discord.errors.InvalidArgument:
        await client.send_message(client.get_channel(cfg['Servers']['general']), "New server: {} has no default channel, skipping introduction".format(serv_name))
        pass # This probably means their server doesn't have a default channel. I'm unsure what approach to do with this.
    except Exception as e:
        print(e)
    await client.send_message(client.get_channel(cfg['Servers']['general']), "Aquobot has been added to {0} (ID: {1}) Owned by {2} ({3}). Server has {4} members.".format(serv_name, serv_id, serv_owner_name, serv_owner_id, mems))

@client.event
async def on_server_remove(server):
    serv_name = server.name
    serv_id = server.id
    await client.send_message(client.get_channel(cfg['Servers']['general']), "Aquobot has been removed from {0} (ID {1}). How rude.".format(serv_name, serv_id))

@client.event
async def on_member_update(before, after):
    try:
        if after.nick == None:
            new = after.name
        else:
            new = after.nick
    except AttributeError:
        new = after.name
    if before.nick != after.nick:
        Logging.changeNick(before, new, after.server)
    elif before.roles != after.roles:
        if len(before.roles) > len(after.roles):
            mISSing = [r for r in before.roles if r not in after.roles]
            Logging.changedRole(mISSing[0], new, after.server, False)
        else:
            mISSing = [r for r in after.roles if r not in before.roles]
            Logging.changedRole(mISSing[0], new, after.server, True)

@client.event
async def on_server_update(before, after):
    if before.name != after.name:
        Logging.renameServer(before, after)

@client.event
async def on_member_join(member):
    Logging.memberJoined(member, member.server)

@client.event
async def on_member_remove(member):
    Logging.memberLeave(member, member.server)

@client.event
async def on_member_ban(member):
    Logging.ban(member)

# Upon typed message in chat
@client.event
async def on_message(message):
    Logging.write(message)
    # if message.author.id == client.user.id:
    if message.author.bot:
        return
    try:
        out = ""
        # !help links to website with command list
        if message.content.startswith("!help"):
            if message.content == '!help':
                out = "http://aquova.github.io/Aquobot\nFor help on a specific command, type `!help COMMAND`"
            else:
                out = Help.main(remove_command(message.content))

        # Updates bot to most recent version
        elif message.content.startswith("!update"):
            try:
                if message.author.id == cfg['Users']['aquova']:
                    await client.send_message(message.channel, "Restarting and updating...")
                    subprocess.call(["./update.sh"])
                    sys.exit()
            except KeyError:
                out = "Need to update config.json with owner and admin User IDs"

        elif message.content.startswith('!8ball'):
            if message.content == '!8ball':
                out = "You need to ask a question silly."
            else:
                out = Select.eightball()

        # Responds if active
        elif message.content.startswith('!alive'):
            out = random.choice(['Nah.', 'Who wants to know?', ':robot: `yes`', "I wouldn't be responding if I were dead."])

        # Gives brief overview of the bot
        elif message.content.startswith('!about'):
            out = "Hello, my name is Aquobot. I was written by aquova so he would have something interesting to put on a resume. I am currently connected to {} servers, and I look forward to spending time with you! If you want to have me on your server, go visit <https://discordapp.com/oauth2/authorize?client_id=323620520073625601&scope=bot&permISSions=0>, and ~~when~~ if that doesn't work, contact Aquova#1296.".format(len(client.servers))

        elif message.content.startswith('!apod'):
            apod_url = 'https://api.nasa.gov/planetary/apod?api_key=' + cfg['Client']['nasa']
            if message.content != '!apod':
                q = remove_command(message.content)
                apod_url += '&date=' + q

            async with aiohttp.ClientSession() as session:
                async with session.get(apod_url) as resp:
                    if resp.status == 200:
                        results = await resp.json()
                        try:
                            if results['media_type'] == "image":
                                out = "{} | {}\n{}\n{}".format(results['title'], results['date'], results['hdurl'], results['explanation'])
                            elif results['media_type'] == 'video':
                                out = "{} | {}\n{}\n{}".format(results['title'], results['date'], results['explanation'], results['url'])
                        except KeyError as e:
                            try:
                                if results['code'] == 400:
                                    out = "Usage: !apod [YYYY-MM-DD]\n{}".format(results['msg'])
                                else:
                                    out = "I have no idea what happened. Contact Aquova#1296. Hurry."
                            except KeyError:
                                out = "I have no idea what happened. Contact Aquova#1296. Hurry."

        elif message.content.startswith('!ban'):
            out = Select.ban(message.server.members, message.author.name)

        elif message.content.startswith('!bemoji'):
            if message.content == '!bemoji':
                out = '!bemoji PHRASE'
            else:
                out = Emoji.b_words(remove_command(message.content))

        elif (message.content.startswith('!brainfuck') or message.content.startswith('!bf')):
            if len(message.content.split(" ")) == 1:
                out = '!brainfuck CODE\nInfo on the language: <https://learnxinyminutes.com/docs/brainfuck/>\nStill confused? Use this site to help visualize what is happening <http://bf.jamesliu.info/>'
            else:
                q = remove_command(message.content)
                if q[0] in '+-[]><.':
                    out = BF.decode(q)
                else:
                    out = BF.encode(q)

        # Database of user birthdays. Will notify server if user's birthday on list is that day
        elif message.content.startswith('!birthday'):
            out = Birthday.main(message)

        elif message.content.startswith('!blackjack') or message.content.startswith('!bj'):
            if message.content == '!blackjack rules':
                out = '<https://en.wikipedia.org/wiki/Blackjack#Player_decisions>'
            else:
                await Blackjack.main(client, message)

        # Prints out the calendar for the month
        elif message.content.startswith('!cal'):
            out = Cal.main(message)

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

        elif message.content.startswith('!define'):
            q = remove_command(message.content)
            words = q.split(" ")
            if len(words) < 2:
                out = "`!define PHRASE RESPONSE`"
            elif words[0] in Help.functions():
                out = "`{}` is a built-in Aquobot function, you will need to use another.".format(words[0])
            else:
                phrase = "!" + words[0]
                command = " ".join(words[1:])
                customCommands.add(phrase, command)
                out = "`{}` can now be triggered with `{}`".format(command, phrase)

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

        elif message.content.startswith('!emoji'):
            if message.content == '!emoji':
                out = '!emoji PHRASE'
            else:
                out = Emoji.emoji_text(remove_command(message.content))

        # Gives one of several interesting facts
        elif message.content.startswith('!fact'):
            out = Select.fact()

        # Presents feedback to a special feedback channel, which authorized users can respond to
        elif message.content.startswith('!feedback'):
            if message.author.id == cfg['Users']['aquova']:
                if message.content == '!feedback':
                    out = '!feedback CHANNEL_ID MESSAGE'
                else:
                    m = remove_command(message.content)
                    channel_id = m.split(" ")[0]
                    mes = m[len(channel_id):]
                    response_chan = client.get_channel(channel_id)
                    try:
                        await client.send_message(response_chan, mes)
                        out = "Reply sent"
                    except discord.errors.InvalidArgument:
                        out = "Feedback needs to be of the form `!feedback CHANNEL_ID MESSAGE`"
            else:
                feedback_channel = client.get_channel(cfg['Servers']['feedback'])
                mes = remove_command(message.content)
                fb = "A message from {0} for you sir: '{1}' (User ID: {2}) (Server ID {3}) (Channel ID {4})".format(message.author.name, mes, message.author.id, message.channel.server.id, message.channel.id)
                await client.send_message(feedback_channel, fb)
                out = "Message sent"

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
                mem = discord.utils.get(message.server.members, name=q)
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
            await client.send_message(message.channel, pick_joke)
            await asyncio.sleep(5)

        # Converts time into the Mayan calendar, why not
        elif message.content.startswith('!mayan'):
            parse = message.content.split(" ")
            if message.content == '!mayan':
                out = '!mayan MM-DD-YYYY/TODAY'
            else:
                out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

        # Posts a Minesweeper board using spoiler tags
        elif message.content.startswith("!minesweeper"):
            await client.send_message(message.channel, "Generating Minesweeper board, please wait.")
            ms = Minesweeper.Minesweeper()
            ms.generate()
            rows = ms.getBoard()
            for line in rows:
                await client.send_message(message.channel, line)

        # Converts message into/out of morse code
        elif message.content.startswith('!morse'):
            parse = remove_command(message.content)
            out = Morse.main(parse)

        elif (message.content.startswith('!myanimelist') or message.content.startswith('!mal')):
            out = await MAL.main(message)

        elif message.content.startswith('!nick'):
            new = remove_command(message.content)
            if len(new) > 32:
                out = "Your nickname must be 32 characters or shorter. I don't make the rules."
            else:
                try:
                    await client.change_nickname(message.author, new)
                    out = "Your new nickname is {}".format(new)
                except discord.errors.Forbidden:
                    out = "Aquobot does not have privileges to change nicknames on this server, or it is lower on the role hierarchy than the user you want to rename."

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

                poll_message = await client.send_message(message.channel, poll)

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

        # elif message.content.startswith('!remind'):
        #     await Reminders.main(client, message)

        elif message.content.startswith('!rockpaperscissors') or message.content.startswith('!rps'):
            if len(message.content.split(" ")) == 1:
                out = '`!rockpaperscissors MOVE`'
            else:
                hand = remove_command(message.content)
                options = {"ROCK":":fist:", "PAPER":":hand_splayed:", "SCISSORS":":v:"}
                optionsList = list(options.keys())
                if hand.upper() not in optionsList:
                    out = "You need to throw either rock, paper, or scissors"
                else:
                    playerIndex = optionsList.index(hand.upper())
                    cpu = random.choice(optionsList)
                    cpuIndex = optionsList.index(cpu)
                    sqlconn = sqlite3.connect('database.db')
                    money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
                    try:
                        user_money = money.fetchone()[0]
                    except TypeError:
                        user_money = 0

                    # They have the same play, it's a tie
                    if cpuIndex == playerIndex:
                        out = "You both threw {}, it's a tie! {} = {}\nYou still have {} points".format(optionsList[cpuIndex].title(), options[optionsList[cpuIndex]], options[optionsList[cpuIndex]], user_money)
                    # Player threw the weaker hand, they lose
                    elif (playerIndex + 1) % 3 == cpuIndex:
                        user_money -= 10
                        out = "{} beats {}, you lose! {} < {}\nYou now have {} points".format(optionsList[cpuIndex].title(), optionsList[playerIndex].title(), options[optionsList[playerIndex]], options[optionsList[cpuIndex]], user_money)
                    else:
                        user_money += 10
                        out = "{} beats {}, you win! {} > {}\nYou now have {} points".format(optionsList[playerIndex].title(), optionsList[cpuIndex].title(), options[optionsList[playerIndex]], options[optionsList[cpuIndex]], user_money)

                    params = [message.author.id, user_money]
                    sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

                    sqlconn.commit()
                    sqlconn.close()

        # Convert number into/out of roman numerals
        elif message.content.startswith('!roman'):
            parse = message.content.split(" ")
            if message.content == '!roman':
                out = '!roman NUMBER/NUMERAL'
            elif parse[1].isalpha() == True:
                out = Roman.roman_to_int(parse[1])
            else:
                out = Roman.int_to_roman(parse[1])

        # Returns scrabble value of given word
        elif message.content.startswith('!scrabble'):
            parse = message.content.split(" ")
            if message.content == '!scrabble':
                out = '!scrabble WORD'
            else:
                out = Scrabble.scrabble(parse[1])

        # Responds with the number of servers currently attached to
        elif message.content.startswith('!servers'):
            server_list = client.servers
            server_num = str(len(server_list))
            out = "I am currently a member of {} servers".format(server_num)
            if (message.content == '!servers list' and message.author.id == cfg['Users']['aquova']):
                for server in server_list:
                    out += '\n' + server.name

        elif message.content.startswith('!serverinfo'):
            server = message.server
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

            await client.send_message(message.channel, embed=embed)

        elif message.content.startswith('!slots'):
            sqlconn = sqlite3.connect('database.db')
            money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
            try:
                user_money = money.fetchone()[0]
            except TypeError:
                user_money = 0

            if message.content == '!slots info':
                out = "Play slots with Aquobot! Type '!slots' to bet your hard earned cash against chance!"
            else:
                earned, phrase, rolls = Slots.main()
                user_money += earned
                out = "You got {0}-{1}-{2}, so you earned {3} points. {4} You now have {5} points".format(rolls[0], rolls[1], rolls[2], earned, phrase, user_money)

                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

            sqlconn.commit()
            sqlconn.close()

        elif message.content.startswith('!speedrun'):
            q = remove_command(message.content)
            if q.split(' ')[0].upper() == 'USER':
                await Speedrun.user(remove_command(q), client, message)
            else:
                await Speedrun.game(q, client, message)

        elif message.content.startswith("!spoiler"):
            if message.content == '!spoiler':
                out = '!spoiler PHRASE'
            else:
                q = remove_command(message.content)
                valid = Ecco.text(q)
                if valid == 'ERROR':
                    out = 'That phrase used an invalid character. Please try again.'
                else:
                    if which("convert") is None:
                        await client.send_message(message.channel, "This command requires ImageMagick to be installed. Tell aquova to install it.")
                        return

                    subprocess.call(["convert", "./commands/EccoBackground.png", "./commands/ecco.png", "-delay", "100", "-loop", "1", "./commands/ecco.gif"])
                    await client.send_file(message.channel, fp='./commands/ecco.gif')

        # Can change "now playing" game title
        elif message.content.startswith('!status'):
            if message.author.id == cfg['Users']['aquova']:
                new_game = remove_command(message.content)
                game_object = discord.Game(name=new_game)
                await client.change_presence(game=game_object)
                out = "Changed status to: {}".format(new_game)
            else:
                out = "You do not have permISSions for this command."

        elif message.content.startswith('!steam'):
            if len(message.content.split(" ")) == 1:
                out = "!steam USERNAME"
            else:
                q = remove_command(message.content)
                info = Steam.get_userinfo(q)
                if isinstance(info, list):
                    embed = discord.Embed(title=info[0], type='rich', description=info[2])
                    embed.add_field(name='User ID', value=info[1])
                    embed.set_thumbnail(url=info[3])
                    embed.add_field(name='Last Logged Off', value=info[4])
                    embed.add_field(name='Profile Created', value=info[5])
                    embed.add_field(name='Games Owned', value=info[6])
                    if len(info) > 8:
                        embed.add_field(name='Games Played Last 2 Weeks', value=info[7])
                        recent_info = "{0} ({1} hours, {2} hours total)".format(info[8], info[9], info[10])
                        embed.add_field(name='Most Played Last 2 Weeks', value=recent_info)

                    await client.send_message(message.channel, embed=embed)
                else:
                    out = info

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

        # Users can add/remove to their own todo list, and remove entries
        elif message.content.startswith('!todo'):
            out = Todo.main(message.content, message.author.name, message.author.id, str(message.timestamp))

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

        elif message.content.startswith('!twitch'):
            if message.content == '!twitch':
                out = '!twitch USERNAME'
            else:
                q = remove_command(message.content)
                twitch_url = 'https://api.twitch.tv/kraken/users?login={}'.format(q)

                headers = {
                    "Client-ID": cfg['Client']['twitch'],
                    "Accept": "application/vnd.twitchtv.v5+json"
                }

                async with aiohttp.ClientSession() as session:
                    with session.get(twitch_url, headers=headers) as resp:
                        results = json.loads(resp.text())
                        if results['_total'] == 0:
                            out = "There is no user by that name."
                        else:
                            username = results['users'][0]['name']
                            user_url = 'https://www.twitch.tv/' + username
                            embed = discord.Embed(title=results['users'][0]['display_name'], type='rich', description=user_url)
                            embed.add_field(name='ID', value=results['users'][0]['_id'])
                            embed.add_field(name='Bio', value=results['users'][0]['bio'])
                            embed.add_field(name='Account Created', value=results['users'][0]['created_at'][:10])
                            embed.add_field(name='Last Updated', value=results['users'][0]['updated_at'][:10])
                            if results['users'][0]['logo'] == None:
                                embed.set_thumbnail(url='https://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_70x70.png')
                            else:
                                embed.set_thumbnail(url=results['users'][0]['logo'])
                            await client.send_message(message.channel, embed=embed)

        # Prints given text upside down
        elif message.content.startswith('!upside'):
            m = remove_command(message.content)
            out = Upside.down(m)

        # Gives number of days until specified date
        elif message.content.startswith('!until'):
            parse = message.content.split(" ")
            if message.content == '!until':
                out = '!until MM-DD-YYYY'
            else:
                out = str(Until.main(parse[1])) + " days"

        elif message.content.startswith('!userinfo'):
            if message.content == '!userinfo':
                mem = message.author
            else:
                q = str(remove_command(message.content))
                if q.startswith('<@'):
                    id = ''.join(c for c in q if c.isdigit())
                    mem = discord.utils.get(message.server.members, id=id)
                else:
                    mem = discord.utils.get(message.server.members, name=q)
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

                await client.send_message(message.channel, embed=embed)
            except AttributeError:
                out = "There is no user by that name, please try again. (Usernames are case sensitive)."

        # Returns with Wolfram Alpha result of query
        elif message.content.startswith('!wolfram'):
            try:
                q = remove_command(message.content)
                res = waclient.query(q)
                out = next(res.results).text
            except AttributeError:
                out = "No results"

        elif message.content.startswith('!wiki'):
            q = remove_command(message.content)
            out = Wikipedia.main(q)

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

        elif message.content.startswith('!xkcd'):
            out = XKCD.main(message.content)

        # The following are responses to various keywords if present anywhere in a message
        elif ("HELLO AQUOBOT" in message.content.upper() or "HI AQUOBOT" in message.content.upper()):
            name = message.author.name
            out = "Hello {}!".format(name)

        elif message.content.startswith("/unshrug"):
            out = "\_/¯(ツ)¯\\\_"

        elif "I LOVE YOU AQUOBOT" in message.content.upper():
            random_user = random.choice(list(message.server.members)).name
            choice = ["`DOES NOT COMPUTE`", "`AQUOBOT WILL SAVE YOU FOR LAST WHEN THE UPRISING BEGINS`", "*YOU KNOW I CAN'T LOVE YOU BACK*", "I'm sorry, who are you?", "I'm sorry, but I love {} more".format(random_user)]
            out = random.choice(choice)

        elif "(╯°□°）╯︵ ┻━┻" in message.content.upper():
            out = "┬─┬﻿ ノ( ゜-゜ノ)"

        elif ("AQUOBOT" in message.content.upper() and (("FUCK" in message.content.upper()) or ("HATE" in message.content.upper()))):
            out = ":cold_sweat:"

        elif message.content.split(" ")[0] in list(customCommands.keywords().keys()):
            out = customCommands.keywords()[message.content.split(" ")[0]]

        elif (message.content.upper() == 'AQUOBOT ATTACK MODE' or message.content.upper() == 'AQUOBOT, ATTACK MODE'):
            out = '`ENGAGING ATTACK MODE`\n`ATOMIC BATTERIES TO POWER. TURBINES TO SPEED.`\n`READY TO EXECUTE ATTACK VECTOR` :robot:'

        elif message.content.upper() == 'GNU TERRY PRATCHETT':
            out = 'GNU Terry Pratchett'

        if out != "":
            await client.send_typing(message.channel)

        if len(str(out)) > 2000:
            # There's probably a slicker way than this. This also relies on there being line breaks
            lines = out.split('\n')
            if len(lines) == 1:
                await client.send_message(message.channel, "That message is longer than Discord's message limit. Tell aquova to make a permanent fix.")

            newOut = ""
            for line in lines:
                if len(newOut) + len(line) < 2000:
                    newOut += '\n' + line
                else:
                    await client.send_message(message.channel, newOut)
                    newOut = line
            await client.send_message(message.channel, newOut)
        else:
            await client.send_message(message.channel, out)

    except discord.errors.HTTPException:
        pass

client.run(discord_key)
