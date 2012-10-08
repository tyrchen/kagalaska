# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import copy
from tag.models import Tag, Place
from django.conf import settings
from tag.utils.util import rank_dict, dict_from_items

DEFAULT_VALUE = settings.NEW_WORD_DEFAULT_VALUE

class TagService(object):
  def __init__(self):
    self.tags = {}
    self.items = {}
    self.to_cache()

  def generate_tag(self, name, score=DEFAULT_VALUE, items=[], **kwargs):
    return Tag(name=name, score=score, items=items, **kwargs)

  def add(self, **json_data):
    tag = self.generate_tag(**json_data)
    tag.save()
    self.add_tag(tag)

  def update(self, **json_data):
    self.remove(**json_data)
    self.add(**json_data)

  def remove(self, **json_data):
    name = json_data.get('name', '')
    if not name in self.tags:
      return

    del self.tags[name]
    tag = Tag.get_by_name(name)
    tag.remove()

  def get_names(self, **json_data):
    names = json_data.get('name', [])
    if not names:
      return

    if isinstance(names, basestring):
      names = [names, ]

    return Tag.get_many_by_names(names)

  def to_cache(self):
    """
    考虑load的时候通过文件
    """
    for tag in Tag.objects():
      self.add_tag(tag)

  def add_tag(self, tag):
    name = tag.name
    parents = getattr(tag, 'parents', [])
    items_dict = tag.get_items()
    items = items_dict['places'] or items_dict['others']
    place_parent = getattr(tag, 'place_parent', '')
    equal_to = getattr(tag, 'equal_to', '')
    proxy = getattr(tag, 'proxy', 'NORMAL')
    self.tags.update({
      name: {
        'parents': parents,
        'items': items,
        'place_parent': place_parent,
        'equal_to': equal_to,
        'proxy': proxy
      }
      })

    for item in items:
      if self.has_slug(item['slug']):
        continue

      obj = Place.get_by_slug(item['slug'], json_format=True)
      if not obj:
        continue

      slug = obj.get('slug', '')
      if not slug:
        continue

      self.items.update({slug: obj})


  def has_slug(self, slug):
    return self.items.has_key(slug)

  def exists_tag(self, tag):
    return self.tags.has_key(tag)

  def get_tag_name(self, name):
    """
    得到Tag， 如果有同义词，取同义词。
    """
    tag = self.tags.get(name, '')
    if not tag:
      return None

    real_tag = tag.get('equal_to', None)
    return real_tag or name

  def filter(self, tags_dict):
    validated_dict = {}
    for name in tags_dict.keys():
      tag_name = self.get_tag_name(name)
      if not tag_name or len(tag_name) < 2:
        continue

      validated_dict.update({
        tag_name: tags_dict[tag_name]
      })

    return validated_dict

  def get_tag(self, name):
    tag_name = self.get_tag_name(name)
    if not tag_name:
      return None

    return self.tags[tag_name]

  def get_city_or_normal(self, name, normal=True):
    tag = self.get_tag(name)
    if not tag:
      return None

    tag_type = self.get_type(name)
    if tag_type == 'PLACE':
      place_parent = tag.get('place_parent', '')
    elif tag_type == 'AREA' or (tag_type == 'NORMAL' and normal):
      place_parent = name
    else:
      place_parent = ''
    return place_parent or None

  def get_type(self, name):
    tag = self.get_tag(name)
    if not tag:
      return 'NORMAL'

    return tag.get('proxy', 'NORMAL')

  def get_parents(self, name):
    tag = self.get_tag(name)
    if not tag:
      return []

    parents = tag.get('parents', [])
    return filter(None, parents)

  def get_item(self, name):
    tag = self.get_tag(name)
    if not tag:
      return {}

    items = tag.get('items', [])
    if not items:
      return {}

    return items[0]

  def get_place_parent(self, name):
    tag = self.get_tag(name)
    if not tag:
      return None

    return tag.get('place_parent', None)

  def guess(self, tags, top_n=1):
    countries = []
    cities = []
    places = []
    normals = []

    for name, value in tags:
      proxy = self.get_type(name)
      if proxy == 'NORMAL':
        normals.append((name, value))
      elif proxy == 'COUNTRY':
        countries.append((name, value))
      elif proxy == 'AREA':
        cities.append((name, value))
      elif proxy == 'PLACE':
        places.append((name, value))

    guessed_places, guessed_cities = self.do_guess_places(countries, cities, places, top_n)
    guessed_normals = self.do_guess_normals(normals, top_n)
    return guessed_places, guessed_cities, guessed_normals

  def do_guess_places(self, countries, cities, places, top=1):
    guessed_cities = self.guess_parents(places)
    def merge_items_to_dict(items, aim_dict):
      for item, value in items:
        if item in aim_dict:
          aim_dict[item] += value
        else:
          aim_dict.update({
            item: value
          })
      return aim_dict

    guessed_cities = merge_items_to_dict(cities, guessed_cities)
    guessed_countries = self.guess_parents(guessed_cities.items())
    guessed_countries = merge_items_to_dict(countries, guessed_countries)
    top_country = rank_dict(guessed_countries, top=1)
    available_country = [country for country, _ in top_country]
    top_cities = rank_dict(guessed_cities)
    top_city = []
    top_places = []
    for city, value in top_cities:
      if self.get_place_parent(city) in available_country:
        top_city.append((city, value + 1))
        break

    available_cities = [city for city, _ in top_city]
    for place, value in places:
      if self.get_place_parent(place) in available_cities:
        top_places.append((place, value))

    if not top_places and not top_city:
      return top_country, []
    else:
      result = []
      result.extend(top_places[: top-1])
      result.extend(top_city)
      return result, top_city

  def do_guess_normals(self, normals, top=1):
    if not normals:
      return []

    available = normals[0: top]
    normal_tags_dict = {}
    dict_from_items(normal_tags_dict, available)

    for key, value in available:
      parents = self.get_parents(key)
      for parent in parents:
        available.append((parent, value + 0.01))

    while available:
      parents_list = []
      for key, value in available:
        parents = self.get_parents(key)
        for parent in parents:
          parents_list.append((parent, value + 0.01))
      dict_from_items(normal_tags_dict, parents_list)
      available = copy.deepcopy(parents_list)

    return rank_dict(normal_tags_dict, top=top)

  def guess_parents(self, children):
    parents = {}
    for child, value in children:
      parent = self.get_place_parent(child)
      parent_value = value + 0.01 # 让父级浮出

      if not parent:
        continue

      elif parent in parents:
        parents[parent] += parent_value
      else:
        parents.update({
          parent: parent_value
        })
    return parents

  def clusters(self, tags, origin, top_n=1): # 还没用到所有的分词和限制个数 TODO
    guessed_places, guessed_cities, guessed_normal = self.guess(tags, top_n)
    places = {}
    others = {}

    for key, value in guessed_places:
      if key in places:
        places[key] += value
      else:
        places.update({
          key: value
        })

    for key, value in guessed_normal:
      if key in others:
        others[key] += value
      else:
        others.update({
          key: value
        })
    return places, others

  def format(self, places, others):
    show = {}
    hide = {}
    cities = {}

    for name, score in places.items():
      class_name = self.get_type(name)
      if class_name == 'AREA':
        item_dict = self.do_format(name, score)
        show.update(item_dict)
        cities.update(item_dict)
      else:
        item_dict = self.do_format(name, score)
        show.update(item_dict)

    for name, score in others.items():
      item_dict = self.do_format(name, score)
      show.update(item_dict)

    return {
      'show': show,
      'hide': hide,
      'cities': cities
    }

  def do_format(self, name, score):
    item = self.get_item(name)
    class_name = item.get('class', 'NORMAL')
    if class_name == 'NORMAL':
      slug = ''
    else:
      slug = item.get('slug', '')

    return {
      name: {
        'score': score,
        'slug': slug
      }
    }