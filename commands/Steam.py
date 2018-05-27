import urllib, json, urllib.parse, urllib.request, datetime, os, sys

with open(os.path.join(sys.path[0], 'config.json')) as json_data_file:
    cfg = json.load(json_data_file)

api = cfg['Client']['steam']

def get_id(username):
	id_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={0}&vanityurl={1}".format(api, username)
	id_result = urllib.request.urlopen(id_url).read().decode('utf8')
	id_data = json.loads(id_result)
	if id_data['response']['success'] == 1:
		return id_data['response']['steamid']
	else:
		return None

def get_userinfo(q):
	userid = get_id(q)
	user_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={0}&steamids={1}".format(api, userid)
	user_result = urllib.request.urlopen(user_url).read().decode('utf8')
	user_data = json.loads(user_result)

	try:
		username = user_data['response']['players'][0]['personaname']
		last_logoff = user_data['response']['players'][0]['lastlogoff']
		last_logoff_readable = datetime.datetime.fromtimestamp(last_logoff)
		date_created = user_data['response']['players'][0]['timecreated']
		date_created_readable = datetime.datetime.fromtimestamp(date_created)
		profile_url = user_data['response']['players'][0]['profileurl']
		avatar = user_data['response']['players'][0]['avatarmedium']
	except IndexError:
		return "No user found with that name."

	games_url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={0}&steamid={1}&format=json".format(api, userid)
	games_result = urllib.request.urlopen(games_url).read().decode('utf8')
	games_data = json.loads(games_result)
	game_total = games_data['response']['game_count']

	try:
		recent_url = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={0}&steamid={1}&format=json".format(api,userid)
		recent_result = urllib.request.urlopen(recent_url).read().decode('utf8')
		recent_data = json.loads(recent_result)
		recent_total = recent_data['response']['total_count']
		recent_game = recent_data['response']['games'][0]['name']
		recent_game_2weeks = round(recent_data['response']['games'][0]['playtime_2weeks'] / 60, 1)
		recent_game_total = round(recent_data['response']['games'][0]['playtime_forever'] / 60, 1)
		# recent_string = "Played {0} game(s) during the past 2 weeks | Most played last 2 weeks: {1} ({2} hours, {3} hours total)".format(recent_total,recent_game,recent_game_2weeks,recent_game_total)
		recent_list = [recent_total, recent_game,recent_game_2weeks, recent_game_total]
	except KeyError:
		# recent_string = "Played 0 games during the past 2 weeks"
		recent_list = ["Played 0 games during the past 2 weeks"]


	output = [username, userid, profile_url, avatar, last_logoff_readable, date_created_readable, game_total] + recent_list
	return output

	# Old Steam output:
	# output = "User {0} | Userid: {1} | Last online: {2} | Profile created: {3} | Total # of games: {4} | ".format(username,userid,last_logoff_readable,date_created_readable,game_total) + recent_string
	# output += '\n' + profile_url
	# return output