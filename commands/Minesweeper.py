from random import randint

class Minesweeper:
    def __init__(self, boardSize=10, bombNum=15):
        self.emojis = {"X": ":bomb:", 0: ":zero:", 1: ":one:", 2: ":two:", 3: ":three:", 4: ":four:", 5: ":five:", 6: ":six:", 7: ":seven:", 8: ":eight:", 9: ":nine:"}
        self.size = boardSize
        self.bombs = bombNum

    def generate(self):
        self.board = [[0 for y in range(self.size)] for x in range(self.size)]
        b_remaining = self.bombs
        while b_remaining > 0:
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)
            if self.board[y][x] == 0:
                self.board[y][x] = "X"
                b_remaining -= 1

        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                self.calcNeighbors(x, y)

    def calcNeighbors(self, x, y):
        if self.board[y][x] == "X":
            return

        total = 0
        for nx in range(-1, 2): # Note that this is -1, 0, 1
            for ny in range(-1, 2):
                if ((x + nx >= 0) and (x + nx < self.size)) and ((y + ny >= 0) and (y + ny < self.size)):
                    if self.board[y+ny][x+nx] == "X":
                        total += 1

        self.board[y][x] = total

    def getBoard(self):
        output = []
        for row in self.board:
            rowText = ""
            for cell in row:
                rowText += "||{}|| ".format(self.emojis[cell])
            output.append(rowText)

        return output

if __name__ == "__main__":
    ms = Minesweeper()
    ms.generate()
    print(ms.getBoard())

