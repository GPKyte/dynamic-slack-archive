import os
import sys
import json

from slackclient import SlackClient

directory = sys.argv[1]

with open(os.path.join(directory, "channels.json")) as dir:
  channels = json.load(dir)
  print(channels)
