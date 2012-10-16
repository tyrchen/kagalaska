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
  pk_name =  'slug'

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

  def update(self, **kwargs):
    proxy = kwargs.pop('proxy', 'PLACE')
    obj = {}
    for key, value in kwargs.items():
      obj.update({
        key: value
      })
    obj.update({'class': proxy})

    super(Place, self).update(obj={'$set': obj})

  @classmethod
  def cls_update(cls, slug, **kwargs):
    proxy = kwargs.pop('proxy', 'PLACE')
    obj = {}
    for key, value in kwargs.items():
      obj.update({
          key: value
      })
    obj.update({'class': proxy})
    super(Place, cls).cls_update(name=slug, obj={'$set': obj})

  def to_dict(self):
    return vars(self)

  @classmethod
  def get_parent_by_slug(cls, slug):
    place = cls.get_by_slug(slug)
    if not place:
      return None
    parent_slug = getattr(place, 'parent_slug', '')
    if not parent_slug:
      return None
    parent = cls.get_by_slug(parent_slug)
    return parent

class Normal(object, Mongoable):
  pk_name = 'slug'

  indexes = [
    ({'slug': 1}, {'unique': True})
  ]

  def __init__(self, slug, **kwargs):
    self.slug = slug
    self.__dict__.update(kwargs)

  @classmethod
  def cls_update(cls, slug, **kwargs):
    slug = slug
    score = kwargs.pop('score', 1.0)
    obj = {
      'slug': slug,
      'score': score
    }
    super(Normal, cls).cls_update(name=slug, obj={'$set': obj})

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
      return None

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
  @ equal_to
  @ place_parent: '北京',
  @ proxy NORMAL or PLACE or AREA or COUNTRY or CONTINENT
  @ items: [{slug: 'bei-jing-bei-jing-di-qu-china, 'class':'AREA' },]
  """
  pk_name = 'name'

  indexes = [
      ({'name': 1}, {'unique': True})
    ]

  mapping = {
    'AREA': Place,
    'PLACE': Place,
    'COUNTRY': Place,
    'CONTINENT': Place,
    'NORMAL': Normal
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
    proxy = 'NORMAL'
    if kwargs.has_key('place_parent'):
      place_parent = kwargs.get('place_parent', '')
    else:
      place_parent = ''
      for item in self.items:
        if item.get('class', 'NORMAL') in ('PLACE', 'AREA', 'COUNTRY', 'CONTINENT'):
          proxy = item.get('class', 'NORMAL')
          parent_instance = Place.get_parent_by_slug(item.get('slug', ''))
          if not parent_instance:
            continue
          else:
            place_parent = getattr(parent_instance, 'name_zh', '')

    self.place_parent = place_parent
    self.proxy = proxy
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
      logger.info(e)
      return None

    else:
      if not json_format:
        return Tag(**json_data)
      else:
        return json_data

  @classmethod
  def load_from_path(cls, path=settings.TAGS_RESOURCE_PATH):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    tag_place_cache = {}

    for line in lines[1:]:
      tag = cls._do_load(line)
      if tag.proxy != 'NORMAL':
        place_slug = tag.items[0]['slug']
        tag_name = tag.equal_to or tag.name
        tag_place_cache.update({
          place_slug: tag_name
        })

    Tag.delete_all()
    for line in lines[1:]:
      tag = cls._do_load(line)
      place_slug = tag.items[0]['slug']
      place_info = Place.get_by_slug(place_slug, json_format=True)
      parent_slug = place_info.get('parent_slug', '') if place_info else ''
      if parent_slug in tag_place_cache:
        tag.place_parent = tag_place_cache[parent_slug]

      print(tag.name)
      if tag.name.strip():
        tag.save()

  @classmethod
  def _do_load(cls, line):
    line = line[:-1].decode('utf-8')
    name, score, parents_str, equal_to, items_str = line.split('\t')
    parents = parents_str.split(',')
    items = items_str.split(',')
    formatted_items = []

    try:
      score = settings.NEW_WORD_DEFAULT_VALUE
    except Exception:
      score = settings.NEW_WORD_DEFAULT_VALUE

    class_name = 'NORMAL'
    for item in items:
      try:
        slug, class_name = item.split('__')
      except Exception:
        slug, class_name = item.split('__')[0], 'NORMAL'
      formatted_items.append({
        'slug': slug,
        'class': class_name
      })
    return Tag(name=name, score=score, proxy=class_name, items=formatted_items,
               parents=parents, equal_to=equal_to)

  @classmethod
  def get_many_by_names(cls, names, json_format=True):
    tags = []
    for name in names:
      tag = cls.get_by_name(name, json_format)
      if not tag:
        continue
      tags.append(tag)
    return tags

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

  @classmethod
  def cls_to_file(cls, path=settings.TAG_TO_FILE_PATH):
    file = open(path, 'w')

    tags = cls.objects()
    for tag in tags:
      line = '%d %s\n' %(len(tag.name), tag.name)
      file.write(line.encode('utf-8'))
    file.close()
    return path

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
      handle = self.mapping.get(item.get('class', 'NORMAL'))
      if handle is Place:
        item = handle.get_by_slug(item['slug'], only=['slug', 'class'], json_format=True)
        if item:
          places.append(item)
      else:
        try:
          item = handle.get_by_slug(item['slug'], json_format=True)
        except:
          print(self.items)
        if item:
          others.append(item)
    return {
      'places': places,
      'others': others
    }