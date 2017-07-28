# Program that uses the YouTube API to return videos searched with keyword
# Written by Austin Bricker, 2017

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json

with open("config.json") as json_data_file:
	cfg = json.load(json_data_file)

DEVELOPER_KEY = cfg['Client']['google']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search(phrase):
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
	search_response = youtube.search().list(q=phrase, part="id,snippet").execute()
	youtube_url = 'https://www.youtube.com/watch?v='
	for search_result in search_response.get("items", []):
		if search_result["id"]["kind"] == "youtube#video":
			video_id = search_result["id"]["videoId"]
			break
	try:
		url = youtube_url + video_id
	except:
		url = "No videos found with that search term."
	return url