"""
The Aquobot program for Discord
The only Discord bot that utilizes the Mayan calendar!
http://github.com/Aquova/Aquobot

Written by Austin Bricker, 2017
Requires Python 3.5+ to run
"""

import sys
sys.path.insert(0, './commands')

import discord
from googletrans import Translator
from google import google
# from bs4 import BeautifulSoup
import lxml.etree as ET
import requests, aiohttp, signal, wolframalpha, async_timeout
import asyncio, json, subprocess, logging, random, sqlite3, datetime, urllib, time

# Python programs I wrote, in ./commands
import Morse, Scrabble, Roman, Days_Until, Mayan, Jokes, Weather, Birthday, Emoji, Help, Quotes, MAL, Blackjack, Speedrun
import Upside, Ecco, Select, Youtube, Steam, Whatpulse, Slots, xkcd, Wikipedia, iss, Todo, BF, Roulette, Braille #, Weather2

# Logs to discord.log
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

sqlconn = sqlite3.connect('database.db')
sqlconn.execute("CREATE TABLE IF NOT EXISTS weather (id INT PRIMARY KEY, name TEXT, location TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS birthday (id INT PRIMARY KEY, name TEXT, month TEXT, day INT, server_id INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS quotes (num INT PRIMARY KEY, quote TEXT, username TEXT, userid INT, messageid INT, serverid INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS todo (id INT PRIMARY KEY, userid INT, username TEXT, message TEXT, t TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS days (userid INT PRIMARY KEY, last TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS whatpulse (userid INT PRIMARY KEY, username TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS anime (userid INT PRIMARY KEY, username TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS points (userid INT PRIMARY KEY, value INT);")
sqlconn.commit()
sqlconn.close()

num_emoji = {0: "0⃣", 1:"1⃣", 2:"2⃣", 3:"3⃣", 4:"4⃣", 5:"5⃣", 6:"6⃣", 7:"7⃣", 8:"8⃣", 9:"9⃣"}

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    game_object = discord.Game(name="type !help", type=0)
    await client.change_presence(game=game_object)

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
                out = 'Quote added from {0}: "{1}". (#{2})'.format(user_name, mes, str(num + 1))
                await client.send_message(reaction.message.channel, out)
    elif (reaction.emoji == '📌' or reaction.emoji == '📍'):
        try:
            await client.pin_message(reaction.message)
        except discord.errors.HTTPException as e:
            await client.send_message(reaction.message.channel, e) # If max pin limit has been reached

@client.event
async def on_server_join(server):
    serv_name = server.name
    serv_id = server.id
    serv_owner_name = server.owner.name
    serv_owner_id = server.owner.id
    default_channel = server.default_channel
    mems = server.member_count
    await client.send_message(default_channel, "Thank you for adding me to your server! Type '!help' for a list of commands")
    await client.send_message(client.get_channel(cfg['Servers']['general']), "Aquobot has been added to {0} (ID: {1}) Owned by {2} ({3}). Server has {4} members.".format(serv_name, serv_id, serv_owner_name, serv_owner_id, mems))

@client.event
async def on_server_remove(server):
    serv_name = server.name
    serv_id = server.id
    await client.send_message(client.get_channel(cfg['Servers']['general']), "Aquobot has been removed from {0} (ID {1}). How rude.".format(serv_name, serv_id))

