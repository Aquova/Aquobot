# This is a program that will play 2P checkers.
# Written by Austin Bricker, 2016

# This section creates the playing board.
board = []
board.append(['0', 'X'] * 4)
board.append(['X', '0'] * 4)
for i in range(0,4):
    board.append(['X'] * 8)
board.append(['O', 'X'] * 4)
board.append(['X', 'O'] * 4)

# A function that will print the board with the correct formatting.
def print_board(board):
    i = 8
    for line in board:
    	print str(i) + " " + " ".join(line) # Modify to remove row nums
	i = i - 1
    print "  a b c d e f g h" + "\n" # Adds column nums

print("O represents red's pieces, 0 is black's pieces, and X's are empty spaces.")
print("Q is red's 'kinged' pieces, 8 is black's" + '\n')    	
red = True
print_board(board)

# "Letter to number": converts column letters into integer
def l2n(x):
    return ord(x) - 97

# This function checks if the move is a valid checker move
def test_move(row1, col1, row2, col2, red):
    if (0 <= col1 < 8) and (0 <= col2 < 8) and (0 <= row1 < 8) and (0 <= row2 < 8):
        if (col2 == col1 + 1) or (col2 == col1 - 1):
            if board[row2][col2] == "X":
                if (row2 == row1 - 1) and (red == True):
                    if (board[row1][col1] == "O") or (board[row1][col1] == "Q"):
                        return True
                elif (red == True) and (row2 == row1 + 1):
                    if board[row1][col1] == "Q":
                        return True
                elif (row2 == row1 + 1) and (red != True):
                    if (board[row1][col1] == "0") or (board[row1][col1] == "8"):    
                        return True
                elif (red != True) and (row2 == row1 - 1):
                    if board[row1][col1] == "8":
                        return True

# This function tests whether a "jump" move is possible
def test_jump(row1, col1, row2, col2, red):
    midcol = (col2 + col1) / 2
    midrow = (row2 + row1) / 2
    if (0 <= col1 < 8) and (0 <= col2 < 8) and (0 <= row1 < 8) and (0 <= row2 < 8):
        if board[row2][col2] == "X":
            if (board[midrow][midcol] != "X"):
                if (red == True) and (row2 == row1 - 2):
                    if (board[row1][col1] == "O") or (board[row1][col1] == "Q"):
                        return True
                elif (red == True) and (row2 == row1 + 2):
                    if board[row1][col1] == "Q":
                        return True
                elif (red != True) and (row2 == row1 + 2):
                    if (board[row1][col1] == "0") or (board[row1][col1] == "8"):
                        return True  
                elif (red != True) and (row2 == row1 - 2):
                    if board[row1][col1] == "8":
                        return True

# This function 'kings' a piece if they make it across the board.
def king_me(row1, col1, row2, col2, red):
    if (red == True) and (row2 == 0):
        return True
    elif (red != True) and (row2 == 7):
        return True

while True:
    if red == True:
    	print("It is red's turn.")
    else:
    	print("It is black's turn.")
    move = raw_input("Please enter a valid move (Current location first, then desired location): ")
    print("")
    if move.upper() == "EXIT":
    	break

    move = move.split(" ")    
    origin = move[0]
    col1 = int(l2n(origin[0]))
    row1 = 8 - int(origin[1])
    # print("col1: " + str(col1))
    # print("row1: " + str(row1))
        
    target = move[1]
    col2 = int(l2n(target[0]))
    row2 = 8 - int(target[1])
    # print("col2: " + str(col2))
    # print("row2: " + str(row2))
    
    if test_jump(row1, col1, row2, col2, red) == True:
        midrow = (row2 + row1) / 2
        midcol = (col2 + col1) / 2
        # print("midcol: " + str(midcol))
        # print("midrow: " + str(midrow))
        board[row2][col2] = board[row1][col1]
        board[row1][col1] = "X"
        board[midrow][midcol] = "X"
        if king_me(row1, col1, row2, col2, red) == True:
            if red == True:
                board[row2][col2] = "Q"
            else: 
                board[row2][col2] = "8"
        red = not red
    elif test_move(row1, col1, row2, col2, red) == True:
        board[row2][col2] = board[row1][col1]
        board[row1][col1] = "X"
        if king_me(row1, col1, row2, col2, red) == True:
            if red == True:
                board[row2][col2] = "Q"
            else:
                board[row2][col2] = "8"
        red = not red
    else:
        print("That is not a valid move, try again.")
    
    print_board(board)    
