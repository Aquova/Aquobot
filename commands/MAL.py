import discord, sqlite3, requests

def main(message):
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

    return out