# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import mmseg as _mmseg
from settings import WORDS_PATH, CHARS_PATH
from log import get_logger
from utils import to_str, to_unicode

logger = get_logger()

class Seg(object):
  '''
  Seg Words depends on different dic libraries
  '''

  def __init__(self, words_path=WORDS_PATH, chars_path=CHARS_PATH):
    self.seg = _mmseg
    self.seg.Dictionary.dictionaries = (
      ('chars', chars_path),
      ('words', words_path),
    )
    self.seg.dict_load_defaults()

  def seg_txt(self, words):
    if type(words) is str:
      algor = self.seg.Algorithm(words)
      for tok in algor:
        yield tok.text
    else:
      yield ""

class BaseSeg(object):
  def __init__(self, words_path=WORDS_PATH, chars_path=CHARS_PATH):
    self.seg = Seg(words_path, chars_path)
    self.words_path = words_path if words_path else WORDS_PATH
    self.keywords = {}
    self._load()

  def _load(self):
    file = open(self.words_path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines:
      line = to_unicode(line)
      try:
        tokens = line.split(' ')[1].strip()
      except Exception, err:
        logger.debug(err)
        continue

      self.add_keyword(tokens)

  def is_keyword(self, word):
    return self.keywords.has_key(word)

  def add_keyword(self, word):
    self.keywords.update({word: True})

  def parse(self, words):
    if not isinstance(words, basestring):
      return []

    results = []

    words = to_str(words)
    for token in self.seg.seg_txt(words):
      token = token.decode('utf-8')
      if self.is_keyword(token):
        results.append(token)

    d = {}
    for r in results:
      if r in d:
        d[r] += 1
      else:
        d[r] = 1

    return d.items()

