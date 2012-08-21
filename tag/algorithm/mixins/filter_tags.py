# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from tag.exceptions import NothingException

"""
  Tags like {
    u'北京': 4.1,
    u'天安门': 2.0,
  }
  @return {
    'show': {
      u'北京': 4.1
    }
    'hide': {
      u'天安门': 2.0
    }
  }
"""

THRESHOLD = 0.06

class ThresholdFilter(object):
  def filter_tags(self, tags, threshold=THRESHOLD):
    if not tags:
      raise NothingException

    total = 0
    for name in tags:
      total += tags[name]

    success = {}
    fail = {}
    for tag in tags:
      if tags[tag]/total > threshold:
        success.update({tag: tags[tag]})
      else:
        fail.update({tag: tags[tag]})

    return success, fail

  