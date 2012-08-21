# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.exceptions import NothingException

def top_items(n, items, cmp):
  """
  将字典里的数据排名，返回前N个
  """
  if not items:
    raise NothingException("On func top items")

  keys = sorted(items, cmp=cmp, reverse=True)
  if len(items) < n:
    return items
  else:
    d = {}
    for key in keys[:n]:
      d.update({key: items[key]})
    return d

def filter_threshold_to_list(items, func, threshold=0.0):
  if not items:
    raise NothingException

  total = 0

  for item in items:
    total += func(item)

  success = []
  fail = []
  for item in items:
    if func(item)/total > threshold:
      success.append(item)
    else:
      fail.append(item)

  return success, fail

def filter_threshold_to_dict(dicts, func, threshold=0.0):
  if not dicts:
    return {}, {}

  total = 0
  for item in dicts:
    total += func(item)

  success = {}
  fail = {}
  for item in dicts:
    if func(item)/total > threshold:
      success.update({item: func(item)})
    else:
      fail.update({item: func(item)})
  return success, fail

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
