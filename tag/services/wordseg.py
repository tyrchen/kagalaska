# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import mmseg as _mmseg
from django.conf import settings
from tag.models import Tag
from tag.utils import to_str

import logging

logger = logging.getLogger()

WORDS_PATH = settings.TAG_TO_FILE_PATH
CHARS_PATH = settings.CHARS_PATH
RATE_PATH = settings.WORDS_RATE_PATH

class Seg(object):
  """
  Seg Words depends on different dic libraries
  """

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

    raise StopIteration

class BaseSeg(object):
  def __init__(self, words_path=WORDS_PATH, chars_path=CHARS_PATH):
    print("写最新字典文件")
    path = Tag.cls_to_file(words_path)
    print("分词载入字典文件")
    self.seg = Seg(path, chars_path)
    print("分词载入完毕")

    self.words_path = words_path if words_path else WORDS_PATH
    self.keywords = {}
    print("载入权重表")
    self._load()
    print("载入完毕")

  def _load(self):
    for tag in Tag.objects():
      name = tag.name
      score = getattr(tag, 'score', settings.NEW_WORD_DEFAULT_VALUE)
      self.add_keyword(name.strip(), score)

  def add_word(self, name, score=settings.NEW_WORD_DEFAULT_VALUE):
    self.add_keyword(name.strip(), float(score))
    self.seg.seg.Dictionary.add(name)

  def is_keyword(self, word):
    return self.keywords.has_key(word)

  def add_keyword(self, word, score=settings.NEW_WORD_DEFAULT_VALUE):
    self.keywords.update({word: score})

  def parse(self, words, weight=1, TF_IDF=True):
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
        d[r] += weight * self.keywords.get(r, 1) if TF_IDF else weight
      else:
        d[r] = weight * self.keywords.get(r, 1) if TF_IDF else weight

    return d
