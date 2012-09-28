# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.models import Tag, Place
from django.conf import settings

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
    try:
      tag.save()
    except Exception:
      return False

    self.add_tag(tag)
    return True

  def update(self, **json_data):
    name = json_data.get('name', '')
    self.remove(name)
    self.add(json_data)

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
    if not place_parent:
      self.tags.update({
        name: {
          'parents': parents,
          'items': items,
          'equal_to': equal_to
        }
      })
    else:
      self.tags.update({
          name: {
            'parents': parents,
            'items': items,
            'place_parent': place_parent,
            'equal_to': equal_to
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

    real_tag = tag.get('peer', None)
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
    return self.tags[tag_name]

  def get_city_or_normal(self, name, normal=True):
    tag = self.get_tag(name)
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
    items = tag['items']
    if not items:
      return 'NORMAL'

    return items[0].get('class', 'NORMAL')

  def get_parents(self, name):
    tag = self.get_tag(name)
    parents = tag.get('parents', [])
    return parents

  def get_item(self, name):
    tag = self.get_tag(name)
    items = tag.get('items', [])
    if not items:
      return {}

    return items[0]

  def clusters(self, tags, origin, top_n=1):
    city_dict = {}
    for name, value in tags:
      city = self.get_city_or_normal(name, normal=False)
      if not city:
        continue

      if city in city_dict:
        city_dict[city] += value
      else:
        city_dict[city] = value

    city_list = city_dict.items()
    def cmp(a, b):
      return int(a[1] - b[1])

    sorted_city_list = sorted(city_list, cmp=cmp, reverse=True)
    top_cities = sorted_city_list if len(sorted_city_list) < top_n else sorted_city_list[:top_n]
    top_cities_dict = {}
    for key, value in top_cities:
      top_cities_dict.update(
        {key: value}
      )

    places = {}
    others = {}

    for name, value in tags:
      class_name = self.get_type(name)
      if class_name == 'PLACE' and self.get_city_or_normal(name) in top_cities_dict:
        places.update({
          name: value}
        )
      elif class_name == 'NORMAL':
        parents = self.get_parents(name)
        for parent in parents:
          others.update({
            parent: value
          })

        if not parents:
          others.update({
            name: value
          })

      elif class_name in ('COUNTRY', 'CONTINENT') and not top_cities:
        places.update({
          name: value
        })

    places.update(top_cities_dict)

    for key, value in origin.items():
      class_name = self.get_type(name)
      if class_name == 'PLACE' and self.get_city_or_normal(name) in top_cities_dict:
        places.update({
          name: value}
        )

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