# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.services.wordseg import BaseSeg
from tag.models import TagManager
from tag.algorithm.tag_rank import TagRank

import json
import logging

logger = logging.getLogger(__name__)

WORDSEG_UNIX_DOMAIN = settings.WORDSEG_UNIX_DOMAIN

class WordSegService(object):
  # Singleton instance to parse words
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = super(WordSegService, cls).__new__(cls, *args, **kwargs)
    return cls.__instance

  def __init__(self):
    self.seg = BaseSeg()

  def parse(self, text, weight=1):
    return self.seg.parse(text, weight=weight)

class TraverseService(object):
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = super(TraverseService, cls).__new__(cls, *args, **kwargs)
    return cls.__instance

  def __init__(self):
    self.manager = TagManager()

  def traverse(self, tag):
    return self.manager.traverse(tag)

class WordSegProtocol(protocol.Protocol):
  def dataReceived(self, data):
    json_data = json.loads(data.decode('utf-8'))
    objs = [
      {'content': json_data['title'], 'weight': 3},
      {'content': json_data['content'], 'weight': 1}
    ]
    imagine = json_data.get('imagine', True)
    rank = TagRank(objs, traverse_func=self.factory.traverse,
                   seg_func=self.factory.parse, imagine=imagine)
    
    results = rank.rank()

    self.transport.write(json.dumps(results).encode('utf-8'))

class WordSegFactory(protocol.Factory):
  protocol = WordSegProtocol

  def __init__(self, wordseg, relations):
    self.wordseg = wordseg
    self.relations = relations

  def parse(self, words, weight=1):
    return self.wordseg.parse(words, weight=weight)

  def traverse(self, tag):
    return self.relations.traverse(tag)

def run():
  wordseg = WordSegService()
  relations = TraverseService()

  print("Start WordSeg Service")
  reactor.listenUNIX(WORDSEG_UNIX_DOMAIN, WordSegFactory(wordseg, relations))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
