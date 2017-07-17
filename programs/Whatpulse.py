import urllib, json, urllib.parse, urllib.request

def main(q):
	user_url = "http://api.whatpulse.org/user.php?user={}&format=json".format(q)
	result = urllib.request.urlopen(user_url).read().decode('utf8')
	data = json.loads(result)
	try:
		username = data['AccountName']
		country = data['Country']
		key_presses = data['Keys']
		clicks = data['Clicks']
		downloaded = data['Download']
		uploaded = data['Upload']
		date_joined = data['DateJoined']
		if data['Team'] == "0":
			team = "None"
		else:
			team = data["Team"]["Name"]
		out = "User: {0} | Date Joined: {1} | Country: {2} | Key presses: {3} | Clicks: {4} | Total downloaded: {5} | Total uploaded: {6} | Team: {7}".format(username,date_joined,country,key_presses,clicks,downloaded,uploaded,team)
		out += '\n' + "http://whatpulse.org/{}".format(username)
	except KeyError:
		out = "There is no user by that name"
	return out
