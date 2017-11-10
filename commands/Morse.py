# This is a program that can encode and decode messages in Morse Code
# Written by Austin Bricker, 2015-2017

morse = {"A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.", "G":"--.", "H":"....", 
         "I":"..", "J":".---", "K":"-.-", "L":".-..", "M":"--", "N":"-.", "O":"---", "P":".--.", 
         "Q":"--.-", "R":".-.", "S":"...", "T":"-", "U":"..-", "V":"...-", "W":".--", "X":"-..-", 
         "Y":"-.--", "Z":"--..", ".":".-.-.-", ",":"--..--", "?":"..--..", "@":".--.-.", ":":"---...", 
         "-":"-....-", "'":".----.", "1":".----", "2":"..---", "3":"...--", "4":"....-", "5":".....", 
         "6":"-....", "7":"--...", "8":"---..", "9":"----.", "0":"-----", " ":"/ "}

def main(msg):
    out = ""
    if (msg[0] == '.' or msg[0] == '-'):
        rev_morse = {v: k for k, v in morse.items()}
        for char in msg:
            out += rev_morse[char]
            # Add something if char not in morse list
    else:
        for char in msg:
            out += morse[char]

    return out