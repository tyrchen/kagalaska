# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import copy

list_nothing = lambda *args, **kwargs: []

DEFAUTL_IMAGEINE_WEIGHT = 0.3


def merge_dicts(to_obj, from_obj, weight=1):
  """
  merge list or dict to a dict
  {'a': 1} {'a': 2, 'b': 1}
  ===> {'a': 3, 'b': 1}
  """
  if isinstance(from_obj, list):
    from_obj = dict.fromkeys(from_obj, weight)

  assert isinstance(from_obj, dict)
  assert isinstance(to_obj, dict)
  for key in from_obj:
    if to_obj.has_key(key):
      to_obj[key] += from_obj[key]
    else:
      to_obj[key] = from_obj[key]

  return to_obj

class TagRank(object):
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
    results = {}

    for obj in self.objs:
      d = self.rank_obj(obj)
      merge_dicts(results, d)

    threshold = 0.06
    total = 0
    for value in results.values():
      total += value

    show = {}
    hide = {}
    for key in results:
      if results[key]/total >= threshold:
        show[key] = results[key]
      else:
        hide[key] = results[key]

    cities = self.tag_manager.city_clusters(show.items())
    return {
      'show': show,
      'hide': hide,
      'cities': cities
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
        merge_dicts(results, data[remain], DEFAUTL_IMAGEINE_WEIGHT*DEFAUTL_IMAGEINE_WEIGHT)

    return results
