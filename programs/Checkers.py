# This is a program that will play 2P checkers in Discord.
# Written by Austin Bricker, 2016-2017

board = []
board.append([':black_large_square:', ':red_circle:'] * 4)
board.append([':red_circle:', ':black_large_square:'] * 4)
for i in range(0,2):
    board.append([':black_large_square:', ':white_large_square:'] * 4)
    board.append([':white_large_square:', ':black_large_square:'] * 4)
board.append([':large_blue_circle:', ':white_large_square:'] * 4)
board.append([':white_large_square:', ':large_blue_circle:'] * 4)
num_emoji = {1:"1⃣", 2:"2⃣", 3:"3⃣", 4:"4⃣", 5:"5⃣", 6:"6⃣", 7:"7⃣", 8:"8⃣", 9:"9⃣"}

def print_board(board):
	out = ""
	i = 8
	for line in board:
		out = out + str(num_emoji[i]) + " " + "".join(line) + '\n'
		i = i - 1
	out = out + ":star: " + ":regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d::regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h:"
	return out

def main():
	return print_board(board)