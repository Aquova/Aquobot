# Slot machine mini-game for Aquobot
# Written by Austin Bricker, 2017

import random

symbols = ['Blue', 'Yellow', 'Bar', 'Black', 'Jackpot']
reels = 3

def main():
	roll = []
	for i in range(reels):
		roll.append(random.choice(symbols))

	if roll[0] == 'Jackpot':
		if roll[1] == 'Jackpot':
			# Two Jackpots plus...
			if roll[2] == 'Jackpot':
				win = 150
			elif roll[2] == 'Black':
				win = -100
			elif roll[2] == 'Blue':
				win = 120
			elif roll[2] == 'Yellow':
				win = 100
			else:
				win = 80
		elif roll[1] == roll[2] == 'Blue':
			win = 60
		elif roll[1] == roll[2] == 'Yellow':
			win = 50
		elif roll[1] == roll[2] == 'Bar':
			win = 40
		elif roll[1] == roll[2] == 'Black':
			win = -100
		else:
			win = -5
	elif roll[0] == roll[1] == roll[2] == 'Blue':
		win = 30
	elif roll[0] == roll[1] == roll[2] == 'Yellow':
		win = 25
	elif roll[0] == roll[1] == roll[2] == 'Bar':
		win = 20
	elif roll[0] == roll[1] == roll[2] == 'Black':
		win = -100
	elif (roll[0] == 'Bar' and roll[1] == 'Bar') or (roll[0] == 'Bar' and roll[2] == 'Bar') or (roll[1] == 'Bar' and roll[2] == 'Bar'):
		win = 10
	else:
		win = -5

	if win == 150:
		phrase = 'JACKPOT!!'
	elif 40 <= win < 150:
		phrase = 'Great job!'
	elif 2 <= win < 40:
		phrase = "Well, it's better than nothing."
	elif -5 <= win < 2:
		phrase = "Try again!"
	else:
		phrase = 'Oooo, bad luck!'

	return (win, phrase, roll)

