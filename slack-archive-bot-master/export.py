#!/bin/python

import datetime
import time
import os
import sys
import sqlite3
import json

from slackclient import SlackClient

directory = sys.argv[1]
time = time.time() - 2*86400

def getDate(ts):
  return datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d')

def dict_factory(cursor, row):
  d = {}
  for index, column in enumerate(cursor.description):
    d[column[0]] = row[index]
  return d

def get_channel_name(id):
  #print(id)
  return ENV['id_channel'].get(id, 'None')

# Look into why this works
def byteify(input):
  if isinstance(input, dict):
    return {byteify(key): byteify(value)
            for key, value in input.iteritems()}
  elif isinstance(input, list):
    return [byteify(element) for element in input]
  elif isinstance(input, unicode):
    return input.encode('utf-8')
  else:
    return input

# Establish connection to SQL database
connection = sqlite3.connect("messages.sqlite")
connection.row_factory = dict_factory

cursor = connection.cursor()

with open(os.path.join(directory, "channels.json")) as f:
  channels = byteify(json.load(f))

# Define the names associated with each channel id
ENV = {
  'channel_id': {}, 
  'id_channel': {},
}


ENV['channel_id'] = dict([(m['name'], m['id']) for m in channels])
ENV['id_channel'] = dict([(m['id'], m['name']) for m in channels])
#print(ENV['channel_id'])
#print(ENV['id_channel'])


# Translate database into JSON format
command = ("SELECT * FROM messages WHERE timestamp > %s ORDER BY channel, timestamp") % time
cursor.execute(command)
results = byteify(cursor.fetchall())

channel_msgs = dict([(c['name'], []) for c in channels])

for message in results:
  message['text'] = message['message']
  message['ts'] = message['timestamp']
  message['type'] = 'message'
  message.pop('message')
  message.pop('timestamp')

  channel_name = get_channel_name(message['channel'])
  if channel_name == "None":
    continue

  channel_msgs[channel_name].append(message)


# Go to channel folder and title message collection as <date>.json
for channel_name in channel_msgs.keys():
  # Checks if any messages today
  if len(channel_msgs[channel_name]) == 0:
    continue
  else:
    print("%s has been updated") %channel_name

  dir = os.path.join(directory, channel_name)
  if "None" in dir:
    print("Channel not found: %s") %message['channel']
    continue

  if not os.path.exists(dir):
    os.makedirs(dir)

  timestamp = getDate(channel_msgs[channel_name][0]['ts'].split('.')[0])
  file = os.path.join(dir, "%s.json") % timestamp

  with open(file, 'w') as outfile:
    json.dump(channel_msgs[channel_name], outfile)
    outfile.close()




connection.close()
