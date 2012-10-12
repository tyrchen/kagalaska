# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import copy
from tag.models import Tag, Place, Normal
from django.conf import settings
from tag.utils.util import rank_dict, dict_from_items, smart_print

DEFAULT_VALUE = settings.NEW_WORD_DEFAULT_VALUE

class Record(object):
  def __init__(self):
    self.tags_dict = {}
    self.slug_dict = {}

  def add(self, name, slugs):
    if isinstance(slugs, list):
      self.tags_dict.update({name: slugs})
      for slug in slugs:
        self.slug_dict.update({slug: name})
    else:
      self.tags_dict.update({name: slugs})
      self.slug_dict.update({slugs: name})

  def get_tag(self, slug):
    return self.slug_dict.get(slug, '')

  def get_items(self, name):
    return self.tags_dict.get(name, [])

class PlaceItemEntity(object):
  def __init__(self, slug, tag_name, **kwargs):
    self.slug = slug
    self.tag_name = tag_name
    self.category = kwargs.pop('class', 'PLACE')
    self.do_init(**kwargs)

  def __unicode__(self):
    return self.__dict__

  def do_init(self, **kwargs):
    self.__dict__.update(kwargs)

  def get_parent_slug(self):
    return getattr(self, 'parent_slug', '')

  @classmethod
  def direct_relation(cls, item_from, item_to):
    item_from_parent_slug = item_from.get_parent_slug()
    if_relation = bool(item_from_parent_slug) and item_from_parent_slug == item_to.slug
    return if_relation

class NormalItemEntity(object):
  def __init__(self, slug, tag_name, parents=[], **kwargs):
    kwargs.pop('class', '')
    self.slug = slug
    self.tag_name = tag_name
    self.parents = parents
    self.category = 'NORMAL'
    self.__dict__.update(kwargs)

  @classmethod
  def direct_relation(cls, item_from, item_to):
    parent_slug = item_to.slug
    return parent_slug in item_from.parents

class InMemoryItems(object):
  def __init__(self):
    self.items = {}

  def add(self, slug, item_instance):
    self.items.update({slug: item_instance})

  def get(self, slug):
    return self.items.get(slug, None)

  def exists(self, slug):
    return self.items.has_key(slug)

  def place_parent(self, place_item):
    parent_slug = place_item.get_parent_slug()
    return self.get(parent_slug)

  def place_all_parents(self, slug, value, increment=0.1):
    smart_print(slug, "in place_all_parents")
    exists = self.exists(slug)
    if not exists:
      return [], [], []

    origin = self.get(slug)
    if origin.category == 'NORMAL':
      return [], [], []

    countries = []
    cities = []
    places = []
    if origin.category == 'PLACE':
      places.append((origin, value))
    elif origin.category == 'AREA':
      cities.append((origin, value))
    else:
      countries.append((origin, value))

    value += increment
    for place, _ in places:
      parent = self.place_parent(place)
      if not parent:
        continue

      cities.append((parent, value))
    value += increment

    for city, _ in cities:
      parent = self.place_parent(city)
      if not parent:
        continue

      countries.append((parent, value))

    return places, cities, countries

  def normal_parents(self, normal_item, value, increment=0.1):
    parent_names = normal_item.parents
    parents = []
    available = []

    value += increment
    for name in parent_names:
      parent = self.get(name)
      if not parent:
        continue
      else:
        parents.append((parent, value))
        available.append((parent, value))

    while available:
      temp = []
      for item, item_value in available:
        available_parents = self.normal_parents(item, item_value+increment)
        parents.extend(available_parents)
        temp.extend(available_parents)
      available = temp

    return parents

  def normal_all_parents(self, slug, value, increment=0.1):
    exists = self.exists(slug)
    if not exists:
      return []

    origin = self.get(slug)
    if origin.category != 'NORMAL':
      return []

    parents = self.normal_parents(origin, value, increment)
    return parents

class TagEntity(object):
  def __init__(self, name, score=1.0,
               equal_to='', parents=[], items=[]):
    self.name = name
    self.equal_to = equal_to
    self.parents = parents
    self.score = score
    self.items = items

  def __unicode__(self):
    return self.__dict__

class InMemoryTags(object):
  def __init__(self):
    self.tags = {}

  def add(self, name, tag_instance):
    self.tags.update({name: tag_instance})

  def get(self, name):
    instance = self.tags.get(name, None)
    if not instance:
      return None

    equal_to = instance.equal_to
    if equal_to:
      return self.get(equal_to)
    else:
      return instance

  def exists(self, name):
    return self.tags.has_key(name)

  def delete(self, name):
    exists = self.exists(name)
    if exists:
      del self.tags[name]

