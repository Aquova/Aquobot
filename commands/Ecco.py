# This is a program that will take in user input and output an image of that text in the style of the text in 'Ecco the Dolphin'
# Written by Austin Bricker, 2017-2018

import os
from PIL import Image

unusualLetters = {"M": 24, "W": 24, "X": 18}

max_row_len = 18
x_margin = 16
y_margin = 26

def centerText(row):
    c = 160
    for letter in row:
        if letter.upper() in list(unusualLetters.keys()):
            c -= unusualLetters[letter.upper()] // 2
        else:
            c -= x_margin / 2
    return int(c)

def text(sentence):
    words = sentence.split(" ")
    new_rows = []
    new_line = words[0]
    if len(words) == 1:
        new_rows.append(new_line)
    else:
        for i in range(1,len(words)):
            if len(new_line) + len(words[i]) < max_row_len:
                new_line += " " + words[i]
            else:
                new_rows.append(new_line)
                new_line = words[i]

            if i == (len(words) - 1):
                new_rows.append(new_line)

    bg_path = os.path.join(os.path.dirname(__file__), 'EccoBackground.png')
    bg = Image.open(bg_path)
    row_num = 0
    y_pos = 132 - (len(new_rows) * y_margin // 2)
    for row in new_rows:
        x_pos = centerText(row)
        for letter in row:
            try:
                if letter == " ": # Behavior if space
                    x_pos += x_margin
                else:
                    if letter == '.':
                        letter = 'dot'
                    elif letter == ':':
                        letter = 'colon'
                    fg_path = os.path.join(os.path.dirname(__file__), 'EccoFont', '{}.png'.format(letter.upper())) # Behavior if a valid letter
                    fg = Image.open(fg_path)
                    width, height = fg.size
                    bg.paste(fg, (x_pos, y_pos), fg)
                    x_pos += width + 2
                    fg.close()
            except FileNotFoundError:
                return 'ERROR'
        row_num += 1
        y_pos += y_margin
    out_path = os.path.join(os.path.dirname(__file__), 'ecco.png')
    bg.save(out_path)
    bg.close()
