"""
Installation script for Aquobot
Aquobot written by Austin Bricker (Aquova), 2017
Type "pip3 install -e ." to run
Install requires Python 3.5+ with pip and setuptools to be installed.
NOTE: I haven't actually tested this yet, so use with caution...
"""
from setuptools import setup
import sys
from subprocess import call

if sys.version_info < (3,5):
    sys.exit('Sorry, Python < 3.5 is not supported')

call(["python3 -m pip install git+https://github.com/abenassi/Google-Search-API/"])

setup(name='Aquobot',
	description="World's coolest Discord chat bot",
	url='http://github.com/Aquova/Aquobot',
	author='Aquova',
	install_requires=[
		'geopy', 
		'wolframalpha', 
		'schedule', 
		'wikipedia', 
		'discord.py', 
		'pillow', 
		'yweather', 
		'googletrans', 
		'google-api-python-client', 
		'requests', 
		'lmxl'
	]
)