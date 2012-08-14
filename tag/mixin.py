# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import pymongo
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

connection = pymongo.Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
db = connection[settings.MONGO_DB]

class Mongoable:
  @property
  def pk(self):
    raise NotImplemented

  def save(self):
    collection_name = self.__class__.__name__.lower()

    try:
      db[collection_name].insert(self.__dict__)
    except Exception, err:
      logger.info(err)
      return False
    else:
      return True

  def update(self, obj, upsert=True):
    collection_name = self.__class__.__name__.lower()

    try:
      db[collection_name].update({'name': self.pk}, obj, upsert=upsert)
    except Exception, err:
      logger.info(err)

  @classmethod
  def cls_update(cls, name, obj, upsert=True):
    collection_name = cls.__name__.lower()

    try:
      db[collection_name].update({'name': name}, obj, upsert=upsert)
    except Exception, err:
      logger.info(err)

  @classmethod
  def objects(cls):
    collection_name = cls.__name__.lower()
    all = db[collection_name].find()
    if not all:
      raise StopIteration

    for item in all:
      del item['_id']
      yield cls(**item)

  @classmethod
  def get_one_query(cls, query):
    collection_name = cls.__name__.lower()

    try:
      json_data = db[collection_name].find_one(query)
    except Exception, err:
      logger.info(err)
      return None
    else:
      return json_data

  @classmethod
  def get_by_query(cls, query):
    collection_name = cls.__name__.lower()

    try:
      clusters = db[collection_name].find(query)
    except Exception, err:
      logger.info(err)
      return None
    else:
      return clusters

  @classmethod
  def get_indexes(cls):
    collection_name = cls.__name__.lower()
    return db[collection_name].index_information()

  @classmethod
  def ensure_indexes(cls):
    if not getattr(cls, 'indexes', None):
      return

    assert isinstance(cls.indexes, list)
    collection_name = cls.__name__.lower()

    try:
      for index in cls.indexes:
        key, kwargs = index
        pk = key.popitem()
        db[collection_name].ensure_index([pk], **kwargs)
    except Exception, err:
      logger.info(err)

  @classmethod
  def clear_indexes(cls):
    collection_name = cls.__name__.lower()
    try:
      db[collection_name].drop_indexes()
    except Exception, err:
      logger.info(err)

  @classmethod
  def delete_all(cls):
    collection_name = cls.__name__.lower()
    db[collection_name].remove()

class Graphical:
  def traverse(self):
    d = {}
    nodes = self.next_nodes()
    d.update({self: self.next_nodes()})

    for p in nodes:
      if not p:
        continue

      if not p.next_nodes():
        continue

      d.update({p: p.next_nodes()})

    return d

  def next_nodes(self):
    raise NotImplemented


