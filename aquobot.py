"""
The Aquobot program for Discord
The only Discord bot that utilizes the Mayan calendar!
http://github.com/Aquova/Aquobot

Written by Austin Bricker, 2017
Requires Python 3.5+ to run
"""

import sys
sys.path.insert(0, './programs')

import discord, wolframalpha, wikipedia, requests, aiohttp
from googletrans import Translator
from geopy.geocoders import Nominatim
from google import google
import lxml.etree as ET
import asyncio, json, subprocess, logging, random, sqlite3, datetime, urllib

# Python programs I wrote, in ./programs
import Morse, Scrabble_Values, Roman_Numerals, Days_Until, Mayan, Jokes, Weather
import Upside, Ecco, Select, Youtube, Steam, Whatpulse, Slots

# Suppressing the UserWarning from the wikipedia module. Possibly a bad idea in the long run
import warnings
warnings.filterwarnings('ignore', category=UserWarning, append=True)

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

def get_xkcd(xkcd_json):
    title = xkcd_json['title']
    date = "{0}/{1}/{2}".format(xkcd_json['month'], xkcd_json['day'], xkcd_json['year'])
    alt_text = xkcd_json['alt']
    img_url = xkcd_json['img']
    num = xkcd_json['num']
    out = title + ", " + date + ", Comic #" + str(num) + '\n' + img_url + '\n' + "Alt text: " + alt_text
    return out

def hand_value(hand):
    total = 0
    for card in hand:
        if (card == 'K' or card == 'Q' or card == 'J'):
            total += 10
        elif card == 'A':
            if total + 11 > 21:
                total += 1
            else:
                total += 11
        else:
            total += int(card)
    return total

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)

async def check_birthday():
    sqlconn = sqlite3.connect('database.db')
    birth_months = sqlconn.execute("SELECT month FROM birthday").fetchone()
    birth_days = sqlconn.execute("SELECT day FROM birthday").fetchone()
    birth_ids = sqlconn.execute("SELECT id FROM birthday").fetchone()

    d = datetime.date.today()
    month = d.month
    day = d.day
    today_bdays = []
    if birth_ids != None:
        for i in range(0, len(birth_ids)):
            try:
                if (month == int(birth_months[i]) and day == int(birth_days[i])):
                    today_bdays.append(birth_ids[i])
            except ValueError as e:
                print("Error handled: " + e)
                pass
    else:
        print("birth_names is null apparently")

    # Oh dear.
    if today_bdays != []:
        for j in today_bdays:
            for server in client.servers:
                ids = [x.id for x in server.members]
                if str(j) in ids:
                    birth_name = sqlconn.execute("SELECT name FROM birthday WHERE id=?", [j]).fetchone()[0]
                    mess = "Today is {0}'s birthday! Everybody wish them a happy birthday! :birthday:".format(birth_name)
                    await client.send_message(server.default_channel, mess)

    sqlconn.commit()
    sqlconn.close()

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # TODO: Fix game changing, as it's now broken
    game_object = discord.Game(name="type !help")
    await client.change_presence(game=game_object)

    global channel_id_list
    channel_id_list = [x.id for x in client.get_all_channels()]

    while True:
        print("Checking birthday")
        await check_birthday()
        print("Done checking, now sleeping.")
        await asyncio.sleep(86400) # One day in seconds - 86400
    
@client.event
async def on_channel_create(channel):
    channel_id_list.append(channel.id)

@client.event
async def on_channel_delete(channel):
    channel_id_list.remove(channel.id)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '💬':
        user_name = reaction.message.author.name
        user_id = reaction.message.author.id
        mes = reaction.message.content
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
    elif reaction.emoji == '📌':
        await client.pin_message(reaction.message)

@client.event
async def on_server_join(server):
    serv_name = server.name
    serv_id = server.id
    serv_owner_name = server.owner.name
    serv_owner_id = server.owner.id
    default_channel = server.default_channel
    mems = server.member_count
    await client.send_message(default_channel, "Thank you for adding me to your server! Type '!help' for a list of commands")
    await client.send_message(cfg['Servers']['general'], "Aquobot has been added to {0} (ID: {1}) Owned by {2} ({3}). Server has {4} members.".format(serv_name, serv_id, serv_owner_name, serv_owner_id, mems))

