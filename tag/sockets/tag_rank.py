# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.algorithm.rank import LazyRank
from tag.service import TagService
from tag.services.wordseg import BaseSeg
from mixins import ModifyMixin, DispatchMixin

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

class WordSegProtocol(protocol.Protocol, DispatchMixin):
  def dataReceived(self, data):
    response = self.dispatch(data, self.factory)
    self.transport.write(response)

class WordSegFactory(protocol.Factory):
  protocol = WordSegProtocol

  def __init__(self, wordseg, relations):
    self.wordseg = wordseg
    self.relations = relations

  def parse(self, words, weight=1, TF_IDF=True):
    return self.wordseg.parse(words, weight=weight, TF_IDF=TF_IDF)

  def traverse(self, tag):
    return self.relations.traverse(tag)

  def rank(self, **json_data):
    extra = json_data.get('extra', [])
    objs = [
      {'content': json_data['title'], 'weight': 2},
      {'content': json_data['content'], 'weight': 1}
    ]
    objs.extend(extra)
    TF_IDF = json_data.get('TF_IDF', True)

    rank = LazyRank(objs, seg_ref=self.wordseg,
                    tag_service_ref=self.relations, tf_idf=TF_IDF)
    results = rank.rank()
    return json.dumps(results).encode('utf-8')

def run():
  wordseg = WordSegService()
  relations = TagService()

  print("Start WordSeg Service")
  reactor.listenUNIX(WORDSEG_UNIX_DOMAIN, WordSegFactory(wordseg, relations))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
