# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from const import UNIX_DOMAIN
from twisted.internet import protocol, reactor
from log import get_logger
from relations.wordseg import BaseSeg

logger = get_logger()

class WordSegService(object):
  # Singleton instance to parse words
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = super(WordSegService, cls).__new__(cls, *args, **kwargs)
    return cls.__instance

  def __init__(self):
    self.seg = BaseSeg()

  def parse(self, text):
    return self.seg.parse(text)

class WordSegProtocol(protocol.Protocol):
  def dataReceived(self, data):
    results = self.factory.parse(data)
    self.transport.write(results)

class WordSegFactory(protocol.Factory):
  protocol = WordSegProtocol

  def __init__(self, service):
    self.service = service

  def parse(self, words):
    return self.service.parse(words).encode('utf-8')

def start():
  service = WordSegService()

  print("Start WordSeg Service")
  reactor.listenUNIX(UNIX_DOMAIN, WordSegFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