# Upon typed message in chat
@client.event
async def on_message(message):
    if message.author.id != client.user.id:
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
                    if (message.author.id == cfg['Users']['eemie'] or message.author.id == cfg['Users']['aquova']):
                        await client.send_message(message.channel, "Restarting and updating...")
                        subprocess.call("./update.sh", shell=True)
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
                server_list = client.servers
                server_num = str(len(server_list))
                aquo_link = "<https://discordapp.com/oauth2/authorize?client_id=323620520073625601&scope=bot&permissions=1278733377>"
                out = "Hello, my name is Aquobot. I was written in Python by Aquova so he would have something interesting to put on a resume. I am currently connected to {0} servers, and I look forward to spending time with you! If you want to have me on your server, go visit {1}, and ~~when~~ if that doesn't work, contact Aquova#1296.".format(server_num, aquo_link)

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
                                elif results['media_type'] =='video':
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
                    if (q[0] in '+-[]><.'):
                        out = BF.decode(q)
                    else:
                        out = BF.encode(q)

            # Work in progress
            elif message.content.startswith("!braille"):
                q = remove_command(message.content)
                out = Braille.main(q)

            # Database of user birthdays. Will notify server if user's birthday on list is that day
            elif message.content.startswith('!birthday'):
                out = Birthday.main(message)

            elif message.content.startswith('!blackjack'):
                if message.content == '!blackjack rules':
                    out = '<https://en.wikipedia.org/wiki/Blackjack#Player_decisions>'
                else:
                    await Blackjack.main(client, message)

            # Prints out the calendar for the month
            elif message.content.startswith('!cal'):
                # OS X doesn't support -h flag, but Linux requires it, so every command needs a Mac and non-Mac version
                import platform
                if len(message.content.split(" ")) == 1:
                    if (platform.system() == "Darwin"):
                        out = "```bash" + '\n' + subprocess.run(['cal'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                    else:
                        out = "```bash" + '\n' + subprocess.run(['cal', '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                elif len(message.content.split(" ")) == 2:
                    try:
                        q = int(remove_command(message.content))
                        if 0 < q and q <= 12:
                            q = str(q) # The cal command requires a string. This is kinda dumb, I know
                            if (platform.system() == "Darwin"):
                                out = "```bash" + '\n' + subprocess.run(['cal', '-m', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                            else:
                                out = "```bash" + '\n' + subprocess.run(['cal', '-hm', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                    except ValueError:
                        months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
                        q = remove_command(message.content)
                        if q.upper() in months:
                            if (platform.system() == "Darwin"):
                                out = "```bash" + '\n' + subprocess.run(['cal', '-m', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                            else:
                                out = "```bash" + '\n' + subprocess.run(['cal', '-hm', q], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
                        else:
                            out = "Usage: !cal"
                else:
                    out = "Usage: !cal"

            # Chooses between given options
            elif message.content.startswith('!choose'):
                if message.content == "!choose":
                    out = "!choose OPTION1, OPTION2, OPTION3..."
                else:
                    tmp = remove_command(message.content)
                    choice = tmp.split(",")
                    out = str(random.choice(choice))

            # This one is for me and eemie
            elif message.content.startswith('!days'):
                if message.server.id == cfg['Servers']['Brickhouse']:
                    if (message.author.id == cfg['Users']['eemie'] or message.author.id == cfg['Users']['aquova']):
                        sqlconn = sqlite3.connect('database.db')
                        today = datetime.date.today()
                        if message.content == '!days reset':
                            params = [message.author.id, today]
                            sqlconn.execute("INSERT OR REPLACE INTO days (userid, last) VALUES (?, ?)", params)
                            out = "Date updated, you sly dog :smirk:"
                        elif message.content.startswith('!days reset'):
                            target = " ".join(message.content.split(" ")[2:])
                            # MM/DD/YYYY
                            m = int(target[:2])
                            d = int(target[3:5])
                            y = int(target[6:10])
                            day = datetime.date(y, m, d)
                            params = [message.author.id, day]
                            sqlconn.execute("INSERT OR REPLACE INTO days (userid, last) VALUES (?, ?)", params)
                            out = "Date updated, you sly dog :smirk:"
                        else:
                            last_day = sqlconn.execute("SELECT last FROM days WHERE userid=?", [message.author.id]).fetchone()[0]
                            last_day = datetime.datetime.strptime(last_day, '%Y-%m-%d').date()
                            delta = today - last_day
                            num = str(delta).split(" ")[0]
                            tmp = ""
                            try:
                                for digit in num:
                                    tmp = tmp + num_emoji[int(digit)]
                            except ValueError:
                                tmp = ":zero:"
                            out = "It has been {} days since your last time! :confetti_ball:".format(tmp)
                    sqlconn.commit()
                    sqlconn.close()

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
                if (message.author.id == cfg['Users']['aquova'] or message.author.id == cfg['Users']['eemie']):
                    if message.content == '!feedback':
                        out = '!feedback CHANNEL_ID MESSAGE'
                    else:
                        m = remove_command(message.content)
                        channel_id = m.split(" ")[0]
                        mes = m[len(channel_id):]
                        response_chan = client.get_channel(channel_id)
                        await client.send_message(response_chan, mes)
                        out = "Reply sent"
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
                    out = message.author.avatar_url
                else:
                    q = remove_command(message.content)
                    mem = discord.utils.get(message.server.members, name=q)
                    try:
                        out = mem.avatar_url
                    except AttributeError:
                        out = "There is no user by that name, please try again. (Usernames are case sensitive)."

            elif message.content.startswith('!g'):
                q = remove_command(message.content)
                out = google.search(q)[0].link

            elif message.content.startswith('!iss'):
                out = iss.main(message.author.id)

            elif message.content.startswith('!img'):
                if message.content == '!img':
                    out = "!img QUERY"
                else:
                    q = remove_command(message.content)
                    params = {'q': q,
                        'safe': 'on',
                        'lr': 'lang_en',
                        'hl': 'en',
                        'tbm': 'isch'
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
                    }

                    async with aiohttp.ClientSession() as session:
                        try:
                            with async_timeout.timeout(5):
                                async with session.get('https://google.com/search', params=params, headers=headers) as resp:
                                    if resp.status == 200:
                                        root = ET.fromstring(await resp.text(), ET.HTMLParser())
                                        foo = root.xpath(".//div[@class='rg_meta notranslate']")[0].text
                                        result = json.loads(foo)
                                        out = result['ou']
                                    else:
                                        out = "Google is unavailable I guess?\nError: {}".format(resp.response)
                        except IndexError:
                            out = "No search results found at all. Did you search for something naughty?"
                        except asyncio.TimeoutError:
                            out = "Timeout error"
                        except Exception as e:
                            out = "An unusual error of type {} occurred".format(type(e).__name__)

            # Tells a joke from a pre-programmed list
            elif message.content.startswith('!joke'):
                joke_list = Jokes.joke()
                pick_joke = random.choice(list(joke_list.keys()))
                out = joke_list[pick_joke]
                await client.send_message(message.channel, pick_joke)
                await asyncio.sleep(5)

            elif (message.content.startswith('!lovecalc') or message.content.startswith('!lc')):
                name_a = message.content.split(" ")[1]
                name_b = message.content.split(" ")[2]
                love_url = 'https://love-calculator.p.mashape.com/getPercentage?fname={}&sname={}'.format(name_a, name_b)

                headers={
                    "X-Mashape-Key": cfg['Client']['mashape'],
                    "Accept": "application/json"
                }

                r = requests.get(love_url, headers=headers)
                results = json.loads(r.text)
                out = "{} and {} are {}% compatible. {}".format(name_a, name_b, results['percentage'], results['result'])

            elif message.content.startswith('!mathfact'):
                if message.content == '!mathfact':
                    out = '!mathfact NUMBER'
                else:
                    num = message.content.split(" ")[1]
                    try:
                        foo = int(num)
                        fact_url = "https://numbersapi.p.mashape.com/{}/math?fragment=true&json=true".format(num)
                        headers={
                            "X-Mashape-Key": cfg['Client']['mashape'],
                            "Accept": "text/plain"
                        }

                        r = requests.get(fact_url, headers=headers)
                        results = json.loads(r.text)
                        out = "{} is {}".format(num, results['text'])
                    except TypeError:
                        out = "That is not a number, please try again."

            # Converts time into the Mayan calendar, why not
            elif message.content.startswith('!mayan'):
                parse = message.content.split(" ")
                if (message.content == '!mayan'):
                    out = '!until MM-DD-YYYY/TODAY'
                else:
                    out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

            # Converts message into/out of morse code
            elif message.content.startswith('!morse'):
                parse = remove_command(message.content)
                out = Morse.main(parse)

            elif (message.content.startswith('!myanimelist') or message.content.startswith('!mal')):
                out = MAL.main(message)

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

            # Pins most recent message of specified user
            elif message.content.startswith('!pin'):
                if message.content == '!pin':
                    out = '!pin @USERNAME'
                else:
                    id = message.content.split(" ")[1]
                    id = id[3:-1]
                    user = discord.utils.get(message.server.members, id=id)
                    async for pin in client.logs_from(message.channel, limit=100):
                        if (pin.author == user and pin.content != message.content):
                            try:
                                await client.pin_message(pin)
                            except discord.errors.HTTPException as e:
                                await client.send_message(reaction.message.channel, e) # If max pin limit has been reached
                            break

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

            # Convert number into/out of roman numerals
            elif message.content.startswith('!roman'):
                parse = message.content.split(" ")
                if (message.content == '!roman'):
                    out = '!roman NUMBER/NUMERAL'
                elif parse[1].isalpha() == True:
                    out = Roman.roman_to_int(parse[1])
                else:
                    out = Roman.int_to_roman(parse[1])

            # Returns scrabble value of given word
            elif message.content.startswith('!scrabble'):
                parse = message.content.split(" ")
                if (message.content == '!scrabble'):
                    out = '!scrabble WORD'
                else:
                    out = Scrabble.scrabble(parse[1])

            # Responds with the number of servers currently attached to
            elif message.content.startswith('!servers'):
                server_list = client.servers
                server_num = str(len(server_list))
                out = "I am currently a member of {} servers".format(server_num)
                if (message.content == '!servers list' and (message.author.id == cfg['Users']['aquova'] or message.author.id == cfg['Users']['eemie'])):
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

            elif message.content.startswith('!spellcheck'):
                q = remove_command(message.content).replace(" ","+")
                sc_url = 'https://montanaflynn-spellcheck.p.mashape.com/check/?text=' + q
                headers={
                    "X-Mashape-Key": cfg['Client']['mashape'],
                    "Accept": "text/plain"
                }

                r = requests.get(sc_url, headers=headers)
                results = json.loads(r.text)
                out = "Suggestion: {}".format(results['suggestion'])

            # Can change "now playing" game title
            elif message.content.startswith('!status'):
                if message.author.id == cfg['Users']['aquova']:
                    new_game = remove_command(message.content)
                    game_object = discord.Game(name=new_game)
                    await client.change_presence(game=game_object)
                    out = "Changed status to: {}".format(new_game)
                else:
                    out = "You do not have permissions for this command."

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
                    # out = Steam.get_userinfo(q) <- The old method

            elif message.content.startswith('!stop'):
                out = Select.stop()

            # Doesn't do anything right now, simply for testing
            elif message.content.startswith('!test'):
                if message.author.id == cfg['Users']['aquova']:
                    out = 'Yeah, thats coo.'
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

            elif message.content.startswith('!trapcard'):
                out = 'https://pbs.twimg.com/media/CXnDzNFWAAA70wX.jpg'

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

                    headers={
                        "Client-ID": cfg['Client']['twitch'],
                        "Accept": "application/vnd.twitchtv.v5+json"
                    }

                    r = requests.get(twitch_url, headers=headers)
                    results = json.loads(r.text)
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
                if (message.content == '!until'):
                    out = '!until MM-DD-YYYY'
                else:
                    out = str(Days_Until.until(parse[1])) + " days"

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

            elif (message.content.startswith('!whatpulse') or message.content.startswith('!wp')):
                sqlconn = sqlite3.connect('database.db')
                if len(message.content.split(" ")) == 1:
                    userinfo = sqlconn.execute("SELECT username FROM whatpulse WHERE userid=?", [message.author.id,])
                    try:
                        q = userinfo.fetchone()[0]
                        info = Whatpulse.main(q)
                        if isinstance(info, list):
                            embed = discord.Embed(title=info[0], type='rich', description=info[8])
                            embed.add_field(name='Date Joined', value=info[1])
                            embed.add_field(name='Country', value=info[2])
                            embed.add_field(name='Key Presses', value=info[3])
                            embed.add_field(name='Clicks', value=info[4])
                            embed.add_field(name='Downloaded', value=info[5])
                            embed.add_field(name='Uploaded', value=info[6])
                            embed.add_field(name='Team', value=info[7])
                            await client.send_message(message.channel, embed=embed)
                        else:
                            out = info
                    except TypeError:
                        out = "!whatpulse [set] USERNAME"
                elif message.content.split(" ")[1].upper() == "SET":
                    username = " ".join(message.content.split(" ")[2:])
                    params = [message.author.id, username]
                    sqlconn.execute("INSERT OR REPLACE INTO whatpulse (userid, username) VALUES (?, ?)", params)
                    out = "User added"
                else:
                    q = remove_command(message.content)
                    info = Whatpulse.main(q)
                    if isinstance(info, list):
                        embed = discord.Embed(title=info[0], type='rich', description=info[8])
                        embed.add_field(name='Date Joined', value=info[1])
                        embed.add_field(name='Country', value=info[2])
                        embed.add_field(name='Key Presses', value=info[3])
                        embed.add_field(name='Clicks', value=info[4])
                        embed.add_field(name='Downloaded', value=info[5])
                        embed.add_field(name='Uploaded', value=info[6])
                        embed.add_field(name='Team', value=info[7])
                        await client.send_message(message.channel, embed=embed)
                    else:
                        out = info
                sqlconn.commit()
                sqlconn.close()

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
                out = xkcd.main(message.content)

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

            elif ("FUCK ME" in message.content.upper() and message.author.id == cfg['Users']['eemie']):
                out = "https://s-media-cache-ak0.pinimg.com/736x/48/2a/bf/482abf4c4f8cd8d9345253db901cf1d7.jpg"

            elif ("AQUOBOT" in message.content.upper() and (("FUCK" in message.content.upper()) or ("HATE" in message.content.upper()))):
                out = ":cold_sweat:"

            elif message.content.startswith('!jade'):
                out = "http://i.imgur.com/vCDF2aO.png"

            elif (message.content.upper() == 'AQUOBOT ATTACK MODE' or message.content.upper() == 'AQUOBOT, ATTACK MODE'):
                out = '`ENGAGING ATTACK MODE`\n`ATOMIC BATTERIES TO POWER. TURBINES TO SPEED.`\n`READY TO EXECUTE ATTACK VECTOR` :robot:'

            elif message.content.upper() == 'GNU TERRY PRATCHETT':
                out = 'GNU Terry Pratchett'

            if out != "":
                await client.send_typing(message.channel)

            await client.send_message(message.channel, out)

        except discord.errors.HTTPException:
            pass

client.run(discord_key)
