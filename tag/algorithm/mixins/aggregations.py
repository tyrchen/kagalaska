# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

class AggregationMixin(object):
  def aggregation(self, *tags_list):
    tags_dict = {}
    for tags in tags_list:
      for name, score in tags.items():
        if name not in tags_dict:
          tags_dict[name] = score
        else:
          tags_dict[name] += score
    return tags_dict
