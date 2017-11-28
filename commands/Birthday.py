import sqlite3, asyncio, sqlite3, datetime, discord

months = {'JANUARY':1, 'JAN':1, 'FEB':2, 'FEBRUARY':2, 'MARCH':3, 'MAR':3, 'APRIL':4, 'APR':4, 'MAY':5, 'JUNE':6, 'JUN':6, 'JULY':7, 'JUL':7, 'AUGUST':8, 'AUG':8, 'SEPTEMBER':9, 'SEPT':9, 'OCTOBER':10, 'OCT':10, 'NOVEMBER':11, 'NOV':11, 'DECEMBER':12, 'DEC':12}
reverse = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

async def check_birthday(client):
    sqlconn = sqlite3.connect('database.db')
    birthdays = sqlconn.execute("SELECT * FROM birthday").fetchall()

    d = datetime.date.today()
    month = d.month
    day = d.day
    bday_names = []
    bday_ids = []
    if birthdays != None:
        for i in range(0, len(birthdays)):
            try:
                if (month == int(birthdays[i][2]) and day == int(birthdays[i][3])):
                    bday_names.append(birthdays[i][1])
                    bday_ids.append(birthdays[i][0])
            except ValueError as e:
                print("Error handled: " + e)
                pass
    else:
        print("birthdays is null apparently")

    if bday_ids != []:
        for j in range(0, len(bday_ids)):
            for server in client.servers:
                ids = [x.id for x in server.members]
                if str(bday_ids[j]) in ids:
                    mess = "Today is {}'s birthday! Everybody wish them a happy birthday! :birthday:".format(bday_names[j])
                    print(mess)
                    await client.send_message(server.default_channel, mess)

    sqlconn.commit()
    sqlconn.close()

def main(m):
    sqlconn = sqlite3.connect('database.db')
    if m.content == '!birthday':
        birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [m.author.id])
        birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [m.author.id])
        try:
            query_month = birth_month.fetchone()[0]
            query_day = birth_day.fetchone()[0]
            out = "Your birthday is {0} {1}".format(reverse[int(query_month)], query_day)
        except TypeError:
            out = "!birthday [set] MONTH DAY"
    elif m.content.startswith('!birthday set'):
        q = m.content.split(" ")[2:]
        try:
            if (1 <= int(q[1]) and int(q[1]) <= 31):
                if q[0].upper() in months.keys():
                    params = (m.author.id, m.author.name, months[q[0].upper()], int(q[1]), m.server.id)
                    sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day, server_id) VALUES (?, ?, ?, ?, ?)", params)
                    out = "{0}'s birthday now set as {1}/{2}".format(m.author.name, months[q[0].upper()], q[1])
                elif (1 <= int(q[0]) and int(q[0]) <= 12):
                    params = (m.author.id, m.author.name, int(q[0]), int(q[1]), m.server.id)
                    sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day, server_id) VALUES (?, ?, ?, ?, ?)", params)
                    out = "{0}'s birthday now set as {1}/{2}".format(m.author.name, q[0], q[1])
                else:
                    out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
            else:
                out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
        except ValueError:
            out = "Invalid birthday format. The format needs to be !birthday set MONTH DAY"
    elif m.content.startswith('!birthday list'):
        birth_ids = sqlconn.execute("SELECT id FROM birthday").fetchall()
        out = ""
        ids = [x.id for x in m.server.members]
        for user in birth_ids:
            if str(user[0]) in ids:
                # Someday clean this up
                birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                birth_name = sqlconn.execute("SELECT name FROM birthday WHERE id=?", [user[0]]).fetchone()[0]
                out += "{0}'s birthday is on {1} {2}\n".format(birth_name, reverse[int(birth_month)], birth_day)
        if out == "":
            out = "There are no birthdays entered for anyone on this server."
    else:
        q = " ".join(m.content.split(" ")[1:])
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

    return out
