import sqlite3, discord, random

def remove_command(m):
    tmp = m.split(" ")[1:]
    return " ".join(tmp)

def main(message):
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

    else:
        try:
            q = int(remove_command(message.content))
            quote = sqlconn.execute("SELECT * FROM quotes WHERE num=?", [q]).fetchall()              
        except ValueError:
            q = str(remove_command(message.content))
            quote = sqlconn.execute("SELECT * FROM quotes WHERE username=?", [q]).fetchall()

        try:
            chosen = random.choice(quote)
            num = chosen[0]
            text = chosen[1]
            username = chosen[2]
            out = 'From {0}: "{1}" (#{2})'.format(username, text, str(num))
        except IndexError:
            out = "No quote matched that query."
    sqlconn.commit()
    sqlconn.close()

    return out
