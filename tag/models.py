# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.mixin import Graphical, Mongoable
from tag.utils import TagFileHelper, to_str

from django.conf import settings

class Place(object, Mongoable):
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
    json_data = cls.get_one_query(query, only=only)

    if not json_data:
      if json_format:
        return {}
      else:
        return None

    del json_data['_id']
    if not json_format:
      return Place(**json_data)
    return json_data

  def get_parent(self):
    if self.__dict__.has_key('parent_slug'):
      return self.__class__.get_by_slug(self.__dict__['parent_slug'])
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
    json_data = cls.get_one_query(query, only=only)

    if not json_data:
      return None

    del json_data['_id']
    if not json_format:
      return Normal(**json_data)
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
    json_data = cls.get_one_query(query)

    if not json_data:
      return None

    del json_data['_id']
    if not json_format:
      return Tag(**json_data)
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
    names = getattr(self, 'parents', None)
    if not names:
      return []

    objs = []
    for name in names:
      obj = self.__class__.get_by_name(name)
      if not obj:
        continue
      objs.append(obj)
      
    return objs

  def add_parents(self, parents, upsert=True):
    self.update({'$addToSet': {'parents': {'$each': parents}}}, upsert=upsert)

  def sub_parents(self, parents, upsert=True):
    self.update({'$pullAll': {'parents': parents}}, upsert=upsert)

  def set_score(self, score=1.0, upsert=True):
    self.update({'$set': {'score': score}}, upsert)

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
        places.append(handle.get_by_slug(item['slug']))
      else:
        others.append(handle.get_by_slug(item['slug']))
    return {
      'places': places,
      'others': others
    }

class TagManager(object):
  def __init__(self):
    self.dict = {}
    self.to_cache()

  def to_cache(self):
    for tag in Tag.objects():
      name = tag.name
      parents = getattr(tag, 'parents', [])
      self.dict.update({
        name: parents
      })

  def has_tag(self, name):
    return self.dict.has_key(name)

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

  def parents(self, name):
    return self.dict.get(name, [])


  