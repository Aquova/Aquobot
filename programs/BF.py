# This is a Brainfuck Interpreter, written for the Aquobot program
# Written by Austin Bricker, 2017

def decode(code):
    cells = [0]
    cellPointer = 0
    codePointer = 0
    output = ''

    while codePointer < len(code):
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

def encode(code):
    return "This isn't working yet, sorry."
    # Implementation here: https://codegolf.stackexchange.com/questions/5418/brainf-golfer/5440#5440
