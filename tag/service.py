# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import copy
from tag.models import Tag, Place
from django.conf import settings
from tag.utils.util import rank_dict, dict_from_items, smart_print

DEFAULT_VALUE = settings.NEW_WORD_DEFAULT_VALUE

class TagService(object):

  class InMemoryTag(object):
    def __init__(self, name, service_ref=None):
      self.service = service_ref
      tag = self.service.tags.get(name, {})
      real_tag = tag.get('equal_to', '')
      real_name = real_tag or name
      tag = self.service.tags.get(real_name, {})
      self.__dict__.update(tag)

    def get_name(self):
      return getattr(self, 'name', '')

    def get_place_parent(self):
      place_parent_name = getattr(self, 'place_parent', '')
      return self.service.InMemoryTag(place_parent_name, self.service)

    def get_proxy(self):
      return getattr(self, 'proxy', 'NORMAL')

    def get_parents(self):
      parent_names = getattr(self, 'parents', [])
      parents = []
      for name in parent_names:
        parents.append(self.service.InMemoryTag(name, self.service))
      return parents

    def get_items(self):
      item_ref = getattr(self, 'items', [])
      item_names = [item['slug'] for item in item_ref]
      items = filter(None, [self.service.items.get(item_name, None)
                           for item_name in item_names])
      if not items:
        return {}
      else:
        return items[0]

    def tag_info(self):
      return self.service.tags.get(self.get_name(), {})

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
        'name': name,
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

  def filter(self, tags_dict):
    validated_dict = {}
    for name in tags_dict.keys():
      tag_item = self.InMemoryTag(name, self)
      tag_name = tag_item.get_name()
      if not tag_name or len(tag_name) < 2:
        continue

      validated_dict.update({
        tag_name: tags_dict[tag_name]
      })

    return validated_dict

  def get_city_or_normal(self, name, normal=True):
    tag = self.InMemoryTag(name, self)
    tag_type = tag.get_proxy()
    if tag_type == 'PLACE':
      place_parent = tag.get_place_parent()
    elif tag_type == 'AREA' or (tag_type == 'NORMAL' and normal):
      place_parent = tag.get_name()
    else:
      place_parent = ''
    return place_parent or None

  def guess(self, tags, top_n=1):
    countries = []
    cities = []
    places = []
    normals = []

    for name, value in tags:
      tag_item = self.InMemoryTag(name, self)
      proxy = tag_item.get_proxy()
      if proxy == 'NORMAL':
        normals.append((tag_item.get_name(), value))
      elif proxy == 'COUNTRY':
        countries.append((tag_item.get_name(), value))
      elif proxy == 'AREA':
        cities.append((tag_item.get_name(), value))
      elif proxy == 'PLACE':
        places.append((tag_item.get_name(), value))

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
    smart_print(guessed_cities, "In do guess places, guess cities")
    guessed_countries = self.guess_parents(guessed_cities.items())
    guessed_countries = merge_items_to_dict(countries, guessed_countries)
    top_country = rank_dict(guessed_countries, top=1)
    smart_print(top_country, "top_country")
    available_country = [country for country, _ in top_country]
    top_cities = rank_dict(guessed_cities)
    top_city = []
    top_places = []
    for city, value in top_cities:
      city_tag = self.InMemoryTag(city, self)
      smart_print(city_tag.__dict__, city_tag.get_name())
      parent = city_tag.get_place_parent()
      if parent.get_name() in available_country:
        top_city.append((city_tag.get_name(), value + 1))
        break

    available_cities = [city for city, _ in top_city]
    smart_print(available_cities, "available_cities")
    for place, value in places:
      place_tag = self.InMemoryTag(place, self)
      parent = place_tag.get_place_parent()
      if parent.get_name() in available_cities:
        top_places.append((place_tag.get_name(), value))

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
      normal_tag = self.InMemoryTag(key, self)
      parents = normal_tag.get_parents()
      for parent in parents:
        if parent.get_name():
          available.append((parent.get_name(), value + 0.01))

    while available:
      parents_list = []
      for key, value in available:
        available_tag = self.InMemoryTag(key, self)
        parents = available_tag.get_parents()
        for parent in parents:
          if parent.get_name():
            parents_list.append((parent.get_name(), value + 0.01))

      dict_from_items(normal_tags_dict, parents_list)
      available = copy.deepcopy(parents_list)

    return rank_dict(normal_tags_dict, top=top)

  def guess_parents(self, children):
    parents = {}
    for child, value in children:
      tag_item = self.InMemoryTag(child, self)
      parent = tag_item.get_place_parent()
      parent_value = value + 0.01 # 让父级浮出

      if not parent.get_name():
        continue

      elif parent in parents:
        parents[parent.get_name()] += parent_value
      else:
        parents.update({
          parent.get_name(): parent_value
        })
    return parents


  def clusters(self, tags, origin, top_n=1): # 还没用到所有的分词和限制个数 TODO
    smart_print(tags, 'cluster tags')
    guessed_places, guessed_cities, guessed_normal = self.guess(tags, top_n)
    smart_print(guessed_places, "guessed places")
    smart_print(guessed_places, "guessed cities")
    smart_print(guessed_normal, "guessed normal")
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
      tag = self.InMemoryTag(name, self)
      class_name = tag.get_proxy()
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
    tag = self.InMemoryTag(name, self)
    item = tag.get_items()
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