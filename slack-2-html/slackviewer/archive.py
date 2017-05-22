import hashlib
import json
import os
import zipfile
import glob

from slackviewer.message import Message


def get_channel_list(path):
    channels = [ c["name"] for c in get_channels(path).values() ]
    return channels


def compile_channels(path, user_data, channel_data):
    channels = get_channel_list(path)
    chats = {}
    for channel in channels:
        channel_dir_path = os.path.join(path, channel)
        messages = []
        day_files = glob.glob(os.path.join(channel_dir_path, "*.json"))
        if not day_files:
            continue
        for day in sorted(day_files, reverse=False):
            with open(os.path.join(path, day)) as f:
                day_messages = json.load(f)
                messages.extend([Message(user_data, channel_data, d) for d in
                                 day_messages])
        chats[channel] = messages
    return chats


def get_users(path):
    with open(os.path.join(path, "users.json")) as f:
        return {u["id"]: u for u in json.load(f)}


def get_channels(path):
    with open(os.path.join(path, "channels.json")) as f:
        return {u["id"]: u for u in json.load(f)}


def SHA1_file(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def extract_archive(filepath):
    filepath=os.path.abspath(filepath)
    if os.path.isdir(filepath):
        print("Archive already extracted. Converting %s") %(filepath)
        return filepath

    if not zipfile.is_zipfile(filepath):
        # Misuse of TypeError? :P
        raise TypeError("{} is not a zipfile".format(filepath))

    zip_dir = os.path.split(filepath)[0]
    extracted_path = os.path.join(zip_dir, "slack-archive")
    if os.path.exists(extracted_path):
        print("{} already exists".format(extracted_path))
    else:
        # Extract zip in same dir as filepath
        with zipfile.ZipFile(filepath) as zip:
            print("{} extracting to {}...".format(
                filepath,
                extracted_path))
            zip.extractall(path=extracted_path)
        print("{} extracted to {}.".format(filepath, extracted_path))

    return extracted_path

