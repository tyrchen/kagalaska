# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import socket
import json
import os

HOME = '/tmp/'
SETTINGS = {
  'wordseg_default': os.path.join(HOME, 'wordseg.sock'),
  'relation_default': os.path.join(HOME, 'relation.sock'),
}

try:
  import django
  WORDSEG_UNIX_DOMAIN = getattr(django.conf.settings, 'WORDSEG_SOCKET', SETTINGS['wordseg_default'])
  RELATIONS_UNIX_DOMAIN = getattr(django.conf.settings, 'RELATION_SOCKET', SETTINGS['relation_default'])
except Exception:
  WORDSEG_UNIX_DOMAIN = SETTINGS['wordseg_default']
  RELATIONS_UNIX_DOMAIN =  SETTINGS['relation_default']

receive_length = lambda str: len(str) * 10 if len(str) > 256 else 4096

def to_unicode(obj):
  if isinstance(obj, str):
    return obj.decode('utf-8')
  else:
    return obj

def to_str(obj):
  if isinstance(obj, unicode):
    return obj.encode('utf-8')
  elif isinstance(obj, str):
    return obj
  else:
    return obj

class SocketProxy(object):
  def __init__(self, connect_to, type=socket.AF_UNIX,
               stream=socket.SOCK_STREAM, func=None):
    self.connect_to = connect_to
    self.socket = socket.socket(type, stream)
    self.format_fun = func if func else self.format

  def connect(self):
    self.socket.connect(self.connect_to)

  def sendall(self, str):
    self.socket.sendall(str)

  def receive(self, max=4096):
    return self.socket.recv(max)

  def format(self, str_list):
    return to_unicode(str_list)

  def close(self):
    self.socket.close()

  def process(self, str):
    str = to_str(str)

    self.connect()
    self.sendall(str)

    response_str = self.receive(max=receive_length(str))
    self.close()

    return self.format_fun(response_str)

class API(object):
  def parse_words(self, words):
    def format(str_list):
      return to_unicode(str_list)

    sock = SocketProxy(connect_to=WORDSEG_UNIX_DOMAIN, func=format)
    return sock.process(words)

  def traverse(self, word):
    def format(str_list):
      return json.loads(str_list.decode('utf-8'))

    sock = SocketProxy(connect_to=RELATIONS_UNIX_DOMAIN, func=format)
    return sock.process(word)
