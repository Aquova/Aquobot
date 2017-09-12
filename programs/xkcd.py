import json, urllib, random

def get_xkcd(xkcd_json):
    title = xkcd_json['title']
    date = "{0}/{1}/{2}".format(xkcd_json['month'], xkcd_json['day'], xkcd_json['year'])
    alt_text = xkcd_json['alt']
    img_url = xkcd_json['img']
    num = xkcd_json['num']
    out = title + ", " + date + ", Comic #" + str(num) + '\n' + img_url + '\n' + "Alt text: " + alt_text
    return out

def main(q):
    xkcd_json_url = urllib.request.urlopen('https://xkcd.com/info.0.json')
    xkcd_json = json.loads(xkcd_json_url.read())
    max_comic = xkcd_json['num']
    if q == '!xkcd':
        out = get_xkcd(xkcd_json)
    elif (q.split(" ")[1] == 'random' or q.split(" ")[1] == 'rand'):
        num = random.randint(1, max_comic)
        new_url = 'https://xkcd.com/{}/info.0.json'.format(num)
        new_json_url = urllib.request.urlopen(new_url)
        xkcd_json = json.loads(new_json_url.read())
        out = get_xkcd(xkcd_json)
    else:
        try:
            num = int(q.split(" ")[1])
            new_url = 'https://xkcd.com/{}/info.0.json'.format(num)
            new_json_url = urllib.request.urlopen(new_url)
            xkcd_json = json.loads(new_json_url.read())
            out = get_xkcd(xkcd_json)
        except ValueError:
            out = "Not a valid number." + '\n' + "!xkcd [comic #]"
        except urllib.error.HTTPError:
            out = "There's no comic with that index number."

    return out