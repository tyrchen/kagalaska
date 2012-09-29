# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.models import Place, Tag, Normal
from django.conf import settings

import json
import os

HOME = settings.DATA_PATH
ORIGIN_PATH = os.path.join(HOME, 'baseinfo.csv')
DEFAULT_SCORE = 8

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
            categories = json_data.get('categories', '')
            tag_type = class_name
            try:
              parent_slug = json_data.get('parent_slug', '')
              parent = Place.get_by_slug(parent_slug, json_format=True)
              place_parent = parent.get('name_zh', '')
            except Exception:
              place_parent = ''

            if not place_parent:
              tag = Tag(name=name, items=[item], score=float(DEFAULT_SCORE),
                        parents=categories, proxy=tag_type)
            else:
              tag = Tag(name=name, items=[item], score=float(DEFAULT_SCORE),
                        place_parent=place_parent, parents=categories,
                        proxy=tag_type)

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
          continue
        else:
          tag.set_score(score=float(score))

        print(name)

class NormalTagLoader(object):
  def __init__(self, path=None):
    self.path = path or os.path.join(HOME, 'normal_tags.csv')
    self.score = DEFAULT_SCORE*2

  def load(self):
    with open(name=self.path, mode='r') as f:
      for each_line in f.readlines():
        name, parents_str = each_line.decode('utf-8')[:-1].split('\t')
        parents = parents_str.split(',')
        print(name, parents)
        # To normal model
        exists = Normal.get_by_slug(name)
        if not exists:
          item = Normal(slug=name)
          print("Saving Normal Item %s" % name)
          item.save()

        for parent in parents:
          exists = Normal.get_by_slug(parent)
          if not exists:
            parent_item = Normal(slug=parent)
            print("Saving Normal Item %s" % parent)
            parent_item.save()

        # To tag model
        exists = Tag.get_by_name(name)
        if not exists:
          tag = Tag(name=name, parents=parents, score=self.score,
                    items=[{'slug': name, 'class': 'NORMAL'},],
                    proxy='NORMAL')
          print("Tag Item, %s" % name)
          tag.save()

        for parent in parents:
          exists = Tag.get_by_name(parent)
          if not exists:
            tag = Tag(name=parent, score=self.score,
                      items=[{'slug': parent, 'class': 'NORMAL'},],
                      proxy='NORMAL')
            print("Tag item %s " % parent)
            tag.save()
