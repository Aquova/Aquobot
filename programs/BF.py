# This is a Brainfuck Interpreter, written for the Aquobot program
# Written by Austin Bricker, 2017
def decode(code):
    cells = [0]
    cellPointer = 0
    codePointer = 0
    output = ''
    totalLoops = 0

    while codePointer < len(code):
        totalLoops += 1
        if totalLoops > 10000:
            output = "Either your code takes a long time to process or it has an infinite loop. Either way, it's being terminated."
            break

        if code[codePointer] == "+":
            cells[cellPointer] += 1
            if cells[cellPointer] > 255:
                cells[cellPointer] = 0

        elif code[codePointer] == "-":
            cells[cellPointer] -= 1
            if cells[cellPointer] < 0:
                cells[cellPointer] = 255

        elif code[codePointer] == ">":
            cellPointer += 1
            if cellPointer == len(cells):
                cells.append(0)

        elif code[codePointer] == "<":
            if cellPointer > 0:
                cellPointer -= 1

        elif code[codePointer] == "[":
            # If value at zero aka last run of loop
            if code[codePointer] == 0:
                openBraces = 1
                # This finds the corresponding ending brace
                # Accounts for nested loops
                while openBraces > 0:
                    codePointer += 1
                    if code[codePointer] == '[':
                        openBraces += 1
                    elif code[codePointer] == ']':
                        openBraces -= 1

        elif code[codePointer] == ']':
            # If the cell value hasn't reached zero, back up to the corresponding brace
            if cells[cellPointer] != 0:
                openBraces = 1
                while openBraces > 0:
                    codePointer -= 1
                    if code[codePointer] == '[':
                        openBraces -= 1
                    elif code[codePointer] == ']':
                        openBraces += 1

        elif code[codePointer] == '.':
            output += chr(cells[cellPointer])

        codePointer += 1

    return output

divisor = 10 # The 'counting' factor

def ord2bfPos(val):
    factor = val / divisor
    remainder = val % divisor
    if int(factor) != 0:
        return ("+" * divisor) + '[>' + ("+" * int(factor)) + '<-]>' + ('+' * remainder) + '.'
    else:
        return ('+' * remainder) + '.'

def ord2bfNeg(val):
    factor = -val / divisor
    remainder = -val % divisor
    if int(factor) != 0:
        return ("+" * divisor) + '[>' + ("-" * int(factor)) + '<-]>' + ('-' * remainder) + '.'
    else:
        return ('-' * remainder) + '.'

def encode(code):
    output = ''
    for i in range(len(code)):
        if i == 0:
            output += ord2bfPos(ord(code[i]))
        else:
            diff = ord(code[i]) - ord(code[i - 1])
            if abs(diff) > divisor:
                output += '<'

            if diff >= 0:
                output += ord2bfPos(diff)
            else:
                output += ord2bfNeg(diff)

    return "```brainfuck\n{}\n```".format(output)

if __name__ == '__main__':
    word = input("Say a phrase: ")
    print(encode(word))
