# A program to play blackjack with the computer, as part of the aquobot program
# Written by Austin Bricker, 2017-2018

import discord, sqlite3, random, asyncio

class Deck:
    def __init__(self):
        self.deck = [str(i) for i in range(2, 11)] * 4
        self.deck.extend(['K', 'Q', 'J', 'A'] * 4)

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self, n):
        dealtCards = self.deck[0:n]
        self.deck = self.deck[n:]
        return dealtCards

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0

    def add(self, cards):
        self.cards.extend(cards)
        for card in cards:
            if (card == 'K' or card == 'Q' or card == 'J'):
                self.value += 10
            elif card == 'A':
                if self.value + 11 > 21:
                    self.value += 1
                else:
                    self.value += 11
            else:
                self.value += int(card)

async def main(client, m):
    # Check for user data in database
    sqlconn = sqlite3.connect('database.db')
    money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [m.author.id])
    try:
        userMoney = money.fetchone()[0]
    except TypeError:
        userMoney = 0

    await client.send_message(m.channel, "Alright {}, time to play Blackjack!".format(m.author.name))

    # Initialize deck and hands
    deck = Deck()
    deck.shuffle()
    dealer = Hand()
    player = Hand()

    dealer.add(deck.deal(2))
    player.add(deck.deal(2))

    await client.send_message(m.channel, "Okay {}, you've drawn a {} and {}, for a total of {}".format(m.author.name, player.cards[0], player.cards[1], player.value))

    # If player blackjacks, finished
    if player.value == 21:
        userMoney += 150
        await client.send_message(m.channel, "{}: Blackjack!! You win! You now have {} points!".format(m.author.name, userMoney))
        params = [m.author.id, userMoney]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
    # If dealer blackjacks, finished
    elif dealer.value == 21:
        userMoney -= 100
        await client.send_message(m.channel, "{}: The dealer has a Blackjack, you lose. You now have {} points".format(m.author.name,userMoney))
        params = [m.author.id, userMoney]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
    else:
        dd = 1                  # Double down multiplier, initialized at 1
        first = True            # Is it the first draw? (For double down)
        # While no player has passed 21, continue playing
        while (dealer.value < 21 and player.value < 21):
            if first:
                await client.send_message(m.channel, "{}: Would you like to 'hit', 'stand', or 'double down' ('dd')?".format(m.author.name))
            else:
                await client.send_message(m.channel, "{}: Would you like to 'hit' or 'stand'?".format(m.author.name))

            msg = await client.wait_for_message(author=m.author, timeout=10)
            if msg == None:
                await client.send_message(m.channel, "{}: I'm sorry, but you have taken too long to respond".format(m.author.name))
                break
            # If player stands, calculate dealers final score
            elif msg.content.upper() == 'STAND':
                # Dealer will always draw if under 17
                while dealer.value < 17:
                    dealer.add(deck.deal(1))
                break
            # If hit, then update player
            elif msg.content.upper() == 'HIT':
                first = False
                newCard = deck.deal(1)
                player.add(newCard)
                await client.send_message(m.channel, "{}: You drew a {}, your new total is {}".format(m.author.name, newCard[0], player.value))
                if player.value > 21:
                    break
            # Double down gives one more card, and multiplies points by 'dd' multiplier
            elif ((msg.content.upper() == 'DOUBLE DOWN' or msg.content.upper() == 'DD') and first == True):
                dd = 2
                newCard = deck.deal(1)
                player.add(newCard)
                await client.send_message(m.channel, "{}: You've chosen to double down! You get one more card, and the bets are doubled.\nYou drew a {}, your new total is {}".format(m.author.name, newCard[0], player.value))
                if player.value > 21:
                    break
                else:
                    while dealer.value < 17:
                        dealer.add(deck.deal(1))
                    break
            else:
                await client.send_message(m.channel, "{}: That's not a valid answer, try again.".format(m.author.name))

        # Send corresponding message regarding current user points
        if dealer.value > 21:
            userMoney += 50 * dd
            await client.send_message(m.channel, "{}: The dealer has gone over 21, you win! You now have {} points".format(m.author.name,userMoney))
        elif player.value > 21:
            userMoney -= 50 * dd
            await client.send_message(m.channel, "{}: You have gone over 21, you lose.. You now have {} points".format(m.author.name,userMoney))
        elif dealer.value > player.value:
            userMoney -= 50 * dd
            await client.send_message(m.channel, "{}: The dealer had {} while you had {}, you lose. You now have {} points".format(m.author.name, dealer.value, player.value, userMoney))
        elif dealer.value == player.value:
            await client.send_message(m.channel, "{}: The dealer had {} while you had {}, it's a draw! You still have {} points".format(m.author.name,dealer.value, player.value, userMoney))
        else:
            userMoney += 50 * dd
            await client.send_message(m.channel, "{}: The dealer has {}, but you have {}! You win! You now have {} points".format(m.author.name, dealer.value, player.value, userMoney))

        params = [m.author.id, userMoney]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    sqlconn.commit()
    sqlconn.close()
