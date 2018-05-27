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
import http, wolframalpha, json, random, sqlite3, datetime, urllib, time, requests
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
    if substring.upper() == phrase[:subLength].upper():
        return True
    return False

def printTitle():
    print("                         _           _   ")
    print("  __ _  __ _ _   _  ___ | |__   ___ | |_ ")
    print(" / _` |/ _` | | | |/ _ \| '_ \ / _ \| __|")
    print("| (_| | (_| | |_| | (_) | |_) | (_) | |_ ")
    print(" \__,_|\__, |\__,_|\___/|_.__/ \___/ \__|")
    print("")

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

    elif (startswith(userInput, "!brainfuck") or startswith(userInput, "!bf")):
        if len(userInput.split(" ")) == 1:
            out = '!brainfuck CODE\nInfo on the language: <https://learnxinyminutes.com/docs/brainfuck/>\nStill confused? Use this site to help visualize what is happening <http://bf.jamesliu.info/>'
        else:
            q = remove_command(userInput)
            if q[0] in '+-[]><.':
                out = BF.decode(q)
            else:
                out = BF.encode(q)

    # Chooses between given options
    elif startswith(userInput, "!choose"):
        if userInput == "!choose":
            out = "!choose OPTION1, OPTION2, OPTION3..."
        else:
            tmp = remove_command(userInput)
            choice = tmp.split(",")
            out = str(random.choice(choice))

    # Responds with .png image of text in "Ecco the Dolphin" style
    elif startswith(userInput, "!ecco"):
        if userInput == '!ecco':
            out = '!ecco PHRASE'
        else:
            q = remove_command(userInput)
            valid = Ecco.text(q)
            if valid == 'ERROR':
                out = 'That phrase used an invalid character. Please try again.'
            else:
                out = "Image generated."

    # Repeats back user message
    elif startswith(userInput, "!echo"):
        out = remove_command(userInput)

    # # Tells a 7 day forecast based on user or location. Uses same database as weather
    # elif (startswith(userInput, "!forecast") or startswith(userInput, "!f")):
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

    elif startswith(userInput, '!g'):
        q = remove_command(userInput)
        out = google.search(q)[0].link

    # elif message.content.startswith('!iss'):
    #     out = ISS.main(message.author.id)

    elif startswith(userInput, "!img"):
        if userInput == "!img":
            out = "!img QUERY"
        else:
            q = remove_command(userInput)
            params = {'q': q,
                'safe': 'on',
                'lr': 'lang_en',
                'hl': 'en',
                'tbm': 'isch'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
            }

            r = requests.get('https://google.com/search', params=params, headers=headers)
            if r.status_code == 200:
                root = ET.fromstring(r.text, ET.HTMLParser())
                foo = root.xpath(".//div[@class='rg_meta notranslate']")[0].text
                result = json.loads(foo)
                out = result['ou']
            else:
                out = "Google is unavailable I guess?\nError: {}".format(r.status_code)

    # Tells a joke from a pre-programmed list
    elif startswith(userInput, "!joke"):
        joke_list = Jokes.joke()
        pick_joke = random.choice(list(joke_list.keys()))
        out = joke_list[pick_joke]
        print(pick_joke)
        time.sleep(5)

    # Converts time into the Mayan calendar, why not
    elif startswith(userInput, "!mayan"):
        parse = userInput.split(" ")
        if userInput == '!mayan':
            out = '!mayan MM-DD-YYYY/TODAY'
        else:
            out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

    # Converts message into/out of morse code
    elif startswith(userInput, "!morse"):
        parse = remove_command(userInput)
        out = Morse.main(parse)

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

    # Convert number into/out of roman numerals
    elif startswith(userInput, "!roman"):
        parse = userInput.split(" ")
        if userInput == '!roman':
            out = '!roman NUMBER/NUMERAL'
        elif parse[1].isalpha() == True:
            out = str(Roman.roman_to_int(parse[1]))
        else:
            out = str(Roman.int_to_roman(parse[1]))

    # Returns scrabble value of given word
    elif startswith(userInput, "!scrabble"):
        parse = userInput.split(" ")
        if userInput == '!scrabble':
            out = '!scrabble WORD'
        else:
            out = str(Scrabble.scrabble(parse[1]))

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

    elif startswith(userInput, "!spellcheck"):
        q = remove_command(userInput).replace(" ", "+")
        sc_url = 'https://montanaflynn-spellcheck.p.mashape.com/check/?text=' + q
        headers = {
            "X-Mashape-Key": cfg['Client']['mashape'],
            "Accept": "text/plain"
        }

        r = requests.get(sc_url, headers=headers)
        results = json.loads(r.text)
        out = "Suggestion: {}".format(results['suggestion'])

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

    elif (startswith(userInput, "!tr") or startswith(userInput, "!translate")):
        if (userInput == '!tr' or userInput == '!translate'):
            out = '!tr SOURCE_LANG MESSAGE'
        else:
            try:
                dest_lang = userInput.split(" ")[1]
                text = " ".join(userInput.split(" ")[2:])
                tr = Translator()
                new = tr.translate(text, dest=dest_lang)
                out = new.text
            except ValueError:
                out = "Invalid destination language."

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

    # Prints given text upside down
    elif startswith(userInput, "!upside"):
        m = remove_command(userInput)
        out = Upside.down(m)

    # Gives number of days until specified date
    elif startswith(userInput, "!until"):
        parse = userInput.split(" ")
        if userInput == '!until':
            out = '!until MM-DD-YYYY'
        else:
            out = str(Until.main(parse[1])) + " days"

    # Returns with Wolfram Alpha result of query
    elif startswith(userInput, '!wolfram'):
        try:
            q = remove_command(userInput)
            res = waclient.query(q)
            out = next(res.results).text
        except AttributeError:
            out = "No results"

    elif startswith(userInput, "!wiki"):
        q = remove_command(userInput)
        out = Wikipedia.main(q)

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

    elif (startswith(userInput, "!youtube") or startswith(userInput, "!yt")):
        q = remove_command(userInput)
        out = Youtube.search(q)

    # elif message.content.startswith('!xkcd'):
    #     out = XKCD.main(message.content)

    if out != "":
        print(out + '\n')

if __name__ == '__main__':
    printTitle()
    while (True):
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
