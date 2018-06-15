"""
An "offline" CLI for Aquobot
Designed to allow me to use some of Aquobot's functions from a terminal, without a Discord client
Written by aquova, 2018
"""

from googletrans import Translator
from google import google
import lxml.etree as ET
import sys, wolframalpha, json, random, sqlite3, datetime, requests, os
from time import sleep
from commands.Utils import remove_command, startswith

from commands import Help, Select, BF, Ecco, Weather, Jokes, Mayan, Morse, Roman, Scrabble, Todo, Upside, Until, Wikipedia, Youtube, XKCD, Slots

with open(os.path.join(sys.path[0], 'config.json')) as json_data_file:
    cfg = json.load(json_data_file)

wolframKey = str(cfg['Client']['wolfram'])
waclient = wolframalpha.Client(wolframKey)

dbPath = os.path.join(os.path.dirname(__file__), "cli.db")
sqlconn = sqlite3.connect(dbPath)
sqlconn.execute("CREATE TABLE IF NOT EXISTS todo (id INT PRIMARY KEY, message TEXT, t TEXT);")
sqlconn.commit()
sqlconn.close()

def printTitle():
    print("                         _           _   ")
    print("  __ _  __ _ _   _  ___ | |__   ___ | |_ ")
    print(" / _` |/ _` | | | |/ _ \| '_ \ / _ \| __|")
    print("| (_| | (_| | |_| | (_) | |_) | (_) | |_ ")
    print(" \__,_|\__, |\__,_|\___/|_.__/ \___/ \__|")
    print("By aquova")
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

    # Tells a 7 day forecast based on specified location
    elif (startswith(userInput, "!forecast") or startswith(userInput, "!f")):
        try:
            q = remove_command(userInput)
            out = Weather.forecast(q)
        except TypeError:
            out = "No location found. Please be more specific."

    elif startswith(userInput, '!g'):
        q = remove_command(userInput)
        out = google.search(q)[0].link

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
        sleep(5)

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

    elif startswith(userInput, "!rockpaperscissors") or startswith(userInput, "!rps"):
        if len(userInput.split(" ")) == 1:
            out = '`!rockpaperscissors MOVE`'
        else:
            hand = remove_command(userInput)
            optionsList = ["ROCK", "PAPER", "SCISSORS"]
            if hand.upper() not in optionsList:
                out = "You need to throw either rock, paper, or scissors"
            else:
                playerIndex = optionsList.index(hand.upper())
                cpuIndex = random.randint(0, len(optionsList) - 1)

                # They have the same play, it's a tie
                if cpuIndex == playerIndex:
                    out = "You both threw {}, it's a tie!".format(optionsList[cpuIndex].title())
                # Player threw the weaker hand, they lose
                elif (playerIndex + 1) % 3 == cpuIndex:
                    out = "{} beats {}, you lose!".format(optionsList[cpuIndex].title(), optionsList[playerIndex].title())
                else:
                    out = "{} beats {}, you win!".format(optionsList[playerIndex].title(), optionsList[cpuIndex].title())

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

    elif startswith(userInput, "!slots"):
        if userInput == '!slots info':
            out = "Play slots with Aquobot! Type '!slots' to bet your hard earned cash against chance!"
        else:
            earned, phrase, rolls = Slots.main()
            out = "You got {0}-{1}-{2}, so you earned {3} points. {4}".format(rolls[0], rolls[1], rolls[2], earned, phrase)

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


    # Displays the time for a user or location.
    elif startswith(userInput, "!time"):
        q = remove_command(userInput)
        out = Weather.time(q)

    # Users can add/remove to their own todo list, and remove entries
    elif startswith(userInput, "!todo"):
        sqlconn = sqlite3.connect('cli.db')
        time = str(datetime.datetime.now()).split(".")[0] + " GMT"
        if userInput == '!todo':
            user_todos = sqlconn.execute("SELECT * FROM todo").fetchall()
            if user_todos == []:
                out = "You have not added anything to your todo list.\nAdd items with '!todo add item'"
            else:
                out = ""
                for item in user_todos:
                    out += "{} @ {}. (#{})".format(item[1], item[2], item[0])
        elif startswith(userInput, "!todo add"):
            num = sqlconn.execute("SELECT COUNT(*) FROM todo")
            num = num.fetchone()[0] + 1
            mes = remove_command(remove_command(userInput))
            params = (num, mes, time)
            sqlconn.execute("INSERT OR REPLACE INTO todo (id, message, t) VALUES (?, ?, ?)", params)
            out = "Item added: {} @ {}. (#{})".format(mes, time, num)
        elif startswith(userInput, '!todo remove'):
            try:
                mes = remove_command(remove_command(userInput))
                remove_id = int(mes)
                sqlconn.execute("DELETE FROM todo WHERE id=?", [remove_id])
                out = "Item {} removed".format(remove_id)
            except TypeError:
                out = "There is no entry of that index value"
            except ValueError:
                out = "That's not a number. Please specify the index number of the item to remove."
        else:
            out = "!todo [add/remove]"
        sqlconn.commit()
        sqlconn.close()

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

    # Returns with the weather of a specified location
    # Needs to be the last 'w' command
    elif (startswith(userInput, "!weather") or startswith(userInput, "!w")):
        try:
            q = remove_command(userInput)
            out = Weather.main(q)
        except TypeError:
            out = "No location found. Please be more specific."

    elif (startswith(userInput, "!youtube") or startswith(userInput, "!yt")):
        q = remove_command(userInput)
        out = Youtube.search(q)

    elif startswith(userInput, '!xkcd'):
        out = XKCD.main(userInput)

    if out != "":
        print(out + '\n')

if __name__ == '__main__':
    printTitle()
    while (True):
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
