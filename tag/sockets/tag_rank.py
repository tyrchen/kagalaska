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
      cls.__instance = BaseSeg()
    return cls.__instance

  def __init__(self):
    self.seg = BaseSeg()

class TraverseService(object):
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = TagManager()
    return cls.__instance

class WordSegProtocol(protocol.Protocol):
  def dataReceived(self, data):
    json_data = json.loads(data.decode('utf-8'))
    extra = json_data.get('extra', [])
    objs = [
      {'content': json_data['title'], 'weight': 1.5},
      {'content': json_data['content'], 'weight': 1}
    ]
    objs.extend(extra)
    imagine = json_data.get('imagine', True)
    TF_IDF = json_data.get('TF_IDF', True)

    rank = TagRank(objs, tag_manager=self.factory.relations,
                   wordseg=self.factory.wordseg, imagine=imagine,
                   TF_IDF=TF_IDF)
    
    results = rank.rank()
    self.transport.write(json.dumps(results).encode('utf-8'))

class WordSegFactory(protocol.Factory):
  protocol = WordSegProtocol

  def __init__(self, wordseg, relations):
    self.wordseg = wordseg
    self.relations = relations

  def parse(self, words, weight=1, TF_IDF=True):
    return self.wordseg.parse(words, weight=weight, TF_IDF=TF_IDF)

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
