# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
list_nothing = lambda *args, **kwargs: []

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

  def __init__(self, objs, traverse_func=list_nothing, seg_func = list_nothing,
               imagine=True, imagine_weight=0.5):
    self.objs = objs
    self.imagine = imagine
    self.seg_func = seg_func
    self.traverse_func = traverse_func
    self.imagine_weight = imagine_weight

  def traverse(self, tag):
    """
    traverse a tag
    traverse(u'北京') ===> {
    u'北京': [u'中国', u'城市'],
    u'中国': [u'亚洲']
    }

    """
    return self.traverse_func(tag)

  def parse(self, content, weight):
    return self.seg_func(content, weight)

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
        
    return {
      'show': show,
      'hide': hide,
    }

  def rank_obj(self, obj):
    """
    Algorithm of rank obj.

    """
    content = obj.get('content', '')
    weight = float(obj.get('weight', 0))

    d = self.parse(content=content, weight=weight)
    if not self.imagine:
      return d

    import copy
    results = copy.deepcopy(d)

    for key in d:
      data = self.traverse(key)
      imagine_weight = self.imagine_weight

      if not data.has_key(key):
        continue

      value = d.get(key, 1)
      parents = data.pop(key)
      merge_dicts(results, parents, weight=imagine_weight)

      for remain in data:
        merge_dicts(results, data[remain], imagine_weight-0.2)

    return results
