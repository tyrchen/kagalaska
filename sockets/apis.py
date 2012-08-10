# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from sockets.handles import WordSeg, TagRelation

class API(object):
  def parse_words(self, words):
    handle = WordSeg()
    return handle.handle(words)

  def traverse(self, word):
    handle = TagRelation()
    return handle.handle(word)
