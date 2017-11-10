# A program that fetches the weather for a Location
# Utilizes the Yahoo Weather API
# Written by Austin Bricker, 2017
# A rewrite of the original Weather.py to better utilizes classes

import yweather, urllib, json, urllib.parse, urllib.request

class weather:

    def __init__(self, place):
        self.place = place
        self.data = get_data(self.place)
        self.weekday = []
        self.weekdate = []
        self.weekhigh = []
        self.weektext = []

    for i in range(7):
        self.weekday.append(self.data['item']['forecast'][i]['day'])
        self.weekdate.append(self.data['item']['forecast'][i]['date'])
        self.weekhigh.append(self.data['item']['forecast'][i]['high'])
        self.weektext.append(self.data['item']['forecast'][i]['text'])


    self.time = self.data['lastBuildDate']
    self.location = self.data['description'][19:]
    self.loc = self.data['title'][-2:]
    self.status = self.data['item']['condition']['text']
    self.temp_F = self.data['item']['condition']['temp']
    self.weather_code = self.data['item']['condition']['code']
    self.temp_C = F2C(self.temp_F)
    self.wind_chill_F = self.data['wind']['chill']
    self.wind_chill_C = F2C(self.wind_chill_F)
    self.wind_dir = self.data['wind']['direction']
    self.wind_card = cardinal(self.wind_dir)
    self.wind_speed_mph = self.data['wind']['speed']
    self.wind_speed_ms = mph2ms(self.wind_speed_mph)
    self.sunrise = self.data['astronomy']['sunrise']
    self.sunset = self.data['astronomy']['sunset']

    def get_woeid(place):
        client = yweather.Client()
        woeid = client.fetch_woeid(place)
        return woeid

    def get_data(place):
        woeid = get_woeid(place)
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select * from weather.forecast where woeid=" + woeid + " and u='f'"
        yql_url = baseurl + urllib.parse.urlencode({'q':yql_query}) + "&format=json"
        result = urllib.request.urlopen(yql_url).read().decode('utf8')
        data = json.loads(result)
        out = data['query']['results']['channel']
        return out

    def F2C(temp):
        fahr = float(temp)
        cel = (fahr - 32) * (5 / 9)
        cel = round(cel, 1)
        return str(cel)

    def mph2ms(speed):
        mph = float(speed)
        ms = mph * 0.447
        ms = round(ms, 1)
        return str(ms)

    def cardinal(value):
        deg = int(value)
        if (deg >= 22.5 and deg < 67.5):
            out = 'NE'
        elif (deg >= 67.5 and deg < 112.5):
            out = 'E'
        elif (deg >= 112.5 and deg < 157.5):
            out = 'SE'
        elif (deg >= 157.5 and deg < 202.5):
            out = 'S'
        elif (deg >= 202.5 and deg < 247.5):
            out = 'SW'
        elif (deg >= 247.5 and deg < 292.5):
            out = 'W'
        elif (deg >= 292.5 and deg < 337.5):
            out = 'NW'
        else:
            out = 'N'
        return out



###


    test_sunset = sunset.split(":")
    if len(test_sunset[1]) == 4:
        sunset = test_sunset[0] + ':0' + test_sunset[1]

    test_sunrise = sunrise.split(':')
    if len(test_sunrise[1]) == 4:
        sunrise = test_sunrise[0] + ':0' + test_sunrise[1]

    out = "Weather for {}: {}, {}°F ({}°C), feels like {}°F ({}°C). Wind: {} at {} mph ({} m/s). Sunrise at {}, sunset at {}.".format(location, weather_status, temp_F, temp_C, wind_chill_F, wind_chill_C, wind_card, wind_speed_mph, wind_speed_ms, sunrise, sunset)
    return out


def emoji_weather(weather_obj):
    flag_emoji = ":flag_{}:".format(weather_obj.loc.lower())
    out = flag_emoji + " " + weather_emoji[int(weather_obj.weather_code)]
    return out

def emoji_forecast(weather_obj):
    out = ":flag_{}:".format(weather_obj.loc.lower()) + '\n'
    for i in range(7):
        value = int(week[i]['code'])
        condition = weather_emoji[value]
        out = out + week[i]['day'] + ": " + condition + '\n'
    return out


###














weather_emoji = {
    0:':cloud_tornado:', 
    1:':ocean: :umbrella:', 
    2:':cyclone:', 
    3:':thunder_cloud_rain:', 
    4:':cloud_lightning:', 
    5:':cloud_rain: :cloud_snow:', 
    6:':cloud_rain: :cloud_snow:', 
    7:':cloud_rain: :cloud_snow:',
    8:':cloud_rain: :snowflake:',
    9:':cloud_rain:',
    10:':cloud_rain: :snowflake:',
    11:':cloud_rain:',
    12:':cloud_rain:',
    13:':cloud_snow:',
    14:':cloud_snow:',
    15:':cloud_snow: :dash:',
    16:':cloud_snow:',
    17:':cloud_snow: :white_circle:',
    18:':cloud_snow: :white_circle:',
    19:':desert:', #This one is supposed to be dust, but it's the best I could do.
    20:':fog:',
    21:':foggy:',
    22:':smoking:',
    23:':dash:',
    24:':dash:',
    25:':snowman:',
    26:':cloud:',
    27:':white_sun_cloud: :night_with_stars:',
    28:':white_sun_cloud:',
    29:':white_sun_small_cloud: :night_with_stars:',
    30:':white_sun_small_cloud:',
    31:':full_moon:',
    32:':sunny:',
    33:':full_moon:',
    34:':sunny:',
    35:':cloud_rain: :white_circle:',
    36:':fire:',
    37:':thunder_cloud_rain:',
    38:':thunder_cloud_rain:',
    39:':thunder_cloud_rain:',
    40:':white_sun_rain_cloud:',
    41:':cloud_snow:',
    42:':cloud_snow:',
    43:':cloud_snow: :snowflake:',
    44:':white_sun_small_cloud:',
    45:':thunder_cloud_rain:',
    46:':cloud_rain: :cloud_snow:',
    47:':cloud_lightning:',
    3200:':question:'
}

