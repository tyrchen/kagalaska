# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from settings import WORDSEG_UNIX_DOMAIN
from twisted.internet import protocol, reactor
from log import get_logger
from services.wordseg import BaseSeg
from services.manager import TagManager

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
    items = self.factory.parse(data)

    parents = []
    for key, value in items:
      d = self.factory.traverse(key)
      for value in d.values():
        parents.extend(value)

    unique_parents = '__1,'.join(list(set(parents))) + '__1'
    results = ','.join(map(lambda item:item[0] + '__' + str(item[1]), items)) + \
      ',' + unique_parents

    self.transport.write(results.encode('utf-8'))

class WordSegFactory(protocol.Factory):
  protocol = WordSegProtocol

  def __init__(self, wordseg, relations):
    self.wordseg = wordseg
    self.relations = relations

  def parse(self, words):
    return self.wordseg.parse(words)

  def traverse(self, tag):
    return self.relations.traverse(tag)

def run():
  wordseg = WordSegService()
  relations = TagManager()

  print("Start WordSeg Service")
  reactor.listenUNIX(WORDSEG_UNIX_DOMAIN, WordSegFactory(wordseg, relations))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