@client.event
async def on_server_remove(server):
    serv_name = server.name
    serv_id = server.id
    await client.send_message(cfg['Servers']['general'], "Aquobot has been removed from {0} (ID {1}). How rude.".format(serv_name, serv_id))

# Upon typed message in chat
@client.event
async def on_message(message):
    if message.channel.id not in channel_id_list:
        secret = "User {0} (ID {1}) sent this DM: {2}".format(message.author.name,message.author.id,message.content)
        DM_channel = client.get_channel(cfg['Servers']['DM-channel'])
        await client.send_message(DM_channel, secret)
        
    if message.author.id != client.user.id:
        try:
            out = ""
            # !help links to website with command list
            if message.content.startswith("!help"):
                out = "http://aquova.github.io/Aquobot"

            # Updates bot to most recent version
            elif message.content.startswith("!update"):
                if (message.author.id == cfg['Users']['eemie'] or message.author.id == cfg['Users']['aquova']):
                    subprocess.call("./update.sh", shell=True)
                    sys.exit()

            # Responds if active
            elif message.content.startswith('!alive'):
                options = ['Nah.', 'Who wants to know?', ':robot: `yes`', "I wouldn't be responding if I were dead."]
                if discord.Client.is_logged_in: # Is this really necessary?
                    out = random.choice(options)

            # Gives brief overview of the bot
            elif message.content.startswith('!about'):
                server_list = client.servers
                server_num = str(len(server_list))
                aquo_link = "<https://discordapp.com/oauth2/authorize?client_id=323620520073625601&scope=bot&permissions=2117594231>"
                out = "Hello, my name is Aquobot. I was written in Python by Aquova so he would have something interesting to put on a resume. I am currently connected to {0} servers, and I look forward to spending time with you! If you want to have me on your server, go visit {1}, and ~~when~~ if that doesn't work, contact Aquova.".format(server_num, aquo_link)

            # Ban actually does nothing
            # It picks a random user on the server and says it will ban them, but takes no action
            elif message.content.startswith('!ban'):
                out = Select.ban(message.server.members, message.author.name)

            # Database of user birthdays. Will notify server if user's birthday on list is that day
            elif message.content.startswith('!birthday'):
                months = {'JANUARY':1, 'JAN':1, 'FEB':2, 'FEBRUARY':2, 'MARCH':3, 'MAR':3, 'APRIL':4, 'APR':4, 'MAY':5, 'JUNE':6, 'JUN':6, 'JULY':7, 'JUL':7, 'AUGUST':8, 'AUG':8, 'SEPTEMBER':9, 'SEPT':9, 'OCTOBER':10, 'OCT':10, 'NOVEMBER':11, 'NOV':11, 'DECEMBER':12, 'DEC':12}
                reverse = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
                sqlconn = sqlite3.connect('database.db')
                author_name = message.author.name
                author_id = message.author.id
                server_id = message.server.id
                if message.content == '!birthday':
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [author_id])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [author_id])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Your birthday is {0} {1}".format(reverse[int(query_month)], query_day)
                    except TypeError:
                        out = "!birthday [set] MONTH DAY"
                elif message.content.startswith('!birthday set'):
                    q = message.content.split(" ")[2:]
                    try:
                        if (1 <= int(q[1]) and int(q[1]) <= 31):
                            if q[0].upper() in months.keys():
                                params = (author_id, author_name, months[q[0].upper()], int(q[1]), server_id)
                                sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day, server_id) VALUES (?, ?, ?, ?, ?)", params)
                                out = "{0}'s birthday now set as {1}/{2}".format(author_name, months[q[0].upper()], q[1])
                            elif (1 <= int(q[0]) and int(q[0]) <= 12):
                                params = (author_id, author_name, int(q[0]), int(q[1]), server_id)
                                sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day) VALUES (?, ?, ?, ?, ?)", params)
                                out = "{0}'s birthday now set as {1}/{2}".format(author_name, q[0], q[1])
                            else:
                                out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
                        else:
                            out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
                    except ValueError:
                        out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
                elif message.content.startswith('!birthday list'):
                    birth_ids = sqlconn.execute("SELECT id FROM birthday").fetchall()
                    out = ""
                    ids = [x.id for x in message.server.members]
                    for user in birth_ids:
                        if str(user[0]) in ids:
                            birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                            birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                            birth_name = sqlconn.execute("SELECT name FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                            out += "{0}'s birthday is on {1} {2}\n".format(birth_name, reverse[int(birth_month)], birth_day)
                    if out == "":
                        out = "There are no birthdays entered for anyone on this server."
                else:
                    q = remove_command(message.content)
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE name=?", [q])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE name=?", [q])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Their birthday is {0} {1}".format(reverse[int(query_month)], query_day)
                    except TypeError:
                        out = "Error: No birthday for that user (searches are case sensitive)."
                sqlconn.commit()
                sqlconn.close()

            elif message.content.startswith('!blackjack'):
                if message.content == '!blackjack rules':
                    out = '<https://en.wikipedia.org/wiki/Blackjack#Player_decisions>'
                else:
                    sqlconn = sqlite3.connect('database.db')
                    money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
                    try:
                        user_money = money.fetchone()[0]
                    except TypeError:
                        user_money = 0

                    await client.send_message(message.channel, "Alright {}, time to play Blackjack!".format(message.author.name))
                    deck = [str(i) for i in range(2, 11)] * 4
                    deck.extend([i for i in ['K', 'Q', 'J', 'A']] * 4)
                    deck = random.sample(deck,len(deck))
                    dealer = []
                    player = []
                    player.append(deck.pop())
                    player.append(deck.pop())
                    dealer.append(deck.pop())
                    dealer.append(deck.pop())
                    await client.send_message(message.channel, "Okay {}, you've drawn a {} and {}, for a total of {}".format(message.author.name, player[0], player[1], hand_value(player)))
                    
                    if hand_value(player) == 21:
                        user_money += 150
                        await client.send_message(message.channel, "{}: Blackjack!! You win! You now have {} points!".format(message.author.name, user_money))
                        params = [message.author.id, user_money]
                        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
                    elif hand_value(dealer) == 21:
                        user_money -= 100
                        await client.send_message(message.channel, "{}: The dealer has a Blackjack, you lose. You now have {} points".format(message.author.name,user_money))
                        params = [message.author.id, user_money]
                        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
                    else:
                        dd = 1 # Double down multplier
                        first = True # Is it the first draw? (For double down)
                        while (hand_value(dealer) < 21 and hand_value(player) < 21):
                            if first:
                                await client.send_message(message.channel, "{}: Would you like to 'hit', 'stand', or 'double down' ('dd')?".format(message.author.name))
                            else:
                                await client.send_message(message.channel, "{}: Would you like to 'hit' or 'stand'?".format(message.author.name))

                            msg = await client.wait_for_message(author=message.author, timeout=10)
                            if msg == None:
                                await client.send_message(message.channel, "{}: I'm sorry, but you have taken too long to respond".format(message.author.name))
                                break
                            elif msg.content.upper() == 'STAND':
                                while hand_value(dealer) < 17:
                                    dealer.append(deck.pop())
                                break
                            elif msg.content.upper() == 'HIT':
                                first = False
                                new_card = deck.pop()
                                player.append(new_card)
                                await client.send_message(message.channel, "{}: You drew a {}, your new total is {}".format(message.author.name,new_card, hand_value(player)))
                                if hand_value(player) > 21:
                                    break
                                else:
                                    continue
                            elif ((msg.content.upper() == 'DOUBLE DOWN' or msg.content.upper() == 'DD') and first == True):
                                new_card = deck.pop()
                                player.append(new_card)
                                dd = 2
                                await client.send_message(message.channel, "{}: You've chosen to double down! You get one more card, and the bets are doubled.\nYou drew a {}, your new total is {}".format(message.author.name,new_card, hand_value(player)))
                                if hand_value(player) > 21:
                                    break
                                else:
                                    while hand_value(dealer) < 17:
                                        dealer.append(deck.pop())
                                    break
                            else:
                                await client.send_message(message.channel, "{}: That's not a valid answer, try again.".format(message.author.name))
                                continue

                        if hand_value(dealer) > 21:
                            user_money += 50 * dd
                            await client.send_message(message.channel, "{}: The dealer has gone over 21, you win! You now have {} points".format(message.author.name,user_money))
                        elif hand_value(player) > 21:
                            user_money -= 50 * dd
                            await client.send_message(message.channel, "{}: You have gone over 21, you lose.. You now have {} points".format(message.author.name,user_money))
                        elif hand_value(dealer) >= hand_value(player):
                            user_money -= 50 * dd
                            await client.send_message(message.channel, "{}: The dealer had {} while you had {}, you lose. You now have {} points".format(message.author.name,hand_value(dealer), hand_value(player), user_money))
                        else:
                            user_money += 50 * dd
                            await client.send_message(message.channel, "{}: The dealer has {}, but you have {}! You win! You now have {} points".format(message.author.name,hand_value(dealer), hand_value(player), user_money))

                        params = [message.author.id, user_money]
                        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

                    sqlconn.commit()
                    sqlconn.close()

            # Prints out the calendar for the month
            elif message.content.startswith('!cal'):
                # This command doesn't work under OS X, as the -h flag isn't supported (for some reason)
                out = "```bash" + '\n' + subprocess.run(['cal', '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"

            # Chooses between given options
            elif message.content.startswith('!choose'):
                if message.content == "!choose":
                    out = "!choose OPTION1, OPTION2, OPTION3..."
                else:
                    tmp = remove_command(message.content)
                    choice = tmp.split(",")
                    out = str(random.choice(choice))

            # This one is for me and Eemie
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
                            for digit in num:
                                tmp = tmp + num_emoji[int(digit)]
                            out = "It has been {} days since your last time! :confetti_ball:".format(tmp)
                    sqlconn.commit()
                    sqlconn.close()

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
                        await client.send_file(message.channel, fp='./programs/ecco.png')

            # Repeats back user message
            elif message.content.startswith('!echo'):
                out = remove_command(message.content)    

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
                    userid = message.author.id
                    username = message.author.name
                    userchannel = message.channel.id
                    userserver = message.channel.server.id
                    mes = remove_command(message.content)
                    fb = "A message from {0} for you sir: '{1}' (User ID: {2}) (Server ID {3}) (Channel ID {4})".format(username, mes, userid, userserver, userchannel)
                    await client.send_message(feedback_channel, fb)
                    out = "Message sent" 

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
                    # To embed image:
                    # em = discord.Embed()
                    # em.set_image(url=url)
                    # await client.send_message(message.channel, embed=em)
                else:
                    q = remove_command(message.content)
                    mem = discord.utils.get(message.server.members, name=q)
                    try:
                        out = mem.avatar_url
                        # em = discord.Embed()
                        # em.set_image(url=url)
                        # await client.send_message(message.channel, embed=em)
                    except AttributeError:
                        out = "There is no user by that name, please try again. (Usernames are case sensitive)."

            elif message.content.startswith('!g'):
                q = remove_command(message.content)
                out = google.search(q)[0].link

            elif message.content.startswith('!iss'):
                sqlconn = sqlite3.connect('database.db')
                geo = Nominatim()
                iss_json_url = urllib.request.urlopen('http://api.open-notify.org/iss-now.json')
                iss_json = json.loads(iss_json_url.read())
                latitude = iss_json['iss_position']['latitude']
                longitude = iss_json['iss_position']['longitude']
                location = geo.reverse("{0}, {1}".format(latitude,longitude))

                if float(latitude) >= 0:
                    latitude += "° N"
                else:
                    latitude = str(-1 * float(latitude)) + "° S"

                if float(longitude) >= 0:
                    longitude += "° E"
                else:
                    longitude = str(-1 * float(longitude)) + "° W"

                time = datetime.datetime.fromtimestamp(iss_json['timestamp'])
                out = "Right now ({0}), the International Space Station is located at {1}, {2}".format(time, latitude, longitude)
                try:
                    out += ", located at {}".format(location)
                except TypeError:
                    pass

                # Check if user's location is stored, and add info
                user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [message.author.id])
                try:
                    user_location = user_loc.fetchone()[0]
                    location = geo.geocode(user_location)
                    user_lat = location.latitude
                    user_long = location.longitude
                    pass_url = urllib.request.urlopen("http://api.open-notify.org/iss-pass.json?lat={0}&lon={1}".format(user_lat,user_long))
                    pass_json = json.loads(pass_url.read())
                    risetime = datetime.datetime.fromtimestamp(pass_json['response'][0]['risetime'])
                    duration = pass_json['response'][0]['duration']
                    out += '\nThe ISS will next pass over your location at {0} for {1} seconds'.format(risetime, duration)
                except TypeError:
                    out += "\nAdd your location to the database with !w add LOCATION to get more information!"

            elif message.content.startswith('!img'):
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
                    async with session.get('https://google.com/search', params=params, headers=headers) as resp:
                        root = ET.fromstring(await resp.text(), ET.HTMLParser())
                        foo = root.xpath(".//div[@class='rg_meta notranslate']")[0].text
                        result = json.loads(foo)
                        out = result['tu']
                        # For embeded image:
                        # url = result['tu']
                        # em = discord.Embed()
                        # em.set_image(url=url)
                        # await client.send_message(message.channel, embed=em)

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

            elif (message.content.startswith('!myanimelist') or message.content.startswith('!mal')):
                sqlconn = sqlite3.connect('database.db')
                if len(message.content.split(" ")) == 1:
                    userinfo = sqlconn.execute("SELECT username FROM anime WHERE userid=?", [message.author.id,])
                    try:
                        q = userinfo.fetchone()[0]
                        url = "https://myanimelist.net/profile/" + q
                        r = requests.get(url)
                        if r.status_code != 404:
                            out = "Here's your account! ~~You weeb~~" + '\n' + url
                        else:
                            out = "No user found by that name"
                    except TypeError:
                        out = "!mal [set] USERNAME"
                elif message.content.split(" ")[1].upper() == "SET":
                    username = " ".join(message.content.split(" ")[2:])
                    url = "https://myanimelist.net/profile/" + username
                    r = requests.get(url)
                    if r.status_code != 404:
                        params = [message.author.id, username]
                        sqlconn.execute("INSERT OR REPLACE INTO anime (userid, username) VALUES (?, ?)", params)
                        out = "You too huh? :flag_jp:"
                    else:
                        out = "No user found by that name, did you misspell it?"
                else:
                    q = remove_command(message.content)
                    url = "https://myanimelist.net/profile/" + q
                    r = requests.get(url)
                    if r.status_code != 404:
                        out = "Here's your account you weeaboo trash!" + '\n' + url
                    else:
                        out = "No user found by that name"
                sqlconn.commit()
                sqlconn.close()

            # Pins most recent message of specified user
            elif message.content.startswith('!pin'):
                if message.content == '!pin':
                    out = '!pin @USERNAME'
                else:
                    id = message.content.split(" ")[1]
                    id = id[3:-1] # This is a terrible way to do this. You should fix this sometime.
                    user = discord.utils.get(message.server.members, id=id)
                    async for pin in client.logs_from(message.channel, limit=100):
                        if (pin.author == user and pin.content != message.content):
                            await client.pin_message(pin)
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
                sqlconn = sqlite3.connect('database.db')
                mes_server = message.server.id
                if message.content == '!quote':
                    try:
                        valid = sqlconn.execute("SELECT quote FROM quotes WHERE serverid=?", [mes_server])
                        quotes = valid.fetchall()
                        quote = random.choice(quotes)
                        rand_username = sqlconn.execute("SELECT username FROM quotes WHERE quote=?", [quote[0]])
                        username = rand_username.fetchone()[0]
                        rand_num = sqlconn.execute("SELECT num FROM quotes WHERE quote=?", [quote[0]])
                        num = rand_num.fetchone()[0]
                        out = 'From {0}: "{1}" (#{2})'.format(username, quote[0], str(num))
                    except TypeError:
                        out = "This server has no quotes in the database. React to a message with :speech_balloon: to add quotes."
                elif len(message.content.split(" ")) == 2:
                    try:
                        num = int(remove_command(message.content))
                        fetched_quote = sqlconn.execute("SELECT quote FROM quotes WHERE num=?", [num])
                        fetched_username = sqlconn.execute("SELECT username FROM quotes WHERE num=?", [num])
                        quote = fetched_quote.fetchone()[0]
                        username = fetched_username.fetchone()[0]
                        if quote != None:
                            out = 'From {0}: "{1}" (#{2})'.format(username, quote, str(num))
                        else:
                            out = "There is no quote of that number"
                    except ValueError:
                        out = "That is not a number. Please try again"
                    except TypeError:
                        out = "There is no quote of that number"
                elif message.content.startswith('!quote remove'):
                    try:
                        num = int(message.content[14:])
                        check_exists = sqlconn.execute("SELECT messageid FROM quotes WHERE num=?", [num])
                        check_exists = check_exists.fetchone()[0]
                        sqlconn.execute("INSERT OR REPLACE INTO quotes (num, quote, username, userid, messageid, serverid) VALUES (?, NULL, NULL, NULL, NULL, NULL)", [num])
                        out = "Item {} removed".format(num)
                    except ValueError:
                        out = "That is not a number. Please specify the quote ID number you wish to remove."
                    except TypeError:
                        out = "There is no ID of that number."    
                sqlconn.commit()
                sqlconn.close()
                
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

            # Responds with the number of servers currently attached to
            elif message.content.startswith('!servers'):
                server_list = client.servers
                server_num = str(len(server_list))
                out = "I am currently a member of {} servers".format(server_num)
                if (message.content == '!servers list' and (message.author.id == cfg['Users']['aquova'] or message.author.id == cfg['Users']['eemie'])):
                    for server in server_list:
                        out += '\n' + server.name

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
            # Isn't currently working, for reasons unknown
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
                sqlconn = sqlite3.connect('database.db')
                username = message.author.name
                userid = message.author.id
                timestamp = str(message.timestamp)
                time = timestamp.split(".")[0] + " GMT" # Right now, time is given in GMT. Possibly change to use local time instead.
                if message.content == '!todo':
                    user_list = sqlconn.execute("SELECT * FROM todo WHERE userid=?", [userid])
                    user_todos = user_list.fetchall()
                    if user_todos == []:
                        out = "You have not added anything to your todo list.\nAdd items with '!todo add item'"
                    else:
                        out = ""
                        for item in user_todos:
                            out += "{0} @ {1}. (#{2})".format(item[3], item[4], item[0]) + '\n'
                elif message.content.startswith('!todo add'):
                    num = sqlconn.execute("SELECT COUNT(*) FROM todo") # WHERE userid IS NOT NULL")
                    num = num.fetchone()[0] + 1
                    mes = message.content[10:]
                    params = (num, userid, username, mes, time)
                    sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, message, t) VALUES (?, ?, ?, ?, ?)", params)
                    out = "Item added by {0}: {1} @ {2}. (#{3})".format(username, mes, time, num)
                elif message.content.startswith('!todo remove'):
                    try:
                        remove_id = int(message.content[13:])
                        check_user = sqlconn.execute("SELECT userid FROM todo WHERE id=?", [remove_id])
                        check_user = str(check_user.fetchone()[0])
                        if check_user == userid:
                            sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, message, t) VALUES (?, NULL, NULL, NULL, NULL)", [remove_id])
                            out = "Item {} removed".format(remove_id)
                        else:
                            out = "You are not allowed to remove other user's items."
                    except TypeError:
                        out = "There is no entry of that index value"
                    except ValueError:
                        out = "That's not a number. Please specify the index number of the item to remove."
                else:
                    out = "!todo [add/remove]"
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
                wiki_url = 'https://en.wikipedia.org/wiki/'
                results = wikipedia.search(q)
                try:
                    wikipedia.WikipediaPage(title=results[0])
                    out = wiki_url + results[0].replace(" ","_")
                except wikipedia.exceptions.DisambiguationError as e:
                    out = wiki_url + e.options[0].replace(" ","_")
                except IndexError:
                    out = 'No article was found with that name'
                    
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
                xkcd_json_url = urllib.request.urlopen('https://xkcd.com/info.0.json')
                xkcd_json = json.loads(xkcd_json_url.read())
                max_comic = xkcd_json['num']
                if message.content == '!xkcd':
                    out = get_xkcd(xkcd_json)
                elif (message.content.split(" ")[1] == 'random' or message.content.split(" ")[1] == 'rand'):
                    num = random.randint(1, max_comic)
                    new_url = 'https://xkcd.com/{}/info.0.json'.format(num)
                    new_json_url = urllib.request.urlopen(new_url)
                    xkcd_json = json.loads(new_json_url.read())
                    out = get_xkcd(xkcd_json)
                else:
                    try:
                        num = int(message.content.split(" ")[1])
                        new_url = 'https://xkcd.com/{}/info.0.json'.format(num)
                        new_json_url = urllib.request.urlopen(new_url)
                        xkcd_json = json.loads(new_json_url.read())
                        out = get_xkcd(xkcd_json)
                    except ValueError:
                        out = "Not a valid number." + '\n' + "!xkcd [comic #]"
                    except urllib.error.HTTPError:
                        out = "There's no comic with that index number."

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
                
            elif message.content.startswith('!lex'):
                out = "https://i.imgur.com/yB8wssv.jpg"

            if message.server.id != cfg['Servers']['Magic']:
                # Never bring a knife to a gunfight
                if message.content.startswith("🔪"):
                    out = ":gun:"

                elif message.content.startswith('🔫'):
                    await client.send_message(message.channel, ":knife:")
                    await asyncio.sleep(1)
                    out = "Oh, wait. :cold_sweat:"

                elif message.content.split(" ")[0].upper() == "I'M" or message.content.split(" ")[0].upper() == "IM":
                    if len(message.content.split(" ")) == 2:
                        if message.content.split(" ")[1].upper() == "AQUOBOT":
                            out = "WHAT?! But if you're Aquobot... Then... Who am I? :cold_sweat:"
                        else:
                            if random.choice(range(100)) == 0:
                                out = "hi {} im aquobot".format(message.content.split(" ")[1].lower())

                elif (message.content.upper().startswith("DID SOMEONE SAY") or message.content.upper().startswith("DID SOMEBODY SAY")):
                    mes = message.content.split(" ")
                    sass = " ".join(mes[3:])
                    out = "*{}*".format(sass)

                elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
                    if (message.author.id != client.user.id and random.choice(range(20)) == 0):
                        out = "https://i0.wp.com/www.thekitchenwhisperer.net/wp-content/uploads/2014/04/BelgianWaffles8.jpg"

                elif ("NETHERLANDS" in message.content.upper()) or ("DUTCH" in message.content.upper()):
                    if random.choice(range(20)) == 0:
                        out = ":flag_nl:"

                elif "MERICA" in message.content.upper():
                    if random.choice(range(20)) == 0:
                        out = "http://2static.fjcdn.com/pictures/Blank_7a73f9_5964511.jpg"

                elif "CANADA" in message.content.upper():
                    if random.choice(range(20)) == 0:
                        out = ":flag_ca: :hockey:"

                elif "EXCUSE ME" in message.content.upper():
                    if random.choice(range(10)) == 0:
                        out = "You're excused."

                elif "EXCUSE YOU" in message.content.upper():
                    if random.choice(range(10)) == 0:
                        out = "I'm excused?"
                
            if out != "":
                await client.send_typing(message.channel)

            await client.send_message(message.channel, out)

        except discord.errors.HTTPException:
            pass

client.run(discord_key)
