#!/bin/python

import datetime
import time
import os
import sys
import sqlite3
import json

from slackclient import SlackClient

def dict_factory(cursor, row):
  d = {}
  for index, column in enumerate(cursor.description):
    d[column[0]] = row[index]
  return d

def get_channel_name(id):
  #print(id)
  return ENV['id_channel'].get(id, 'None')

def getDate(ts):
  return datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d')

### Taken from StackOverflow
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
###



db_directory = sys.argv[1]
directory = os.path.join(os.path.curdir, "EBTH_SlackArchive")
time = time.time() - 86400
getAll = raw_input("Do you want to export all messages instead of last day?(y/N)").lower()
if (getAll=='y'):
  time = 0.0

path_to_db = os.path.join(db_directory, "messages.sqlite")

# Establish connection to SQL database
connection = sqlite3.connect(path_to_db)
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

command = ("SELECT * FROM messages WHERE timestamp > %s ORDER BY channel, timestamp") % time
cursor.execute(command)
results = byteify(cursor.fetchall())

channel_msgs = dict([(c['name'], {}) for c in channels])

for message in results:
  message['text'] = message['message']
  message['ts'] = message['timestamp']
  message['type'] = 'message'
  message.pop('message')
  message.pop('timestamp')

  channel_name = get_channel_name(message['channel'])
  if channel_name == "None":
    continue

  # timestamp format is #########.######
  day = getDate(message['ts'].split('.')[0])
  if channel_msgs[channel_name].get(day, None):
    channel_msgs[channel_name][day].append(message)
  else:
    channel_msgs[channel_name][day] = [message]

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

  for day in channel_msgs[channel_name].keys():
    file = os.path.join(dir, "%s.json") % day
    with open(file, 'w') as outfile:
      json.dump(channel_msgs[channel_name][day], outfile)
      outfile.close()




connection.close()
