import os
import sys
import json
import datetime
import time

from slackclient import SlackClient

def getTime(ts):
  return datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d.json')

def go():
  """
  ts = 1489605670
  print(getTime(ts))
  print(getTime(ts+1))
  print(getTime(ts+10))
  print(getTime(ts+100))
  print(getTime(ts+1000))
  print(getTime(ts+10000))
  print(getTime(ts+100000))
  print(getTime(ts+1000000))
  print(getTime(ts+10000000))
  print(getTime(ts+100000000))
  print(getTime(ts+1000000000))
  print("-------------")
  print(getTime(ts))
  print(getTime(ts+1))
  print(getTime(ts+11))
  print(getTime(ts+111))
  print(getTime(ts+1111))
  print(getTime(ts+11111))
  print(getTime(ts+111111))
  print(getTime(ts+1111111))
  print(getTime(ts+11111111))
  print(getTime(ts+111111111))
  print(getTime(ts+1111111111))
  print("-------------")
  print(getTime(ts))
  print(getTime(ts+60))
  print(getTime(ts+86400))
  print(getTime(0))
  """  
  date = time.time()
  print(date)
  print(getTime(date))

go()
