import sqlite3, discord

def main(m):
    sqlconn = sqlite3.connect('database.db')
    username = m.author.name
    userid = m.author.id
    timestamp = str(m.timestamp)
    time = timestamp.split(".")[0] + " GMT" # Right now, time is given in GMT. Possibly change to use local time instead.
    if m.content == '!todo':
        user_list = sqlconn.execute("SELECT * FROM todo WHERE userid=?", [userid])
        user_todos = user_list.fetchall()
        if user_todos == []:
            out = "You have not added anything to your todo list.\nAdd items with '!todo add item'"
        else:
            out = ""
            for item in user_todos:
                out += "{0} @ {1}. (#{2})".format(item[3], item[4], item[0]) + '\n'
    elif m.content.startswith('!todo add'):
        num = sqlconn.execute("SELECT COUNT(*) FROM todo") # WHERE userid IS NOT NULL")
        num = num.fetchone()[0] + 1
        mes = m.content[10:]
        params = (num, userid, username, mes, time)
        sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, m, t) VALUES (?, ?, ?, ?, ?)", params)
        out = "Item added by {0}: {1} @ {2}. (#{3})".format(username, mes, time, num)
    elif m.content.startswith('!todo remove'):
        try:
            remove_id = int(m.content[13:])
            check_user = sqlconn.execute("SELECT userid FROM todo WHERE id=?", [remove_id])
            check_user = str(check_user.fetchone()[0])
            if check_user == userid:
                sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, m, t) VALUES (?, NULL, NULL, NULL, NULL)", [remove_id])
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

    return out