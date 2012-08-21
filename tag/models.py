# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.mixin import Graphical, Mongoable
from tag.utils import to_str
from django.conf import settings
from exceptions import NotExistsException, MongoDBHandleException
from validate import item_exists, item_in

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

class TagManager(object):
  def __init__(self):
    self.tags = {}
    self.items = {}
    self.to_cache()

  def to_cache(self):
    for tag in Tag.objects():
      name = tag.name
      parents = getattr(tag, 'parents', [])
      items = tag.get_items()['places']
      self.tags.update({
        name: {
          'parents': parents,
          'items': items
        }
      })

      for item in items:
        if not item['class'] in Tag.mapping:
          continue

        if self.has_slug(item['slug']):
          continue

        obj = Place.get_by_slug(item['slug'], json_format=True)
        if not obj:
          continue

        slug = obj.get('slug', '')
        if not slug:
          continue

        self.items.update({slug: obj})

  def has_tag(self, name):
    return self.tags.has_key(name)

  def traverse(self, name):
    d = {}

    if not self.has_tag(name):
      return d

    parents = self.parents(name)
    d.update({
      name: parents
    })
    for parent in parents:
      if not parent:
        continue

      if not self.parents(parent):
        continue

      d.update(self.traverse(parent))

    return d

  def format_tags(self, success, fail, city_slugs=[]):
    fail_result = {}
    success_result = {}

    for tag in fail:
      b, item = self.format_tag({tag: fail[tag]}, city_slugs=[])
      fail_result.update(item)

    for tag in success:
      b, item = self.format_tag({tag: success[tag]}, city_slugs=city_slugs)
      if not b:
        fail_result.update(item)
      else:
        success_result.update(item)

    return success_result, fail_result


  def format_tag(self, tag, city_slugs=[]):
    def extra_condition(item, city_slugs):
      if not city_slugs:
        return True

      if item.get('class', '') == 'PLACE':
        return self.items[item['slug']].get('parent_slug', '') in city_slugs

      elif item.get('class', '') == 'AREA':
        return self.items[item['slug']].get('slug', '') in city_slugs

      else:
        return True

    items = self.tags[tag.items()[0][0]]['items']
    if not items:
      return True, {
        tag.items()[0][0]: {
          'score': tag.items()[0][1],
          'slug': ''
        }
      }
    else:
      recommend = ''
      for item in items:
        if item.get('class', '') == 'PLACE' and extra_condition(item, city_slugs):
          recommend = item
          break

        elif item.get('class', '') == 'AREA' and extra_condition(item, city_slugs):
          recommend = item

      if recommend:
        return True, {
          tag.items()[0][0]: {
            'score': tag.items()[0][1],
            'slug': recommend['slug']
          }
        }
      else:
        return False, {
          tag.items()[0][0]: {
            'score': tag.items()[0][1],
            'slug': items[0]['slug']
          }
        }

  def parents(self, name):
    item = self.tags.get(name, [])
    if not item:
      return []

    parents = item.get('parents', [])
    return parents

  def has_slug(self, slug):
    return self.items.has_key(slug)

  def get_item(self, slug):
    return self.items.get(slug, {})

  def tag_cities(self, name, weight=1.0):
    if not self.has_tag(name):
      return []

    cities = []
    items = self.tags[name]['items']
    for item in items:
      city = self.item_city(item)
      if not city:
        continue
        
      else:
        d = {
          city['name_zh']: {
              'slug': city['slug'],
              'score': weight
          }
        }
        cities.append(d)
    return cities 

  def item_city(self, item):
    if item['class'] == 'PLACE':
      try:
        item = self.get_item(item['slug'])
        parent_slug = item.get('parent_slug', '')
        parent = self.get_item(parent_slug)
      except Exception:
        return {}

      else:
        return parent

    elif item['class'] == 'AREA':
      try:
        item = self.get_item(item['slug'])
      except Exception:
        return {}

      else:
        return item

    else:
      return {}