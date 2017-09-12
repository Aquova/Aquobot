import sqlite3

months = {'JANUARY':1, 'JAN':1, 'FEB':2, 'FEBRUARY':2, 'MARCH':3, 'MAR':3, 'APRIL':4, 'APR':4, 'MAY':5, 'JUNE':6, 'JUN':6, 'JULY':7, 'JUL':7, 'AUGUST':8, 'AUG':8, 'SEPTEMBER':9, 'SEPT':9, 'OCTOBER':10, 'OCT':10, 'NOVEMBER':11, 'NOV':11, 'DECEMBER':12, 'DEC':12}
reverse = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

def main(m, author_name, author_id, server_id):
    sqlconn = sqlite3.connect('database.db')
    if m == '!birthday':
        birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [author_id])
        birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [author_id])
        try:
            query_month = birth_month.fetchone()[0]
            query_day = birth_day.fetchone()[0]
            out = "Your birthday is {0} {1}".format(reverse[int(query_month)], query_day)
        except TypeError:
            out = "!birthday [set] MONTH DAY"
    elif m.startswith('!birthday set'):
        q = m.split(" ")[2:]
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
    elif m.startswith('!birthday list'):
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
        q = remove_command(m)
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