# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

def item_in(item, obj):
  assert isinstance(obj, (list, dict))
  try:
    if_in = item in obj
  except Exception:
    return False

  else:
    return if_in

def item_exists(item):
  return bool(item)