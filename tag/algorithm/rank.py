# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from mixins.aggregations import AggregationMixin
from tag.service import TagService
from tag.services.wordseg import BaseSeg
from django.conf import settings
from tag.utils.util import smart_print

FILTER_THRESHOLD = getattr(settings, 'FILTER_THRESHOLD', 0.03)
TOP_N = getattr(settings, 'TOP_N', 3)

class LazyRank(AggregationMixin):
  def __init__(self, contents, seg_ref, tag_service_ref, tf_idf=True, **kwargs):
    self.seg = seg_ref
    self.tf_idf = tf_idf
    self.contents = contents
    self.tag_service = tag_service_ref
    self.__dict__.update(kwargs)

  def parse(self, content, weight):
    """
    文本分词，单次的结果有聚合
    """
    return self.seg.parse(content, weight, self.tf_idf)

  def filter(self, tags_dict):
    """
    转换同义词并过滤掉一个字的Tag
    """
    return self.tag_service.filter(tags_dict)

  def ranking(self, tags, top=10):
    total = 0
    for _, value in tags.items():
      total += value

    top_tags_list = []
    threshold = FILTER_THRESHOLD

    for key, value in tags.items():
      # 根据阈值过滤
      if value/total > threshold:
        item = (key, value)
        top_tags_list.append(item)

    def cmp(a, b):
      return int(a[1] - b[1])

    sorted_items = sorted(top_tags_list, cmp, reverse=True)
    return sorted_items if len(sorted_items) < top else sorted_items[:top]

  def clusters(self, tags, origin, top_n=1):
    return self.tag_service.clusters(tags, origin, top_n)

  def format(self, places, others):
    return self.tag_service.format(places, others)

  def rank(self):
    tags_list = []
    for content in self.contents:
      tags = self.parse(content['content'], content.get('weight', 1))
      tags_list.append(tags) # 根据内容和权重分词  {'content': '我爱北京', 'weight': 5}
    smart_print(tags_list, "分词结果")
    # 将分词结果聚合
    tags_dict = self.aggregation(*tags_list)  # {'北京': 5}
    smart_print(tags_dict, "标签聚合")
    filtered_tags = self.filter(tags_dict)
    smart_print(filtered_tags, "标签filter")

    top_n_tags_list = self.ranking(filtered_tags, top=10) # 将聚合结果排名
    smart_print(top_n_tags_list, "排名前N")
    places, others = self.clusters(top_n_tags_list, filtered_tags, top_n=TOP_N) # 根据权重得出最权威的places和其他信息
    smart_print(places, "地点")
    smart_print(others, "其他")

    result = self.format(places, others)
    smart_print(result, "结果")
    return result # 返回formatted的数据

def test():
  contents = [{
    'content': u"""
      天安门不是我的家，天津是的
    """,
    'weight': 1,
  },{
    'content': '我爱天安门',
    'weight': 3,
  }]
  seg_ref = BaseSeg()
  tag_service_ref = TagService()
  rank = LazyRank(contents=contents, seg_ref=seg_ref, tag_service_ref=tag_service_ref)
  return rank.rank()