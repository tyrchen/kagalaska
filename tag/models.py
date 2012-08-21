# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.mixins import Graphical, Mongoable
from tag.utils import to_str
from django.conf import settings
from exceptions import NotExistsException, MongoDBHandleException

import logging

logger = logging.getLogger(__name__)

class Place(object, Mongoable):
  indexes = [
     ({'slug': 1}, {'unique': True})
  ]

  ONLY_MAPPING = {
    'ONLY_SLUG': ['slug', ],
    'ONLY_USEFUL': ['slug', 'name_zh', 'name_en', 'class', 'centroid', 'parent_slug'],
    'ALL': []
  }

  def __init__(self, slug, **kwargs):
    self.slug = slug
    self.__dict__.update(kwargs)

  @property
  def pk(self):
    return self.slug

  @classmethod
  def get_by_slug(cls, slug, only=ONLY_MAPPING['ONLY_USEFUL'], json_format=False):
    only = only
    query = {'slug': slug}

    try:
      json_data = cls.get_one_query(query, only=only)
      
    except (NotExistsException, MongoDBHandleException):
      return None
    except Exception, e:
      logger.info(e)
      return None

    else:
      if not json_format:
        return Place(**json_data)
      else:
        return json_data

  def get_parent(self):
    if self.__dict__.has_key('parent_slug'):
      return self.__class__.get_by_slug(self.__dict__['parent_slug'])
    else:
      return None

  def to_dict(self):
    return vars(self)

class Normal(object, Mongoable):
  indexes = [
    ({'slug': 1}, {'unique': True})
  ]

  def __init__(self, slug, **kwargs):
    self.slug = slug
    self.__dict__.update(kwargs)

  @property
  def pk(self):
    return self.slug

  @classmethod
  def get_by_slug(cls, slug, only_slug=False, json_format=False):
    only = [] if not only_slug else ['slug', ]
    query = {'slug': slug}

    try:
      json_data = cls.get_one_query(query, only=only)

    except (NotExistsException, MongoDBHandleException):
      return None
    except Exception, e:
      logger.info(e)

    else:
      if not json_format:
        return Normal(**json_data)
      else:
        return json_data

class Tag(object, Mongoable, Graphical):
  """
  Tag Model:
  @ name
  @ score
  @ parents
  @ similarities
  @ peer
  @ items: {slug: 'bei-jing-bei-jing-di-qu-china, 'class':'AREA' }
  """

  indexes = [
      ({'name': 1}, {'unique': True})
    ]

  mapping = {
    'AREA': Place,
    'PLACE': Place,
    'COUNTRY': Place,
    'CONTINENT': Place,
  }

  def __str__(self):
    return self.name

  def __unicode__(self):
    return self.name

  def __repr__(self):
    return to_str(self.name)

  def __init__(self, name, score=1.0, items=[], **kwargs):
    self.name = name
    self.score = score
    self.items = items
    self.__dict__.update(kwargs)

  @property
  def pk(self):
    return self.name

  @classmethod
  def cls_set_score(cls, name, score=1.0, upsert=True):
    cls.cls_update(name=name, obj={'$set': {'score': score}}, upsert=upsert)

  @classmethod
  def cls_add_parents(cls, name, parents=[], upsert=True):
    cls.cls_update(name=name, obj={'$addToSet': {'parents': {'$each': parents}}},
                   upsert=upsert)

  @classmethod
  def get_by_name(cls, name, json_format=False):
    query = {'name': name}

    try:
      json_data = cls.get_one_query(query)
    except (NotExistsException, MongoDBHandleException):
      return None
    except Exception, e:
      logger(e)
      return None

    else:
      if not json_format:
        return Tag(**json_data)
      else:
        return json_data

  @classmethod
  def cls_to_rate(cls, default=6):
    path = settings.WORDS_RATE_PATH
    file = open(path, 'a')
    
    objs = cls.objects()
    for obj in objs:
      name = obj.name
      score = obj.score if obj.score != 1 else default
      line = '%s\t%.4f\n' %(name, score)
      file.write(line.encode('utf-8'))

    file.close()

  def to_dict(self):
    return vars(self)

  def next_nodes(self):
    try:
      names = self.parents
    except Exception, e:
      logger.info(e)
      return []

    else:
      nodes = []
      for name in names:
        node = self.__class__.get_by_name(name)
        if not node:
          continue
        nodes.append(node)
      return nodes

  def add_parents(self, parents, upsert=True):
    try:
      self.update({'$addToSet': {'parents': {'$each': parents}}}, upsert=upsert)
    except Exception:
      pass

  def sub_parents(self, parents, upsert=True):
    try:
      self.update({'$pullAll': {'parents': parents}}, upsert=upsert)
    except Exception:
      pass

  def set_score(self, score=1.0, upsert=True):
    try:
      self.update({'$set': {'score': score}}, upsert)
    except Exception:
      pass

  def reload(self):
    instance = self.__class__.get_by_name(name=self.name)
    self.__dict__ = instance.__dict__

  def get_items(self):
    """
     TODO 耦合太高，结果会出现依赖。
    """
    places = []
    others = []
    for item in self.items:
      handle = self.mapping.get(item['class'], Normal)
      if handle is Place:
        places.append(handle.get_by_slug(item['slug'], only=['slug', 'class'], json_format=True))
      else:
        others.append(handle.get_by_slug(item['slug'], only=['slug', 'class'], json_format=True))
    return {
      'places': places,
      'others': others
    }