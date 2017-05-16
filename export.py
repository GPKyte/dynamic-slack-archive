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
    return ENV['id_channel'].get(id, 'None')

def getDate(ts):
    return datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d')

### Taken from StackOverflow, turns unicode into text
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
db_path = os.path.join(db_directory, "messages.sqlite")
arch_dir = os.path.join(os.path.curdir, "SlackArchive")
if not os.path.isdir(arch_dir):
    os.makedirs(arch_dir) 

time = time.time() - 86400
getAll = raw_input("Do you want to export all messages instead of last day?(y/N) ").lower()
if (getAll=='y'):
    time = 0.0


# Establish connection to SQL database
connection = sqlite3.connect(db_path)
connection.row_factory = dict_factory
cursor = connection.cursor()

cursor.execute("SELECT * FROM channels")
channels = byteify(cursor.fetchall())
cursor.execute("SELECT * FROM users")
users = byteify(cursor.fetchall())
for u in users:
    u['profile'] = {}
    u['profile']['image_32'] = u.pop('avatar')

# Define the names associated with each channel id
ENV = {
    'channel_id': {}, 
    'id_channel': {},
}

ENV['channel_id'] = dict([(m['name'], m['id']) for m in channels])
ENV['id_channel'] = dict([(m['id'], m['name']) for m in channels])

# Add channel and user list files to archive directory
channel_file = os.path.join(arch_dir, 'channels.json')
with open(channel_file, 'w') as outfile:
    json.dump(channels, outfile)
    outfile.close()
user_file = os.path.join(arch_dir, 'users.json')
with open(user_file, 'w') as outfile:
    json.dump(users, outfile)
    outfile.close()



command = ("SELECT * FROM messages WHERE timestamp > %s ORDER BY channel, timestamp") % time
cursor.execute(command)
results = byteify(cursor.fetchall())

# Clean and store results in accepted format
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
update_count = 0
for channel_name in channel_msgs.keys():
    # Checks for any messages from today
    if len(channel_msgs[channel_name]) == 0:
        continue
    else:
	update_count += 1
        print("%s has been updated") %channel_name

    dir = os.path.join(arch_dir, channel_name)
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
print("Updated %s channels") %(update_count)

connection.close()
