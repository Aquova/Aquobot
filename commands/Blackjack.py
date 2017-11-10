import discord, sqlite3, random, asyncio

def hand_value(hand):
    total = 0
    for card in hand:
        if (card == 'K' or card == 'Q' or card == 'J'):
            total += 10
        elif card == 'A':
            if total + 11 > 21:
                total += 1
            else:
                total += 11
        else:
            total += int(card)
    return total

async def main(client, m):
    sqlconn = sqlite3.connect('database.db')
    money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [m.author.id])
    try:
        user_money = money.fetchone()[0]
    except TypeError:
        user_money = 0

    await client.send_message(m.channel, "Alright {}, time to play Blackjack!".format(m.author.name))

    # Someday replace this with player/dealer objects
    deck = [str(i) for i in range(2, 11)] * 4
    deck.extend([i for i in ['K', 'Q', 'J', 'A']] * 4)
    deck = random.sample(deck,len(deck))
    dealer = []
    player = []
    player.append(deck.pop())
    player.append(deck.pop())
    dealer.append(deck.pop())
    dealer.append(deck.pop())
    await client.send_message(m.channel, "Okay {}, you've drawn a {} and {}, for a total of {}".format(m.author.name, player[0], player[1], hand_value(player)))

    if hand_value(player) == 21:
        user_money += 150
        await client.send_message(m.channel, "{}: Blackjack!! You win! You now have {} points!".format(m.author.name, user_money))
        params = [m.author.id, user_money]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
    elif hand_value(dealer) == 21:
        user_money -= 100
        await client.send_message(m.channel, "{}: The dealer has a Blackjack, you lose. You now have {} points".format(m.author.name,user_money))
        params = [m.author.id, user_money]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
    else:
        dd = 1 # Double down multplier
        first = True # Is it the first draw? (For double down)
        while (hand_value(dealer) < 21 and hand_value(player) < 21):
            if first:
                await client.send_message(m.channel, "{}: Would you like to 'hit', 'stand', or 'double down' ('dd')?".format(m.author.name))
            else:
                await client.send_message(m.channel, "{}: Would you like to 'hit' or 'stand'?".format(m.author.name))

            msg = await client.wait_for_message(author=m.author, timeout=10)
            if msg == None:
                await client.send_message(m.channel, "{}: I'm sorry, but you have taken too long to respond".format(m.author.name))
                break
            elif msg.content.upper() == 'STAND':
                while hand_value(dealer) < 17:
                    dealer.append(deck.pop())
                break
            elif msg.content.upper() == 'HIT':
                first = False
                new_card = deck.pop()
                player.append(new_card)
                await client.send_message(m.channel, "{}: You drew a {}, your new total is {}".format(m.author.name,new_card, hand_value(player)))
                if hand_value(player) > 21:
                    break
                else:
                    continue
            elif ((msg.content.upper() == 'DOUBLE DOWN' or msg.content.upper() == 'DD') and first == True):
                new_card = deck.pop()
                player.append(new_card)
                dd = 2
                await client.send_message(m.channel, "{}: You've chosen to double down! You get one more card, and the bets are doubled.\nYou drew a {}, your new total is {}".format(m.author.name,new_card, hand_value(player)))
                if hand_value(player) > 21:
                    break
                else:
                    while hand_value(dealer) < 17:
                        dealer.append(deck.pop())
                    break
            else:
                await client.send_message(m.channel, "{}: That's not a valid answer, try again.".format(m.author.name))
                continue

        if hand_value(dealer) > 21:
            user_money += 50 * dd
            await client.send_message(m.channel, "{}: The dealer has gone over 21, you win! You now have {} points".format(m.author.name,user_money))
        elif hand_value(player) > 21:
            user_money -= 50 * dd
            await client.send_message(m.channel, "{}: You have gone over 21, you lose.. You now have {} points".format(m.author.name,user_money))
        elif hand_value(dealer) >= hand_value(player):
            user_money -= 50 * dd
            await client.send_message(m.channel, "{}: The dealer had {} while you had {}, you lose. You now have {} points".format(m.author.name,hand_value(dealer), hand_value(player), user_money))
        else:
            user_money += 50 * dd
            await client.send_message(m.channel, "{}: The dealer has {}, but you have {}! You win! You now have {} points".format(m.author.name,hand_value(dealer), hand_value(player), user_money))

        params = [m.author.id, user_money]
        sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    sqlconn.commit()
    sqlconn.close()
