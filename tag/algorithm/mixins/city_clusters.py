# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.algorithm.math import top_items
from tag.exceptions import NothingException

"""
  Obj: {
    u'北京' : 4.2,
    u'天安门': 2.1,
    u'南京' : 1.2
  }
  @return {
    u'北京': {
      'score': 6.3,
      'slug': 'bei-jing-bei-jing-di-qu-china',
    }
  }

"""

class BaseCityClusters(object):
  def city_clusters(self, tags, top_n=1):
    if not tags:
      raise NothingException("On City_clusters Mixin")

    d = {}
    for name, weight in tags:
      cities = self.get_tag_cities(name, weight)
      for city in cities:
        for name in city:
          if name not in d:
            d.update(city)
          else:
            d[name]['score'] += city[name]['score']

    def cmp(a, b):
      return int(d[a]['score'] - d[b]['score'])

    top_cities = top_items(top_n, d, cmp)
    return top_cities

  def get_tag_cities(self, name, weight):
    raise NotImplemented

