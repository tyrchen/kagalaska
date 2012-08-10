# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from mixin import Graphical, Mongoable
from utils import TagFileHelper, to_str

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
