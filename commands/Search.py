import aiohttp, async_timeout, json, asyncio
import lxml.etree as ET

# I probably could combine these into one function someday
async def google(searchTerm):
    params = {'q': searchTerm,
        'safe': 'on',
        'lr': 'lang_en',
        'hl': 'en'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
    }

    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(5):
                async with session.get('https://google.com/search', params=params, headers=headers) as resp:
                    if resp.status == 200:
                        root = ET.fromstring(await resp.text(), ET.HTMLParser())
                        result = root.xpath(".//div[@class='r']")[0][0].attrib
                        out = result['href']
                    else:
                        out = "Google is unavailable I guess?\nError: {}".format(resp.response)
        except IndexError:
            out = "No search results found at all. Did you search for something naughty?"
        except asyncio.TimeoutError:
            out = "Timeout error"
        except Exception as e:
            out = "An unusual error of type {} occurred: ".format(type(e).__name__, str(e))

        return out

async def images(searchTerm):
    params = {'q': searchTerm,
        'safe': 'on',
        'lr': 'lang_en',
        'hl': 'en',
        'tbm': 'isch'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
    }

    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(5):
                async with session.get('https://google.com/search', params=params, headers=headers) as resp:
                    if resp.status == 200:
                        root = ET.fromstring(await resp.text(), ET.HTMLParser())
                        foo = root.xpath(".//div[@class='rg_meta notranslate']")[0].text
                        result = json.loads(foo)
                        out = result['ou']
                    else:
                        out = "Google is unavailable I guess?\nError: {}".format(resp.response)
        except IndexError:
            out = "No search results found at all. Did you search for something naughty?"
        except asyncio.TimeoutError:
            out = "Timeout error"
        except Exception as e:
            out = "An unusual error of type {} occurred".format(type(e).__name__)

        return out
