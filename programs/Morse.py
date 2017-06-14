# This is a program that can encode and decode messages in Morse Code
# Written by Austin Bricker, 2015-2017

morse = {"A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.", "G":"--.", "H":"....", "I":"..", "J":".---", "K":"-.-", "L":".-..", "M":"--", "N":"-.", "O":"---", "P":".--.", "Q":"--.-", "R":".-.", "S":"...", "T":"-", "U":"..-", "V":"...-", "W":".--", "X":"-..-", "Y":"-.--", "Z":"--..", ".":".-.-.-", ",":"--..--", "?":"..--..", "@":".--.-.", ":":"---...", "-":"-....-", "'":".----.", "1":".----", "2":"..---", "3":"...--", "4":"....-", "5":".....", "6":"-....", "7":"--...", "8":"---..", "9":"----.", "0":"-----", " ":"/ "}

def decode(stuff):
    final = ""
    char = stuff.split()
    rev_morse = {v: k for k, v in morse.items()}

    for item in char:
        if item != " ":
            final = final + rev_morse[item]
        else:
            final = final + " "
    return final

def encode(stuff):
    final = ""
    for letter in stuff:
        final = final + morse[letter.upper()] + " "
    return final
