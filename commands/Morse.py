# This is a program that can encode and decode messages in Morse Code
# Written by Austin Bricker, 2015-2017

morse = {"A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.", "G":"--.", "H":"....",
         "I":"..", "J":".---", "K":"-.-", "L":".-..", "M":"--", "N":"-.", "O":"---", "P":".--.",
         "Q":"--.-", "R":".-.", "S":"...", "T":"-", "U":"..-", "V":"...-", "W":".--", "X":"-..-",
         "Y":"-.--", "Z":"--..", ".":".-.-.-", ",":"--..--", "?":"..--..", "@":".--.-.", ":":"---...",
         "-":"-....-", "'":".----.", "1":".----", "2":"..---", "3":"...--", "4":"....-", "5":".....",
         "6":"-....", "7":"--...", "8":"---..", "9":"----.", "0":"-----", " ":"/ "}

def main(msg):
    final = ""
    if (msg[0] == '.' or msg[0] == '-'):
        char = msg.split()
        rev_morse = {v: k for k, v in morse.items()}
        for item in char:
            if item != " " and item in rev_morse:
                final += rev_morse[item]
            else:
                final += " "
    else:
        for letter in msg:
            if letter.upper() in morse:
                final += morse[letter.upper()] + " "

    return final
