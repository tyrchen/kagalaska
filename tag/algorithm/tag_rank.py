# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from math import top_items, merge_dicts
from mixins.filter_tags import ThresholdFilter
from mixins.city_clusters import BaseCityClusters
from mixins.seg_content import BaseSegContent
from tag.exceptions import NothingException


import logging

logger = logging.getLogger(__file__)

class TagRank(ThresholdFilter, BaseCityClusters, BaseSegContent):
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
              TF_IDF=True):
    self.objs = objs
    self.imagine = imagine
    self.tag_manager = tag_manager
    self.wordseg = wordseg
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
    return self.wordseg.parse(content, weight, TF_IDF)

  def rank(self):
    tags = {}
    for obj in self.objs :
      content = obj.get('content', '')
      weight = obj.get('weight', 0.5)
      d = self.seg_content(content=content, weight=weight,
                           TF_IDF=self.TF_IDF, imagine=self.imagine)
      merge_dicts(tags, d)

    try:
      # 将分词出来的Tag跟军TF_IDF模型过滤
      success, fail = self.filter_tags(tags)
      # 根据结果获取city的聚类
      top_cities = self.city_clusters(success.items())

    except NothingException:
      return {}
    except Exception, e:
      logger.info(e)
      return {}

    success, fail = self.format_tags(success, fail,
      [top_cities[city]['slug'] for city in top_cities])

    return {
      'show': success,
      'hide': fail,
      'cities': top_cities
    }

  def format_tags(self, success, fail, city_slugs=[]):
    return self.tag_manager.format_tags(success, fail, city_slugs)

  def get_tag_cities(self, name, weight):
    return self.tag_manager.tag_cities(name, weight)
