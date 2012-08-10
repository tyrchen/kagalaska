# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from utils import to_str, to_unicode
from const import WORDSEG_UNIX_DOMAIN, RELATIONS_UNIX_DOMAIN

import socket
import json

receive_length = lambda str: len(str) * 10 if len(str) > 256 else 4096

class SocketProxy(object):
  def __init__(self, connect_to, type=socket.AF_UNIX,
               stream=socket.SOCK_STREAM):
    self.connect_to = connect_to
    self.socket = socket.socket(type, stream)

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

    return self.format(response_str)

class WordSeg(object):
  def handle(self, words):
    sock = SocketProxy(WORDSEG_UNIX_DOMAIN)
    return sock.process(words)

  def format(self, str_list):
    return to_unicode(str_list)

class TagRelation(object):
  def handle(self, word):
    sock = SocketProxy(RELATIONS_UNIX_DOMAIN)
    return sock.process(word)

  def format(self, str_list):
    return json.loads(str_list.decode('utf-8'))
