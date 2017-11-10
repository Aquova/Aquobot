# A program that takes text input and flips it upside down
# Written by Austin Bricker, 2017

flip = {'A':'∀','B':'q','C':'Ɔ','D':'p','E':'Ǝ','F':'Ⅎ','G':'פ','H':'H','I':'I','J':'ſ','K':'ʞ','L':'˥','M':'W','N':'N','O':'O','P':'Ԁ','Q':'Q','R':'ɹ','S':'S','T':'┴','U':'∩','V':'Λ','W':'M','X':'X','Y':'⅄','Z':'Z','a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ','i':'ᴉ','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d','q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x','y':'ʎ','z':'z','1':'Ɩ','2':'ᄅ','3':'Ɛ','4':'h','5':'5','6':'9','7':'ㄥ','8':'8','9':'6','0':'0','!':'¡','?':'¿','_':'‾','"':',,',"'":",",",":"'",'.':'˙'}

def down(phrase):
    phrase = phrase[::-1]
    out = ""
    for letter in phrase:
        if letter in list(flip.keys()):
            out = out + flip[letter]
        else:
            out = out + letter
    return out
