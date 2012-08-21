# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.models import Place, Tag
from django.conf import settings

import json
import os

HOME = settings.DATA_PATH
ORIGIN_PATH = os.path.join(HOME, 'baseinfo.csv')

class PlaceInfoLoader(object):
  def __init__(self, origin_path=None):
    self.origin_path = origin_path if origin_path else ORIGIN_PATH

  def load(self, to_db=False, to_tag=False):
    with open(name=self.origin_path, mode='r') as f:
      for each_line in f.readlines():
        json_data = json.loads(each_line[:-1])
        save, format_data = self.format_info(json_data)
        if not save:
          continue

        try:
          print(json_data['name_zh'])
          if to_db:
            slug = json_data.pop('slug')
            place = Place(slug=slug, **json_data)
            place.save()

          if to_tag:
            slug = json_data.pop('slug')
            class_name = json_data.pop('class')
            name = json_data.pop('name_zh')
            item = {'slug': slug, 'class': class_name}
            tag = Tag(name=name, items=[item])
            tag.save()
            
        except Exception, err:
          print(err)
          continue

  def format_info(self, info):
    name = info.get('name_zh', '')
    if not name:
      return False, {}

    return True, info

class TagRelationLoader(object):

  def __init__(self, path=None):
    self.path = settings.RELATIONS_PATH if not path else path

  def load(self):
    with open(name=self.path, mode='r') as f:
      for each_line in f.readlines():
        name, score, parents_ = each_line.decode('utf-8')[:-1].split('\t')
        parents = filter(None, parents_.split(','))
        tag = Tag.get_by_name(name)

        if not tag:
          item = Tag(name=name, score=float(score), parents=parents)
          item.save()
        else:
          tag.add_parents(parents=parents)

        print(name)

class TagScoreLoader(object):
  def __init__(self, path=None):
    self.path = settings.WORDS_RATE_PATH if not path else path

  def load(self):
    with open(name=self.path, mode='r') as f:
      for each_line in f.readlines():
        name, score = each_line.decode('utf-8')[:-1].split('\t')
        tag = Tag.get_by_name(name)

        if not tag:
          item = Tag(name=name, score=float(score))
          item.save()
        else:
          tag.set_score(score=float(score))

        print(name)