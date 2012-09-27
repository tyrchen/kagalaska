# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from exceptions import NotExistsException, MongoDBHandleException

import pymongo
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
      raise MongoDBHandleException('On Save')
    else:
      return True

  def update(self, obj, upsert=True):
    collection_name = self.__class__.__name__.lower()

    try:
      db[collection_name].update({'name': self.pk}, obj, upsert=upsert)
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException('On Instance Update')

  @classmethod
  def cls_update(cls, name, obj, upsert=True):
    collection_name = cls.__name__.lower()

    try:
      db[collection_name].update({'name': name}, obj, upsert=upsert)
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException('On Class Update')

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
  def get_one_query(cls, query, only=[]):
    restrict = dict.fromkeys(only, 1)
    collection_name = cls.__name__.lower()

    try:
      if not restrict:
        json_data = db[collection_name].find_one(query)
      else:
        json_data = db[collection_name].find_one(query, restrict)
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException("On Cls Get One Query")
    
    else:
      if json_data.has_key('_id'):
        del json_data['_id']
      return json_data

  @classmethod
  def get_by_query(cls, query, only=[]):
    restrict = dict.fromkeys(only, 1)
    collection_name = cls.__name__.lower()

    try:
      if not restrict:
        clusters = db[collection_name].find(query)
      else:
        clusters = db[collection_name].find(query, restrict)
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException("On Cls Get by Query")

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
      raise MongoDBHandleException("On Ensure indexes")

  @classmethod
  def clear_indexes(cls):
    collection_name = cls.__name__.lower()
    try:
      db[collection_name].drop_indexes()
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException("On Clear indexes")

  @classmethod
  def delete_all(cls):
    collection_name = cls.__name__.lower()
    db[collection_name].remove()

  def remove(self):
    collection_name = self.__class__.__name__.lower()
    try:
      db[collection_name].remove({'name': self.pk})
    except Exception, err:
      logger.info(err)
      raise MongoDBHandleException(
        "On Remove Document %s " % self.pk)

class Graphical:
  def traverse(self):
    d = {}
    nodes = self.next_nodes()
    if not nodes:
      return {self: []}
    
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


