# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from math import (top_items, filter_threshold_to_dict, merge_dicts, filter_threshold_to_list)
from mixins.filter_tags import ThresholdFilter
from tag.exceptions import NothingException

import copy
import logging

logger = logging.getLogger(__file__)

list_nothing = lambda *args, **kwargs: []

DEFAUTL_IMAGEINE_WEIGHT = 0.3
TOP_TAGS_THRESHOLD = 0.06


class TagRank(ThresholdFilter):
  """
  algorithm to rank tags
  @property
  ====> objs like : [{
        'content': u'我爱北京天安门',
        'weight': 5
        },{
        'content': u'今天去天安门看升旗了，很机动'
        'weight': 1
        }
      ]
  @return {'天安门': 6, '北京': 5}
  """

  def __init__(self, objs, tag_manager, wordseg, imagine=True,
               imagine_weight=DEFAUTL_IMAGEINE_WEIGHT, TF_IDF=True):
    self.objs = objs
    self.imagine = imagine
    self.tag_manager = tag_manager
    self.wordseg = wordseg
    self.imagine_weight = imagine_weight
    self.TF_IDF =TF_IDF

  def traverse(self, tag):
    """
    traverse a tag
    traverse(u'北京') ===> {
    u'北京': [u'中国', u'城市'],
    u'中国': [u'亚洲']
    }

    """
    return self.tag_manager.traverse(tag)

  def parse(self, content, weight, TF_IDF=True):
    return self.wordseg.parse(content, weight, self.TF_IDF)

  def rank(self):
    tags = {}

    for obj in self.objs :
      d = self.rank_obj(obj)
      merge_dicts(tags, d)

    try:
      # filter_tags
      success, fail = self.filter_tags(tags)
    except NothingException:
      return {}
    except Exception, e:
      logger.info(e)
      return {}

    cities = self.tag_manager.city_clusters(success.items())

    def cmp(a, b):
      return int(cities[a]['score'] - cities[b]['score'])
      
    top_cities = top_items(1, cities, cmp)
    success, fail = self.tag_manager.format_tags(success, fail,
      [top_cities[city]['slug'] for city in top_cities])

    return {
      'show': success,
      'hide': fail,
      'cities': top_cities
    }

  def rank_obj(self, obj):
    """
    Algorithm of rank obj.

    """
    content = obj.get('content', '')
    weight = float(obj.get('weight', 0.5))

    d = self.parse(content=content, weight=weight)
    if not self.imagine:
      return d

    results = copy.deepcopy(d)

    for key in d:
      data = self.traverse(key)
      imagine_weight = self.imagine_weight

      if not data.has_key(key):
        continue

      parents = data.pop(key)
      merge_dicts(results, parents, weight=DEFAUTL_IMAGEINE_WEIGHT)

      for remain in data:
        merge_dicts(results, data[remain],
                    DEFAUTL_IMAGEINE_WEIGHT*DEFAUTL_IMAGEINE_WEIGHT)

    return results
