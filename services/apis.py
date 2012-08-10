# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from services.handles import WordSeg, Graphical

class API(object):
  def parse_words(self, words):
    handle = WordSeg()
    return handle.handle(words)

  def traverse(self, word):
    handle = Graphical()
    return handle.handle(word)
