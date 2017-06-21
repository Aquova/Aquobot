# A program that fetches the weather for a Location
# Utilizes the Yahoo Weather API
# Written by Austin Bricker, 2017

import yweather, urllib, json, urllib.parse, urllib.request

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

def forecast(place):
    data = get_data(place)
    week = data['item']['forecast']
    out = ""
    for i in range(7):
        out = out + week[i]['day'] + " " + week[i]['date'] + ", " + week[i]['text'] + " with a high of " + week[i]['high'] + "°F (" + F2C(week[i]['high']) + "°C) " + '\n'
    return out


def main(place):
    data = get_data(place)

    location = data['description'][19:]
    weather_status = data['item']['condition']['text']
    temp_F = data['item']['condition']['temp']
    temp_C = F2C(temp_F)
    wind_chill_F = data['wind']['chill']
    wind_chill_C = F2C(wind_chill_F)
    wind_dir = data['wind']['direction']
    wind_card = cardinal(wind_dir)
    wind_speed_mph = data['wind']['speed']
    wind_speed_ms = mph2ms(wind_speed_mph)
    sunrise = data['astronomy']['sunrise']
    sunset = data['astronomy']['sunset']

    test = sunset.split(":")
    if len(test[1]) == 4:
        sunset = test[0] + ':0' + test[1]

    out = "Weather for " + location + ": " + weather_status + ", " + temp_F + "°F (" + temp_C + "°C), feels like " + wind_chill_F + "°F (" + wind_chill_C + "°C). Wind: " + wind_card + " at "+ wind_speed_mph + " mph (" + wind_speed_ms + " m/s). Sunrise at " + sunrise + ", sunset at " + sunset + "."

    return out
