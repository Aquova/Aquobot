# This is a program that takes in any date, and gives out the equivalent date in the Mayan notation.
# Written by Austin Bricker, 2015-2017

import datetime

def mayan(num):
    if num.upper() == "TODAY":
        target = datetime.date.today()
    else:
        new = num.split('-')
        m = int(new[0])
        d = int(new[1])
        y = int(new[2])
        target = datetime.date(y,m,d)

    ref = datetime.date(2012, 12, 21) # This is 12/21/12, or 13.0.0.0.0
    delta = ref - target

    # Worked out, 13.0.0.0.0 is a total of 1872000 days since the beginning of the long count.
    total = 1872000
    n = total - delta.days

    first = n // 144000
    n = n % 144000
    second = n // 7200
    n = n % 7200
    third = n // 360
    n = n % 360
    fourth = n // 20
    fifth = n % 20

    mayan = str(first) + "." + str(second) + "." + str(third) + "." + str(fourth) + "." + str(fifth)
    return mayan
