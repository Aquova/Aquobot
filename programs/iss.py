import sqlite3, urllib, json, datetime
from geopy.geocoders import Nominatim

def main(mai):
    sqlconn = sqlite3.connect('database.db')
    geo = Nominatim()
    iss_json_url = urllib.request.urlopen('http://api.open-notify.org/iss-now.json')
    iss_json = json.loads(iss_json_url.read())
    latitude = iss_json['iss_position']['latitude']
    longitude = iss_json['iss_position']['longitude']
    location = geo.reverse("{0}, {1}".format(latitude,longitude))

    if float(latitude) >= 0:
        latitude += "° N"
    else:
        latitude = str(-1 * float(latitude)) + "° S"

    if float(longitude) >= 0:
        longitude += "° E"
    else:
        longitude = str(-1 * float(longitude)) + "° W"

    time = datetime.datetime.fromtimestamp(iss_json['timestamp'])
    out = "Right now ({0}), the International Space Station is located at {1}, {2}".format(time, latitude, longitude)
    try:
        out += ", located at {}".format(location)
    except TypeError:
        pass

    # Check if user's location is stored, and add info
    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [mai])
    try:
        user_location = user_loc.fetchone()[0]
        location = geo.geocode(user_location)
        user_lat = location.latitude
        user_long = location.longitude
        pass_url = urllib.request.urlopen("http://api.open-notify.org/iss-pass.json?lat={0}&lon={1}".format(user_lat,user_long))
        pass_json = json.loads(pass_url.read())
        risetime = datetime.datetime.fromtimestamp(pass_json['response'][0]['risetime'])
        duration = pass_json['response'][0]['duration']
        out += '\nThe ISS will next pass over your location at {0} for {1} seconds'.format(risetime, duration)
    except TypeError:
        out += "\nAdd your location to the database with !w add LOCATION to get more information!"

    return out