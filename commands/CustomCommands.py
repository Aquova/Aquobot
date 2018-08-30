# A function where users can add their own simple text commands
import sqlite3

class Commands:
    def __init__(self):
        self.phrases = {}
        self.generate()

    def generate(self):
        sqlconn = sqlite3.connect('database.db')
        cc = sqlconn.execute("SELECT * FROM commands").fetchall()
        for p in cc:
            self.phrases[p[0]] = p[1]
        sqlconn.close()

    def add(self, phrase, command):
        sqlconn = sqlite3.connect('database.db')
        sqlconn.execute("INSERT OR REPLACE INTO commands (phrase, response) VALUES (?, ?)", [phrase, command])
        self.phrases[phrase] = command
        sqlconn.commit()
        sqlconn.close()

    def keywords(self):
        return self.phrases
