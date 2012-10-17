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
      黄金海岸及贝尔港 　　
      有人说，如果世界上有一个吸引男人眼球的天堂，那一定不是泰国，不是古巴，而是巴塞罗那。
      在这个南欧度假胜地，挤满比基尼女郎的海滩是最让人留恋的地方，海滩上的热力人群是男人们最洗眼的宝贝。
      加泰罗尼亚的姑娘似乎天生就具有了所有女性美丽的必备要素：性感的身材、健康的肤色、金色的披肩长发、艳美的脸庞……更重要的一点是，
      她们拥有加泰罗尼亚民族特有的热情奔放，她们的美是一种洋溢着活力和快乐的美。我躺在金黄色的、软绵绵的、细细的、温暖的沙滩上，手里拿着饮料，
      静静的欣赏着眼前的一切，呼吸着新鲜的略带咸味的空气。白浪夹在金黄色和蓝色之间，让我不由得想起了家乡，那个美丽的海滨城市。抬眼望去，无尽的、
      广袤的、壮丽的海景，由近到远--金黄色的沙滩、白色的波浪，绿色的海水、深蓝色的海洋，心潮随着海浪起伏，视线随着海色展开，夕阳慷慨地抚摩着这片景色
      ，温暖的、湿润的海风吹在脸上，让人久久地不忍离去。 　　
      顺着哥伦布手指大海的青铜像，我来到了当年哥伦布远航出海口。这里现在是巴塞罗那港一个深水码头。
      密密麻麻的私人游艇让我艳羡不已，湛蓝的海水里停泊着一艘哥伦布出海时乘用的“拉尼亚”号帆船复制品，
      供游人参观。在吹着浪漫海风的海上Ramble del Mar浮桥畔，波浪般的曲线如相框般勾勒出巴塞罗那最浪漫的景象。
      长长的海岸线铺着一条别具一格的彩色石板人行路，与惹人心醉的蓝色海洋仅隔一条十几米宽浪漫迷人的金色沙滩。
      每隔一段路都有仅供情侣两人面向大海的石头座椅，凸现了巴塞罗那人激情之外的柔情似水。
      道路两旁种植着高大挺拔的棕榈树，翠绿的阔叶随海风摇曳，仿佛向行人发出种种神秘的信息。
      我找到一处木椅，凭海临风。
      近处，停靠海港的船只密集，远方，昏暗的天际和大海融成一片。这边欣赏白浪拍岸的蓝色海洋
      ，那边观瞻芳草延绵的绿色城市，美丽和谐清秀淡雅，让人心境开朗其乐无穷。
    """,
    'weight': 1,
  },{
    'content': '嘿嘿',
    'weight': 3,
  }]
  seg_ref = BaseSeg()
  tag_service_ref = TagService()
  rank = LazyRank(contents=contents, seg_ref=seg_ref, tag_service_ref=tag_service_ref)
  return rank.rank()