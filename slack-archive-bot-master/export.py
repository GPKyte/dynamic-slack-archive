#!/bin/python

import datetime
import os
import sys
import sqlite3
import json

from slackclient import SlackClient

directory = sys.argv[1]


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
cursor.execute("SELECT * FROM messages ORDER BY channel, timestamp")
results = byteify(cursor.fetchall())


for message in results:
  channel_name = get_channel_name(message['channel'])
  dir = os.path.join(directory, channel_name)
  if "None" in dir:
    print("Channel not found: %s") %message['channel']
    continue

  file = os.path.join(dir, "base_date")
  if os.path.isfile(file):
    with open(file, 'r+') as outfile:
      old_data = json.load(outfile)
      new_data = old_data.update(message)
      json.dump(new_data, outfile)
      outfile.close()

  else:
    with open(file, 'r+') as outfile:
      json.dump(message)
      outfile.close()

connection.close()
