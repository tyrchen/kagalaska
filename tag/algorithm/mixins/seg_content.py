# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import copy
from tag.algorithm.math import merge_dicts

DEFAUTL_IMAGEINE_WEIGHT = 0.3

class BaseSegContent(object):
  def seg_content(self, content='', weight=0.5, TF_IDF=True, imagine=False):
    tags_dict = self.parse(content=content, weight=weight, TF_IDF=TF_IDF)
    if not imagine:
      return tags_dict

    results = copy.deepcopy(tags_dict)

    for key in tags_dict:
      data = self.traverse(key)

      if not data.has_key(key):
        continue

      parents = data.pop(key)
      merge_dicts(results, parents, weight=DEFAUTL_IMAGEINE_WEIGHT)

      for remain in data:
        merge_dicts(results, data[remain],
                    DEFAUTL_IMAGEINE_WEIGHT*DEFAUTL_IMAGEINE_WEIGHT)

    return results

  def parse(self, content, weight, TF_IDF=True):
    raise NotImplemented

  def traverse(self, tag):
    raise  NotImplemented