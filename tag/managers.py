# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.models import Tag, Place, Normal

class TagRankService(object):
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
        self.item_city(item)

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