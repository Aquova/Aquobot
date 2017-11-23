import discord, sqlite3, asyncio

async def main(client, message):
    sqlconn = sqlite3.connect('database.db')
    if len(message.content.split(" ")) == 1:
        userinfo = sqlconn.execute("SELECT code FROM acpc WHERE userid=?", [message.author.id,])
        try:
            out = userinfo.fetchone()[0]
        except TypeError:
            out = "!acpc [set] USERNAME"
    elif message.content.split(" ")[1].upper() == "SET":
        code = " ".join(message.content.split(" ")[2:])
        params = [message.author.id, code]
        sqlconn.execute("INSERT OR REPLACE INTO acpc (userid, code) VALUES (?, ?)", params)
        out = "Friend code added."
    else:
        q = " ".join(m.content.split(" ")[1:])
        try:
            member = discord.utils.get(message.server.members, name=q)
            code = sqlconn.execute("SELECT code FROM acpc WHERE username=?", [member.id])
            out = 'Their code is: ' + birth_month.fetchone()[0]
        except:
            out = "Error: No code for that user (searches are case sensitive)."
    sqlconn.commit()
    sqlconn.close()

    await client.send_message(message.channel, out)
