"""
An "offline" CLI for Aquobot
Designed to allow me to use some of Aquobot's functions from a terminal, without a Discord client
Written by aquova, 2018
"""

import sys
sys.path.insert(0, './commands')

from googletrans import Translator
from google import google
import lxml.etree as ET
import aiohttp, wolframalpha, asyncio, json, random, sqlite3, datetime, urllib, time
import async_timeout
from Utils import remove_command

import Help, Select, BF, Cal, Ecco, Weather, ISS, Jokes, Mayan, Morse, Roman, Scrabble, Speedrun, Steam, Todo, Upside, Until, Wikipedia, Youtube, XKCD

with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

wolframKey = str(cfg['Client']['wolfram'])
waclient = wolframalpha.Client(wolframKey)

def startswith(phrase, substring):
    subLength = len(substring)
    if len(phrase) < subLength:
        return False
    if substring == phrase[:subLength]:
        return True
    return False

def main():
    userInput = input("> ")
    out = ""
    # quit or !quit or exit exits the program
    if startswith(userInput, "quit") or startswith(userInput, "exit"):
        sys.exit(0)

    # !help links to website with command list
    elif startswith(userInput, "!help"):
        if userInput == '!help':
            out = "http://aquova.github.io/Aquobot\nFor help on a specific command, type `!help COMMAND`"
        else:
            out = Help.main(remove_command(userInput))

    elif startswith(userInput, "!8ball"):
        if userInput == "!8ball":
            out = "You need to ask a question silly."
        else:
            out = Select.eightball()

    # Responds if active
    elif startswith(userInput, "!alive"):
        out = random.choice(['Nah.', 'Who wants to know?', ':robot: `yes`', "I wouldn't be responding if I were dead."])

    # elif (message.content.startswith('!brainfuck') or message.content.startswith('!bf')):
    #     if len(message.content.split(" ")) == 1:
    #         out = '!brainfuck CODE\nInfo on the language: <https://learnxinyminutes.com/docs/brainfuck/>\nStill confused? Use this site to help visualize what is happening <http://bf.jamesliu.info/>'
    #     else:
    #         q = remove_command(message.content)
    #         if q[0] in '+-[]><.':
    #             out = BF.decode(q)
    #         else:
    #             out = BF.encode(q)

    # # Prints out the calendar for the month
    # elif message.content.startswith('!cal'):
    #     out = Cal.main(message)

    # # Chooses between given options
    # elif message.content.startswith('!choose'):
    #     if message.content == "!choose":
    #         out = "!choose OPTION1, OPTION2, OPTION3..."
    #     else:
    #         tmp = remove_command(message.content)
    #         choice = tmp.split(",")
    #         out = str(random.choice(choice))

    # # Responds with .png image of text in "Ecco the Dolphin" style
    # elif message.content.startswith('!ecco'):
    #     if message.content == '!ecco':
    #         out = '!ecco PHRASE'
    #     else:
    #         q = remove_command(message.content)
    #         valid = Ecco.text(q)
    #         if valid == 'ERROR':
    #             out = 'That phrase used an invalid character. Please try again.'
    #         else:
    #             out = "Image generated."

    # # Repeats back user message
    # elif message.content.startswith('!echo'):
    #     out = remove_command(message.content)

    # # Tells a 7 day forecast based on user or location. Uses same database as weather
    # elif (message.content.startswith('!forecast') or message.content.startswith('!f')):
    #     sqlconn = sqlite3.connect('database.db')
    #     author_id = int(message.author.id)
    #     author_name = message.author.name
    #     if (message.content == '!forecast' or message.content == '!f'):
    #         user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
    #         try:
    #             query_location = user_loc.fetchone()[0]
    #             out = Weather.forecast(query_location)
    #         except TypeError:
    #             out = "!forecast [set] LOCATION"
    #     elif message.content.startswith("!forecast set"):
    #         q = message.content[13:]
    #         params = (author_id, author_name, q)
    #         sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
    #         out = "Location set as %s" % q
    #     else:
    #         try:
    #             q = remove_command(message.content)
    #             out = Weather.forecast(q)
    #         except TypeError:
    #             out = "No location found. Please be more specific."
    #     sqlconn.commit()
    #     sqlconn.close()

    # # Same as !forecast, but responds with emojis
    # elif message.content.startswith('!qf'):
    #     sqlconn = sqlite3.connect('database.db')
    #     author_id = int(message.author.id)
    #     author_name = message.author.name
    #     if message.content == '!qf':
    #         user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
    #         try:
    #             query_location = user_loc.fetchone()[0]
    #             out = Weather.emoji_forecast(query_location)
    #         except TypeError:
    #             out = "!qf [set] LOCATION"
    #     elif message.content.startswith("!qf set"):
    #         q = message.content[7:]
    #         params = (author_id, author_name, q)
    #         sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
    #         out = "Location set as %s" % q
    #     else:
    #         try:
    #             q = remove_command(message.content)
    #             out = Weather.emoji_forecast(q)
    #         except TypeError:
    #             out = "No location found. Please be more specific."
    #     sqlconn.commit()
    #     sqlconn.close()

    # elif message.content.startswith('!g'):
    #     q = remove_command(message.content)
    #     out = google.search(q)[0].link

    # elif message.content.startswith('!iss'):
    #     out = ISS.main(message.author.id)

    # # elif message.content.startswith('!img'):
    # #     if message.content == '!img':
    # #         out = "!img QUERY"
    # #     else:
    # #         q = remove_command(message.content)
    # #         params = {'q': q,
    # #             'safe': 'on',
    # #             'lr': 'lang_en',
    # #             'hl': 'en',
    # #             'tbm': 'isch'
    # #         }

    # #         headers = {
    # #             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
    # #         }

    # #         with aiohttp.ClientSession() as session:
    # #             try:
    # #                 with async_timeout.timeout(5):
    # #                     with session.get('https://google.com/search', params=params, headers=headers) as resp:
    # #                         if resp.status == 200:
    # #                             root = ET.fromstring(resp.text(), ET.HTMLParser())
    # #                             foo = root.xpath(".//div[@class='rg_meta notranslate']")[0].text
    # #                             result = json.loads(foo)
    # #                             out = result['ou']
    # #                         else:
    # #                             out = "Google is unavailable I guess?\nError: {}".format(resp.response)
    # #             except IndexError:
    # #                 out = "No search results found at all. Did you search for something naughty?"
    # #             except asyncio.TimeoutError:
    # #                 out = "Timeout error"
    # #             except Exception as e:
    # #                 out = "An unusual error of type {} occurred".format(type(e).__name__)

    # # Tells a joke from a pre-programmed list
    # # elif message.content.startswith('!joke'):
    # #     joke_list = Jokes.joke()
    # #     pick_joke = random.choice(list(joke_list.keys()))
    # #     out = joke_list[pick_joke]
    # #     print(pick_joke)
    # #     await asyncio.sleep(5)

    # # Converts time into the Mayan calendar, why not
    # elif message.content.startswith('!mayan'):
    #     parse = message.content.split(" ")
    #     if message.content == '!mayan':
    #         out = '!mayan MM-DD-YYYY/TODAY'
    #     else:
    #         out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

    # # Converts message into/out of morse code
    # elif message.content.startswith('!morse'):
    #     parse = remove_command(message.content)
    #     out = Morse.main(parse)

    # elif message.content.startswith('!rockpaperscissors') or message.content.startswith('!rps'):
    #     if len(message.content.split(" ")) == 1:
    #         out = '`!rockpaperscISSors MOVE`'
    #     else:
    #         hand = remove_command(message.content)
    #         options = {"ROCK":":fist:", "PAPER":":hand_splayed:", "SCISSORS":":v:"}
    #         optionsList = list(options.keys())
    #         if hand.upper() not in optionsList:
    #             out = "You need to throw either rock, paper, or scISSors"
    #         else:
    #             playerIndex = optionsList.index(hand.upper())
    #             cpuIndex = random.randint(0, len(optionsList) - 1)
    #             sqlconn = sqlite3.connect('database.db')
    #             money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
    #             try:
    #                 user_money = money.fetchone()[0]
    #             except TypeError:
    #                 user_money = 0

    #             # They have the same play, it's a tie
    #             if cpuIndex == playerIndex:
    #                 out = "You both threw {}, it's a tie! {} = {}\nYou still have {} points".format(optionsList[cpuIndex].title(), options[optionsList[cpuIndex]], options[optionsList[cpuIndex]], user_money)
    #             # Player threw the weaker hand, they lose
    #             elif (playerIndex + 1) % 3 == cpuIndex:
    #                 user_money -= 10
    #                 out = "{} beats {}, you lose! {} < {}\nYou now have {} points".format(optionsList[cpuIndex].title(), optionsList[playerIndex].title(), options[optionsList[playerIndex]], options[optionsList[cpuIndex]], user_money)
    #             else:
    #                 user_money += 10
    #                 out = "{} beats {}, you win! {} > {}\nYou now have {} points".format(optionsList[playerIndex].title(), optionsList[cpuIndex].title(), options[optionsList[playerIndex]], options[optionsList[cpuIndex]], user_money)

    #             params = [message.author.id, user_money]
    #             sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    #             sqlconn.commit()
    #             sqlconn.close()

    # # Convert number into/out of roman numerals
    # elif message.content.startswith('!roman'):
    #     parse = message.content.split(" ")
    #     if message.content == '!roman':
    #         out = '!roman NUMBER/NUMERAL'
    #     elif parse[1].isalpha() == True:
    #         out = Roman.roman_to_int(parse[1])
    #     else:
    #         out = Roman.int_to_roman(parse[1])

    # # Returns scrabble value of given word
    # elif message.content.startswith('!scrabble'):
    #     parse = message.content.split(" ")
    #     if message.content == '!scrabble':
    #         out = '!scrabble WORD'
    #     else:
    #         out = Scrabble.scrabble(parse[1])

    # elif message.content.startswith('!slots'):
    #     sqlconn = sqlite3.connect('database.db')
    #     money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
    #     try:
    #         user_money = money.fetchone()[0]
    #     except TypeError:
    #         user_money = 0

    #     if message.content == '!slots info':
    #         out = "Play slots with Aquobot! Type '!slots' to bet your hard earned cash against chance!"
    #     else:
    #         earned, phrase, rolls = Slots.main()
    #         user_money += earned
    #         out = "You got {0}-{1}-{2}, so you earned {3} points. {4} You now have {5} points".format(rolls[0], rolls[1], rolls[2], earned, phrase, user_money)

    #         params = [message.author.id, user_money]
    #         sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    #     sqlconn.commit()
    #     sqlconn.close()

    # # elif message.content.startswith('!speedrun'):
    # #     q = remove_command(message.content)
    # #     if q.split(' ')[0].upper() == 'USER':
    # #         await Speedrun.user(remove_command(q), client, message)
    # #     else:
    # #         await Speedrun.game(q, client, message)

    # # elif message.content.startswith('!spellcheck'):
    # #     q = remove_command(message.content).replace(" ", "+")
    # #     sc_url = 'https://montanaflynn-spellcheck.p.mashape.com/check/?text=' + q
    # #     headers = {
    # #         "X-Mashape-Key": cfg['Client']['mashape'],
    # #         "Accept": "text/plain"
    # #     }

    # #     async with aiohttp.ClientSession() as session:
    # #         async with session.get(sc_url, headers=headers) as resp:
    # #             results = json.loads(resp.text())
    # #             out = "Suggestion: {}".format(results['suggestion'])

    # # elif message.content.startswith('!steam'):
    # #     if len(message.content.split(" ")) == 1:
    # #         out = "!steam USERNAME"
    # #     else:
    # #         q = remove_command(message.content)
    # #         info = Steam.get_userinfo(q)
    # #         if isinstance(info, list):
    # #             embed = discord.Embed(title=info[0], type='rich', description=info[2])
    # #             embed.add_field(name='User ID', value=info[1])
    # #             embed.set_thumbnail(url=info[3])
    # #             embed.add_field(name='Last Logged Off', value=info[4])
    # #             embed.add_field(name='Profile Created', value=info[5])
    # #             embed.add_field(name='Games Owned', value=info[6])
    # #             if len(info) > 8:
    # #                 embed.add_field(name='Games Played Last 2 Weeks', value=info[7])
    # #                 recent_info = "{0} ({1} hours, {2} hours total)".format(info[8], info[9], info[10])
    # #                 embed.add_field(name='Most Played Last 2 Weeks', value=recent_info)

    # #             await client.send_message(message.channel, embed=embed)
    # #         else:
    # #             out = info
    # #         # out = Steam.get_userinfo(q) <- The old method

    # # Displays the time for a user or location. Uses same database as weather
    # elif message.content.startswith('!time'):
    #     sqlconn = sqlite3.connect('database.db')
    #     author_id = int(message.author.id)
    #     author_name = message.author.name
    #     if message.content == '!time':
    #         user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
    #         try:
    #             query_location = user_loc.fetchone()[0]
    #             out = Weather.time(query_location)
    #         except TypeError:
    #             out = "!time [set] LOCATION"
    #     elif message.content.startswith("!time set"):
    #         q = message.content[9:]
    #         params = (author_id, author_name, q)
    #         sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
    #         out = "Location set as %s" % q
    #     else:
    #         q = remove_command(message.content)
    #         out = Weather.time(q)
    #     sqlconn.commit()
    #     sqlconn.close()

    # # Users can add/remove to their own todo list, and remove entries
    # elif message.content.startswith('!todo'):
    #     out = Todo.main(message.content, message.author.name, message.author.id, str(message.timestamp))

    # # elif (message.content.startswith('!tr') or message.content.startswith('!translate')):
    # #     if (message.content == '!tr' or message.content == '!translate'):
    # #         out = '!tr SOURCE_LANG MESSAGE'
    # #     else:
    # #         try:
    # #             dest_lang = message.content.split(" ")[1]
    # #             text = " ".join(message.content.split(" ")[2:])
    # #             if text == '^':
    # #                 async for mes in client.logs_from(message.channel, limit=10):
    # #                     if mes.content != message.content:
    # #                         text = mes.content
    # #                         break
    # #             tr = Translator()
    # #             new = tr.translate(text, dest=dest_lang)
    # #             out = new.text
    # #         except ValueError:
    # #             out = "Invalid destination language."

    # # elif message.content.startswith('!twitch'):
    # #     if message.content == '!twitch':
    # #         out = '!twitch USERNAME'
    # #     else:
    # #         q = remove_command(message.content)
    # #         twitch_url = 'https://api.twitch.tv/kraken/users?login={}'.format(q)

    # #         headers = {
    # #             "Client-ID": cfg['Client']['twitch'],
    # #             "Accept": "application/vnd.twitchtv.v5+json"
    # #         }

    # #         async with aiohttp.ClientSession() as session:
    # #             with session.get(twitch_url, headers=headers) as resp:
    # #                 results = json.loads(resp.text())
    # #                 if results['_total'] == 0:
    # #                     out = "There is no user by that name."
    # #                 else:
    # #                     username = results['users'][0]['name']
    # #                     user_url = 'https://www.twitch.tv/' + username
    # #                     embed = discord.Embed(title=results['users'][0]['display_name'], type='rich', description=user_url)
    # #                     embed.add_field(name='ID', value=results['users'][0]['_id'])
    # #                     embed.add_field(name='Bio', value=results['users'][0]['bio'])
    # #                     embed.add_field(name='Account Created', value=results['users'][0]['created_at'][:10])
    # #                     embed.add_field(name='Last Updated', value=results['users'][0]['updated_at'][:10])
    # #                     if results['users'][0]['logo'] == None:
    # #                         embed.set_thumbnail(url='https://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_70x70.png')
    # #                     else:
    # #                         embed.set_thumbnail(url=results['users'][0]['logo'])
    # #                     await client.send_message(message.channel, embed=embed)

    # # Prints given text upside down
    # elif message.content.startswith('!upside'):
    #     m = remove_command(message.content)
    #     out = Upside.down(m)

    # # Gives number of days until specified date
    # elif message.content.startswith('!until'):
    #     parse = message.content.split(" ")
    #     if message.content == '!until':
    #         out = '!until MM-DD-YYYY'
    #     else:
    #         out = str(Until.main(parse[1])) + " days"

    # # Returns with Wolfram Alpha result of query
    # elif message.content.startswith('!wolfram'):
    #     try:
    #         q = remove_command(message.content)
    #         res = waclient.query(q)
    #         out = next(res.results).text
    #     except AttributeError:
    #         out = "No results"

    # elif message.content.startswith('!wiki'):
    #     q = remove_command(message.content)
    #     out = Wikipedia.main(q)

    # # Returns with the weather of a specified location
    # # Needs to be the last 'w' command
    # elif (message.content.startswith('!weather') or message.content.startswith('!w')):
    #     sqlconn = sqlite3.connect('database.db')
    #     author_id = int(message.author.id)
    #     author_name = message.author.name
    #     if (message.content == '!weather' or message.content == '!w'):
    #         user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
    #         try:
    #             query_location = user_loc.fetchone()[0]
    #             out = Weather.main(query_location)
    #         except TypeError:
    #             out = "!weather [set] LOCATION"
    #     elif (message.content.startswith("!weather set") or message.content.startswith('!w set')):
    #         tmp = message.content.split(" ")[2:]
    #         q = " ".join(tmp)
    #         params = (author_id, author_name, q)
    #         sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
    #         out = "Location set as %s" % q
    #     else:
    #         try:
    #             q = remove_command(message.content)
    #             out = Weather.main(q)
    #         except TypeError:
    #             out = "No location found. Please be more specific."
    #     sqlconn.commit()
    #     sqlconn.close()

    # # Same as !weather, but prints emojis
    # elif message.content.startswith('!qw'):
    #     sqlconn = sqlite3.connect('database.db')
    #     author_id = int(message.author.id)
    #     author_name = message.author.name
    #     if message.content == '!qw':
    #         user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
    #         try:
    #             query_location = user_loc.fetchone()[0]
    #             out = Weather.emoji_weather(query_location)
    #         except TypeError:
    #             out = "!qw [set] LOCATION"
    #     elif message.content.startswith("!qw set"):
    #         q = message.content[7:]
    #         params = (author_id, author_name, q)
    #         sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
    #         out = "Location set as %s" % q
    #     else:
    #         q = remove_command(message.content)
    #         out = Weather.emoji_weather(q)
    #     sqlconn.commit()
    #     sqlconn.close()

    # elif (message.content.startswith('!youtube') or message.content.startswith('!yt')):
    #     q = remove_command(message.content)
    #     out = Youtube.search(q)

    # elif message.content.startswith('!xkcd'):
    #     out = XKCD.main(message.content)

    if out != "":
        print(out + '\n')

if __name__ == '__main__':
    print("Aquobot")
    while (True):
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
