# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.mixin import Graphical, Mongoable
from tag.utils import TagFileHelper, to_str

class Tag(object, Mongoable, Graphical):
  indexes = [
      ({'name': 1}, {'unique': True})
    ]

  def __str__(self):
    return self.name

  def __unicode__(self):
    return self.name

  def __repr__(self):
    return to_str(self.name)

  def __init__(self, name, **kwargs):
    self.name = name
    self.__dict__.update(kwargs)

  @property
  def pk(self):
    return self.name

  @classmethod
  def load_from_dict(cls):
    helper = TagFileHelper()
    tags = helper.load_from_file()
    for tag in tags:
      item = cls(name=tag['name'], score=tag['score'], parents=tag['parents'])
      item.save()

  @classmethod
  def get_by_name(cls, name, json_format=False):
    query = {'name': name}
    json_data = cls.get_one_query(query)

    if not json_data:
      return None

    if not json_format:
      return Tag(name=json_data['name'], parents=json_data['parents'])
    return json_data

  def to_dict(self):
    return self.__dict__

  def next_nodes(self):
    names = getattr(self, 'parents', None)

    for name in names:
      yield self.__class__.get_by_name(name)

  def add_parents(self, parents, upsert=True):
    self.update({'$addToSet': {'parents': {'$each': parents}}}, upsert=upsert)

  def sub_parents(self, parents, upsert=True):
    self.update({'$pullAll': {'parents': parents}}, upsert=upsert)

  def reload(self):
    instance = self.__class__.get_by_name(name=self.name)
    self.__dict__ = instance.__dict__

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