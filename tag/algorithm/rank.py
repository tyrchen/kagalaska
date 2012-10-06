# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from mixins.aggregations import AggregationMixin
from tag.service import TagService
from tag.services.wordseg import BaseSeg
from tag.utils.util import smart_print
from django.conf import settings

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

    # 将分词结果聚合
    tags_dict = self.aggregation(*tags_list)  # {'北京': 5}
    filtered_tags = self.filter(tags_dict)

    top_n_tags_list = self.ranking(filtered_tags, top=10) # 将聚合结果排名
    places, others = self.clusters(top_n_tags_list, filtered_tags, top_n=TOP_N) # 根据权重得出最权威的places和其他信息

    result = self.format(places, others)
    return result # 返回formatted的数据

def test():
  contents = [{
    'content': u"""
            做了很多的准备，到了三亚，才发现担心的太多了
        行：成都—重庆：动车；

        重庆—三亚：飞机，560元（因为是淡季，机票相对便宜，所有费用包含），从成都出发的GGMM们，建议去重庆溜达一圈，除去成都到重庆的费用，还可以省下一笔呢，我认识很多的成都出去玩的朋友都是这样的线路，顺便游游重庆，(*^__^*) 嘻嘻……

        到三亚之后你可以选择：公车、跟团的有专车接送、当然你也可以选择租车。
        一个人建议坐公车,三亚的街道和景区没有你想象或者图片拍得那么美丽，但是公交系统却是超出你想象的发达（因为三亚确实很小，到哪里都非常的近，千万不要被什么多少分钟，多少钱的交通费用吓到了）
        因为本人基本是坐公交和跟一日游团，所以着重介绍公交：从我住的市区（明珠广场）一块钱或两块钱（转乘，很方便）可以坐到很多地方：火车站、机场、第一市场、免税店等等。远点的到森林公园、蜈支洲岛、南山、亚龙湾、天涯海角等就需要坐长途公交，但是问问就能知道在哪个公交站（不需要找车站）坐车了，走走停停也就40分钟左右。
        几个人可以租车，价钱不贵，玩得更好。

        住：家庭旅馆：淡季标间在80--150左右；在三亚多如牛毛，我是淡季去的，不存在住房紧缺，要是旺季出游，提醒朋友们提前预订更好，更安心（团购里去看看，有时候价格更合适）。
                 青旅：也是不错的选择，朋友推荐的迷途和三亚雍和他们住了都说性价比高，还经常组织活动、聚餐什么的，非常有家的感觉。
                 酒店：先预订吧，绝对比你直接去便宜。三亚住宿环境最好的一个地之一就是亚龙湾的酒店区域，有一般的房间，也有海边别墅，比起森林公园的鸟巢和蜈支洲岛的住宿性价比更高。他们都有自己的私人海滩，更静谧，适合度假~~~
        吃：海鲜，第一市场去买吧（三亚估计没人不知道第一市场的），我就不具体说各类海鲜的价格了，反正多问两家再买更好。按个数收取加工费的建议买量少个大的。可以在外面加工，有些家庭旅馆和青旅是可以带回去自己加工的哦。我不想介绍哪些加工店有多好，朋友们可以自己先去店里看看是否明码标价加工费怎么算再去。
                 文昌鸡：吃了两次，还是海口那家和当地朋友一起去吃的更好吃，其实就是白水鸡蘸调料，而且鸡是相当的肥，我个人不怎么喜欢吃，尝个鲜。
                 东山羊：海口的朋友带我们吃的汤锅，确实很好吃，全天然饲养，膻味很少，巴适！
                 和乐蟹：市场上有，多问问，别上当了，蟹有很多种。
                 清补凉、抱罗粉：我每天都去第一市场欣园面包旁正宗那家吃清补凉，抱罗粉的话尝尝即可。这家店简直是驰名国内旅游市场啊！
                加积鸭：很遗憾，还没来得及吃就走了。
                热带水果：我的最爱：芒果、木瓜、火龙果、青椰，我多想全部带回来啊！

         门票：直接买票：当然最贵。
                        一日游：怕麻烦可跟当地一日游团，但要找正规的，谈好出行内容，有无车辆接送、包含哪些门票、中午就餐问题等。
                        网上订票：这次很后悔跟了一日游团，虽说便利了，但是没耍好。其实三亚真的很小，最好的办法就是在网上订票或者在一日游只买他的团票，自己坐车去，省钱也玩得好。
                        Ps：军人、学生、老人很多景点是有优惠的，跟团和买票要问清楚，别花冤枉的哦。
        行程安排：根据地图显示,这样安排景点更合理
        1、  南山、天涯海角
        2、  户外一日游；
        3、  森林公园（非2拍摄地）、亚龙湾
        4、  蜈支洲岛
        当然你的行程根据你的喜好安排，我只是站下我的，(*^__^*) 嘻嘻……

         让我来自恋一下，(*^__^*) 嘻嘻……别介意：
        第一次尝试这么艳丽的，呵呵
    """,
    'weight': 1,
  },{
    'content': '我爱三亚',
    'weight': 3,
  }]
  seg_ref = BaseSeg()
  tag_service_ref = TagService()
  rank = LazyRank(contents=contents, seg_ref=seg_ref, tag_service_ref=tag_service_ref)
  return rank.rank()