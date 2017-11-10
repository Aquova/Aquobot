import discord, sqlite3, random, asyncio

# This program is a bit of a mess, and could probably be cleaned up someday.
async def main(client, message):
    basic_bet = 10
    sqlconn = sqlite3.connect('database.db')
    money = sqlconn.execute("SELECT value FROM points WHERE userid=?", [message.author.id])
    try:
        user_money = money.fetchone()[0]
    except TypeError:
        user_money = 0

    # Bets are calculated by number of numbers being bet on, n
    # Payout: basic_bet * ((36 / n) - 1)
    wheel = ['00'] + [str(n) for n in range(0,37)]
    ball = random.choice(wheel)
    red = ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34', '36']
    black = list(set(wheel) - set(red + ['0', '00']))
    dozen = [[str(c) for c in range(1,13)], [str(c) for c in range(13,25)], [str(c) for c in range(25,37)]]
    half = [[str(c) for c in range(1,19)], [str(c) for c in range(19,37)]]

    await client.send_message(message.channel, "Red: 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36\nBlack: 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35")
    options = "Time to play roulette! Input the number you'd like to bet on:\n1. A single number\n2. 0 and 00\n3. Odds\n4. Evens (excludes 0 and 00)\n5. Reds\n6. Blacks\n7. A dozen\n8. Half"
    await client.send_message(message.channel, options)
    msg = await client.wait_for_message(author=message.author, timeout=10)

    if msg == None:
        out = 'You have taken too long to respond, please try again.'

    # Single number
    elif msg.content == '1':
        await client.send_message(message.channel, 'Which number would you like to bet on?')
        choice = await client.wait_for_message(author=message.author, timeout=10)
        if choice.content in wheel:
            await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
            if choice.content == ball:
                user_money += basic_bet * 35
                await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
            else:
                user_money -= basic_bet * 35
                await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            await client.send_message(message.channel, "That's not a number on the wheel... Please try again.")

    # 0 or 00
    elif msg.content == '2':
        await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
        if ball in ['0', '00']:
            user_money += basic_bet * 17
            await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            user_money -= basic_bet * 17
            await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    # Odds
    elif msg.content == '3':
        await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
        if int(ball) % 2 == 1:
            user_money += basic_bet * 1
            await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            user_money -= basic_bet * 1
            await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    # Evens
    elif msg.content == '4':
        await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
        if int(ball) % 2 == 0 and int(ball) != 0:
            user_money += basic_bet * 1
            await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            user_money -= basic_bet * 1
            await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    # Red
    elif msg.content == '5':
        await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
        if ball in red:
            user_money += basic_bet * 1
            await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            user_money -= basic_bet * 1
            await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    # Black
    elif msg.content == '6':
        await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
        if ball in black:
            user_money += basic_bet * 1
            await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            user_money -= basic_bet * 1
            await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
            params = [message.author.id, user_money]
            sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)

    # Dozen
    elif msg.content == '7':
        await client.send_message(message.channel, 'Okay, which dozen?\n1. 1-12\n2. 13-24\n3. 25-36')
        choice = await client.wait_for_message(author=message.author, timeout=10)
        if choice.content in [str(c) for c in range(1,4)]:
            await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
            if ball in dozen[int(choice.content) - 1]:
                user_money += basic_bet * 2
                await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
            else:
                user_money -= basic_bet * 2
                await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            await client.send_message(message.channel, 'That is not a valid option. Please try again.')

    # Halves
    elif msg.content == '8':
        await client.send_message(message.channel, 'Okay, which half of the numbers?\n1. 1-18\n2. 19-36')
        choice = await client.wait_for_message(author=message.author, timeout=10)
        if choice.content in [str(c) for c in range(1,3)]:
            await client.send_message(message.channel, 'Spinning the wheel! The ball landed on {}'.format(ball))
            if ball in half[int(choice.content) - 1]:
                user_money += basic_bet * 1
                await client.send_message(message.channel, 'You win!! Your new score is {}'.format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
            else:
                user_money -= basic_bet * 1
                await client.send_message(message.channel, "I'm sorry, you lose. Your new score is {}".format(user_money))
                params = [message.author.id, user_money]
                sqlconn.execute("INSERT OR REPLACE INTO points (userid, value) VALUES (?, ?)", params)
        else:
            await client.send_message(message.channel, 'That is not a valid option. Please try again.')

    else:
        out = 'That is not a valid answer, please try again.'

    sqlconn.commit()
    sqlconn.close()
