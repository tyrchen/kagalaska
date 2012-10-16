# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.algorithm.rank import LazyRank
from tag.service import TagService
from tag.services.wordseg import BaseSeg
from mixins import ModifyMixin, DispatchMixin
from tag.models import Place, Normal

import json
import logging
from tag.utils.util import smart_print

logger = logging.getLogger(__name__)

WORDSEG_UNIX_DOMAIN = settings.WORDSEG_UNIX_DOMAIN
DEFAULT_VALUE = settings.NEW_WORD_DEFAULT_VALUE
TITLE_WEIGHT = settings.TITLE_WEIGHT
CONTENT_WEIGHT = settings.CONTENT_WEIGHT

class WordSegService(object):
  # Singleton instance to parse words
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = BaseSeg()
    return cls.__instance

class WordSegProtocol(protocol.Protocol, DispatchMixin):
  def dataReceived(self, data):
    response = self.dispatch(data, self.factory)
    self.transport.write(json.dumps(response).encode('utf-8'))

class WordSegFactory(protocol.Factory, ModifyMixin):
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
      {'content': json_data['title'], 'weight': TITLE_WEIGHT},
      {'content': json_data['content'], 'weight': CONTENT_WEIGHT}
    ]
    objs.extend(extra)
    TF_IDF = json_data.get('TF_IDF', True)

    rank = LazyRank(objs, seg_ref=self.wordseg,
                    tag_service_ref=self.relations, tf_idf=TF_IDF)
    results = rank.rank()
    return results

  def add(self, **kwargs):
    name = kwargs.get('name', '')
    if not name:
      return

    score = float(kwargs.get('score', DEFAULT_VALUE))
    self.wordseg.add_word(name, score)
    self.relations.add(**kwargs)
    return {'success': True}

  def get(self, **kwargs):
    return self.relations.get_names(**kwargs)

  def update(self, **kwargs):
    smart_print(kwargs, "before update")
    self.remove(**kwargs)
    self.add(**kwargs)
    return {'success': True}

  def remove(self, **kwargs):
    self.relations.remove(**kwargs)
    return {'success': True}

  def place_update(self, **kwargs):
    smart_print(kwargs, 'place_update')
    try:
      slug = kwargs.get('slug', '')
      if not slug:
        return {'success': False}

      Place.cls_update(**kwargs)
    except Exception:
      return {'success': False}
    else:
      return {'success': True}

  def normal_update(self, **kwargs):
    smart_print(kwargs, 'normal_update')
    try:
      slug = kwargs.get('slug', '')
      if not slug:
        return {'success': False}

      Normal.cls_update(**kwargs)
    except Exception:
      return {'success': False}
    else:
      return {'success': True}

def run():
  wordseg = WordSegService()
  relations = TagService()

  print("Start WordSeg Service")
  reactor.listenUNIX(WORDSEG_UNIX_DOMAIN, WordSegFactory(wordseg, relations))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
