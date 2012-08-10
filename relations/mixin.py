# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import pymongo
from const import MONGO_DB, MONGO_HOST, MONGO_PORT
from log import get_logger

logger = get_logger()

connection = pymongo.Connection(host=MONGO_HOST, port=MONGO_PORT)
db = connection[MONGO_DB]

class Mongoable:
  def save(self):
    collection_name = self.__class__.__name__.lower()

    try:
      db[collection_name].insert(self.__dict__)
    except Exception, err:
      logger.info(err)
      return False
    else:
      return True

  def update(self, **kwargs):
    pass

  @classmethod
  def objects(cls):
    collection_name = cls.__name__.lower()
    all = db[collection_name].find()
    if not all:
      raise StopIteration

    for item in all:
      name = item.pop('name')
      id = str(item.pop('_id'))
      item.update(id=id)
      yield cls(name=name, **item)

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

  def delete_all(self):
    collection_name = self.__class__.__name__.lower()
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


