import discord, urllib, json, urllib.parse, urllib.request, asyncio

class User:
    def __init__(self, url):
        result = urllib.request.urlopen(url).read().decode('utf8')
        data = json.loads(result)
        self.username = data['data']['names']['international']

def getTime(time):
    hours = int(time // 3600)
    minutes = int((time % 3600) // 60)
    seconds = int((time % 60) // 1)
    milliseconds = int(round(time % 1, 3) * 1000)
    output = ''
    if (hours != 0):
        output += str(hours) + 'h '
    output += "{}m {}s ".format(minutes, seconds)
    if (milliseconds != 0):
        output += str(milliseconds) + 'ms'
    return output

async def game(q, client, message):
    q = q.replace(' ', '%20')
    search_url = 'https://www.speedrun.com/api/v1/games?name={}&embed=categories'.format(q)
    result = urllib.request.urlopen(search_url).read().decode('utf8')
    data = json.loads(result)
    try:
        name = data['data'][0]['names']['international']
        url = data['data'][0]['weblink']
        cover = data['data'][0]['assets']['cover-large']['uri']
        release = data['data'][0]['release-date']
        category_len = len(data['data'][0]['categories']['data'])

        embed = discord.Embed(title=name, type='rich', description=url)
        embed.add_field(name='Release Date', value=release)
        embed.set_thumbnail(url=cover)
        embed.add_field(name='Total # of Categories', value=category_len)
        try:
            id = data['data'][0]['id']
            record_url = 'https://www.speedrun.com/api/v1/games/{}/records?miscellaneous=no&scope=full-game'.format(id)
            record_result = urllib.request.urlopen(record_url).read().decode('utf8')
            record_data = json.loads(record_result)
            for i in range(0, len(record_data['data'])):
                # TODO: Add % if '100' or 'Any' appears in the string
                category_name = record_data['data'][i]['weblink'].split('#')[-1].replace('_', ' ')

                top_user_url = record_data['data'][i]['runs'][0]['run']['players'][0]['uri']
                top_user = User(top_user_url)

                top_time = record_data['data'][i]['runs'][0]['run']['times']['primary_t']
                formatted_time = getTime(top_time)
                embed.add_field(name=category_name, value=top_user.username + '\n' + formatted_time)
        except KeyError:
            pass

        await client.send_message(message.channel, embed=embed)
    except IndexError:
        await client.send_message(message.channel, 'No game found by that name')