class TagService(object):
  def __init__(self):
    self.memory_tags = InMemoryTags()
    self.memory_normal_items = InMemoryItems()
    self.memory_place_items = InMemoryItems()
    self.to_cache()

  def generate_tag(self, name, score=DEFAULT_VALUE, items=[], **kwargs):
    return Tag(name=name, score=score, items=items, **kwargs)

  def add(self, **json_data):
    tag = self.generate_tag(**json_data)
    tag.save()
    self.add_tag(tag, force_add=True)

  def update(self, **json_data):
    self.remove(**json_data)
    self.add(**json_data)

  def remove(self, **json_data):
    name = json_data.get('name', '')
    if not self.memory_tags.exists(name):
      return

    self.memory_tags.delete(name)
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

  def add_tag(self, tag, force_add=False):
    name = tag.name
    if not name:
      return

    score = getattr(tag, 'score', 1.0)
    parents = getattr(tag, 'parents', [])
    items = getattr(tag, 'items', [])
    instance_items = []
    equal_to = getattr(tag, 'equal_to', '')
    for item in items:
      slug = item['slug'] or name
      if (not force_add) and (self.memory_normal_items.exists(slug) or self.memory_place_items.exists(slug)):
        continue

      category = item['class']
      if category == 'NORMAL':
        item_info = Normal.get_by_slug(slug, json_format=True)
        if not item_info:
          continue

        item_instance = NormalItemEntity(tag_name=name, parents=parents, **item_info)
        self.memory_normal_items.add(slug, item_instance)
      else:
        item_info = Place.get_by_slug(slug, json_format=True)
        if not item_info:
          continue

        item_instance = PlaceItemEntity(tag_name=name, **item_info)
        self.memory_place_items.add(slug, item_instance)
      instance_items.append(item_instance)

    tag_instance = TagEntity(name, score=score, equal_to=equal_to,
                                 parents=parents, items=instance_items)
    self.memory_tags.add(name, tag_instance)


  def filter(self, tags_dict):
    validated_dict = {}
    for name in tags_dict.keys():
      tag_item = self.memory_tags.get(name)
      if not tag_item or len(tag_item.name) < 2:
        continue

      validated_dict.update({
        tag_item: tags_dict[name]
      })

    return validated_dict

  def guess(self, tags, top_n=1):
    countries = []
    cities = []
    places = []
    normals = []

    smart_print(tags, "in guess tags")
    for tag, value in tags:
      items = tag.items
      smart_print(items, "tag_items")
      for item in items:
        category = item.category
        if category == 'NORMAL':
          normals.append((item, value))
        else:
          item_places, item_cities, item_countries \
          = self.memory_place_items.place_all_parents(item.slug, value)
          countries.extend(item_countries)
          cities.extend(item_cities)
          places.extend(item_places)

      for parent_name in tag.parents:
        parent = self.memory_normal_items.get(parent_name)
        if not parent:
          continue
        else:
          normals.append((parent, value))

    smart_print(countries, "countries")
    smart_print(cities, 'cities')
    smart_print(places, 'places')
    smart_print(normals, 'normals')
    guessed_places, guessed_cities = self.do_guess_places(countries, cities, places, top_n)
    smart_print(guessed_places, "guessed places")
    smart_print(guessed_cities, "guessed cities")
    guessed_normals = self.do_guess_normals(normals, top_n)
    smart_print(guessed_normals, "guessed normals")
    return guessed_places, guessed_cities, guessed_normals

  def do_guess_places(self, countries, cities, places, top=1):
    countries_dict = {}
    cities_dict = {}
    places_dict = {}
    dict_from_items(countries_dict, countries)
    dict_from_items(cities_dict, cities)
    dict_from_items(places_dict, places)
    smart_print(countries_dict, "countries_dict")
    smart_print(cities_dict, "cities_dict")
    smart_print(places_dict, "places_dict")

    top_country = rank_dict(countries_dict, top=1)
    available_countries = [country for country, _ in top_country]

    top_cities = rank_dict(cities_dict, top=top)
    top_city = []
    for city, value in top_cities:
      relations = []
      for available_country in available_countries:
        relation = PlaceItemEntity.direct_relation(city, available_country)
        relations.append(relation)
      if any(relations):
        top_city.append((city, value))
        break

    available_cities = [city for city, _ in top_city]
    top_places = []

    for place, value in places:
      relations = []
      for city in available_cities:
        relation = PlaceItemEntity.direct_relation(place, city)
        relations.append(relation)
      if any(relations):
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

    smart_print(normals, "in guess normals")
    available = normals[0: top]
    normal_tags_dict = {}
    dict_from_items(normal_tags_dict, available)
    parents_list = []

    for normal_item, value in available:
      parents_list.extend(self.memory_normal_items.normal_all_parents(normal_item.slug, value))
    smart_print(parents_list, "parent_list")
    dict_from_items(normal_tags_dict, parents_list)

    top_normals = rank_dict(normal_tags_dict, top=1)
    for key, _ in normal_tags_dict.items():
      relations = []
      for top_normal, _ in top_normals:
        relation = top_normal == key or NormalItemEntity.direct_relation(key, top_normal)
        relations.append(relation)
      if not any(relations):
        del normal_tags_dict[key]

    return rank_dict(normal_tags_dict, top=top)

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

    for place_item, score in places.items():
      if place_item.category == 'AREA':
        item_dict = self.do_format(place_item, score)
        show.update(item_dict)
        cities.update(item_dict)
      else:
        item_dict = self.do_format(place_item, score)
        show.update(item_dict)

    for normal_item, score in others.items():
      item_dict = self.do_format(normal_item, score)
      show.update(item_dict)

    return {
      'show': show,
      'hide': hide,
      'cities': cities
    }

  def do_format(self, item, score):
    if item.category == 'NORMAL':
      slug = ''
    else:
      slug = item.slug

    return {
      item.tag_name: {
        'score': score,
        'slug': slug
      }
    }