# This is a program that can convert integers into Roman Numerals, or vice versa
# Written by Austin Bricker, 2015-2017

def roman_to_int(num):
    output = 0
    for letter in num:
        if letter.upper() == "M":
            output += 1000
        elif letter.upper() == "D":
            output += 500
        elif letter.upper() == "C":
            output += 100
        elif letter.upper() == "L":
            output += 50
        elif letter.upper() == "X":
            output += 10
        elif letter.upper() == "V":
            output += 5
        elif letter.upper() == "I":
            output += 1
    if "CM" in num.upper():
        output -= 200
    if "XC" in num.upper():
        output -= 20
    if "IX" in num.upper():
        output -= 2
    if "IV" in num.upper():
        output -= 2
    return output

def int_to_roman(number):
    num = int(number)
    output = ""
    M = num // 1000
    output = output + ("M" * M)
    new = num - (M * 1000)
    if new < 900:
        D = new // 500
        output = output + ("D" * D)
        new = new - (D * 500)
        C = new // 100
        output = output + ("C" * C)
        new = new - (C * 100)
    else:
        output = output + "CM"
        new = new - 900
    if new < 90:
        L = new // 50
        output = output + ("L" * L)
        new = new - (L * 50)
        X = new // 10
        output = output + ("X" * X)
        new = new - (X * 10)
    else:
        output = output + "XC"
        new = new - 90
    if new < 9:
        V = new // 5
        output = output + ("V" * V)
        new = new - (V * 5)
        if new < 4:
            I = new
            output = output + ("I" * I)
        else:
            output = output + "IV"
            new = new - 4
    else:
        output = output + "IX"
        new = new - 9
    return output
