#!/bin/python
# Usage: python export.py <path_to_database> <path_for_new_folder>
# Output: folder in given directory

import datetime
import time
import os
import sys
import sqlite3
import json

from slackclient import SlackClient

# Used in conjunction with sqlite3 to generate JSON-like format
def dict_factory(cursor, row):
    d = {}
    for index, column in enumerate(cursor.description):
        d[column[0]] = row[index]
    return d

# Turns unicode into text
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

def get_channel_name(id):
    return ENV['id_channel'].get(id, 'None')

def getDate(ts):
    return datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d')


# Uncomment time in the future if running daily (Used to export last days of messages)
#time = time.time() - 86400 # One full day in seconds
time = 0.0
db_path = sys.argv[1]
arch_dir = sys.argv[2]
if not os.path.isdir(arch_dir):
    os.makedirs(arch_dir) 
    time = 0.0 # Full export instead of day export

# Uncomment if you need to export entire archive or make this choice
# getAll = raw_input("Do you want to export all messages instead of last day?(y/N) ").lower()
# if (getAll=='y'):
#    time = 0.0


# Establish connection to SQL database
connection = sqlite3.connect(db_path)
connection.row_factory = dict_factory
cursor = connection.cursor()

# Get channel and user data
cursor.execute("SELECT * FROM channels")
channels = byteify(cursor.fetchall())
cursor.execute("SELECT * FROM users")
users = byteify(cursor.fetchall())
for u in users:
    u['profile'] = {}
    u['profile']['image_72'] = u.pop('avatar')

# Save channel and user data files to archive folder
channel_file = os.path.join(arch_dir, 'channels.json')
with open(channel_file, 'w') as outfile:
    json.dump(channels, outfile)
    outfile.close()
user_file = os.path.join(arch_dir, 'users.json')
with open(user_file, 'w') as outfile:
    json.dump(users, outfile)
    outfile.close()


# Define the names associated with each channel id
ENV = {
    'channel_id': {}, 
    'id_channel': {},
}

ENV['channel_id'] = dict([(m['name'], m['id']) for m in channels])
ENV['id_channel'] = dict([(m['id'], m['name']) for m in channels])

# Get all messages after given time (in seconds since the Epoch)
command = ("SELECT * FROM messages WHERE timestamp > %s ORDER BY channel, timestamp") % time
cursor.execute(command)
results = byteify(cursor.fetchall())

# Clean and store message results in Slack-ish format
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

    if not os.path.isdir(dir):
        os.makedirs(dir)

    for day in channel_msgs[channel_name].keys():
        file = os.path.join(dir, "%s.json") % day
        with open(file, 'w') as outfile:
            json.dump(channel_msgs[channel_name][day], outfile)
            outfile.close()
print("Updated %s channels") %(update_count)

connection.close()
