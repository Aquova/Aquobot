num_emoji = {0: ":zero: ", 1:":one: ", 2:":two: ", 3:":three: ", 4:":four: ", 5:":five: ", 6:":six: ", 
				7:":seven: ", 8:":eight: ", 9:":nine: "}

def emoji_text(m):
	final = ""
	for letter in m:
		if letter.isalpha():
			final += ":regional_indicator_{}: ".format(letter)
		elif letter.isdigit():
			final += num_emoji[int(letter)]
		elif letter == "!":
			final += ":exclamation: "
		elif letter == " ":
			final += " "
		else:
			final += ":question: "

	return final

def b_words(m):
	output = []
	words = m.split(" ")
	for word in words:
		if (len(word) >= 4) and (word[1].lower() in ['a', 'e', 'i', 'o', 'u']):
			output.append(":b:" + word[1:])
		else:
			output.append(word)
	final = " ".join(output)
	return final