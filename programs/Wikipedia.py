import wikipedia, warnings

# Suppressing the UserWarning from the wikipedia module. Possibly a bad idea in the long run
warnings.filterwarnings('ignore', category=UserWarning, append=True)

def main(q):
	wiki_url = 'https://en.wikipedia.org/wiki/'
	results = wikipedia.search(q)
	try:
	    wikipedia.WikipediaPage(title=results[0])
	    out = wiki_url + results[0].replace(" ","_")
	except wikipedia.exceptions.DisambiguationError as e:
	    out = wiki_url + e.options[0].replace(" ","_")
	except IndexError:
	    out = 'No article was found with that name'

	return out