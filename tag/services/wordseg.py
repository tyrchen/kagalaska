# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import mmseg as _mmseg
from django.conf import settings
from tag.models import Tag
from tag.utils import to_str
from shadow.contribs.mmseg import Segment
from shadow.utils.profilings import log_n_time

import logging
import re
from tag.utils.util import smart_print

logger = logging.getLogger()

WORDS_PATH = settings.TAG_TO_FILE_PATH
CHARS_PATH = settings.CHARS_PATH
RATE_PATH = settings.WORDS_RATE_PATH
ENGLISH_SEGMENT_SEPARATOR = 'ZZZ'

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

class PythonSeg(object):
  def __init__(self):
    self.seg = Segment()
    self.keywords = {}
    self.load()

  def load(self):
    for tag in Tag.objects():
      score = getattr(tag, 'score', settings.NEW_WORD_DEFAULT_VALUE)
      self.add_word(tag.name, score)

  def add_word(self, name, score=settings.NEW_WORD_DEFAULT_VALUE):
    self.seg.add(name.strip())
    self.add_keyword(name.strip(), score)

  def add_keyword(self, word, score=settings.NEW_WORD_DEFAULT_VALUE):
    self.keywords.update({word.strip(): score})

  def is_keyword(self, word):
    return self.keywords.has_key(word)

  def parse(self, words, weight=1, TF_IDF=True):
    if not isinstance(words, basestring):
      return []

    results = []

    for token in self.seg.seg_text(words):
      if len(token) > 1:
        results.append(token)

    d = {}
    for r in results:
      if r in d:
        d[r] += weight * self.keywords.get(r, 1) if TF_IDF else weight
      else:
        d[r] = weight * self.keywords.get(r, 1) if TF_IDF else weight

    return d


class BaseSeg(object):
  def __init__(self, words_path=WORDS_PATH, chars_path=CHARS_PATH):
    path = Tag.cls_to_file(words_path)
    self.seg = Seg(path, chars_path)

    self.words_path = words_path if words_path else WORDS_PATH
    self.keywords = {}
    self._load()

  def _load(self):
    for tag in Tag.objects():
      score = getattr(tag, 'score', settings.NEW_WORD_DEFAULT_VALUE)
      self.add_word(tag.name, score)

  def add_word(self, name, score=settings.NEW_WORD_DEFAULT_VALUE):
    keyword = re.sub('\s', ENGLISH_SEGMENT_SEPARATOR, name.strip())
    self.add_keyword(name.strip(), float(score))
    self.seg.seg.Dictionary.add(keyword)

  def is_keyword(self, word):
    return self.keywords.has_key(word)

  def add_keyword(self, word, score=settings.NEW_WORD_DEFAULT_VALUE):
    self.keywords.update({word: score})

  def parse(self, words, weight=1, TF_IDF=True):
    if not isinstance(words, basestring):
      return []

    results = []

    smart_print(words)
    words = re.sub('\s', ENGLISH_SEGMENT_SEPARATOR, words)
    smart_print(words)
    words = to_str(words)
    for token in self.seg.seg_txt(words):
      token = token.decode('utf-8')
      token = re.sub('Z+', ' ', token).strip()
      if self.is_keyword(token):
        results.append(token)

    d = {}
    for r in results:
      if r in d:
        d[r] += weight * self.keywords.get(r, 1) if TF_IDF else weight
      else:
        d[r] = weight * self.keywords.get(r, 1) if TF_IDF else weight

    return d

@log_n_time(1000)
def python_seg(p):
  content = u"""
  PREPAID TAXI去了NDSL。没想到刚到印度，又被骗了，不过对德里早有心理准备，
  所以对我们没造成太大影响。事情是这样，到了NDSL，也就是新德里车站（德里一共4个大的火车站），
  刚下出租车，几个貌似工作人员的人让我们从侧面有个可以到站台的楼梯上去。上去前还说要检查我们的车票。
  看了我们车票以后，JJWW说了很多，谁也没听明白。于是带我们到了对面一家办公室，看起来还有模有样，写着什么铁路的代理。
  然后那个人开始胡编乱造了，说在印度，网上订的火车票必须提前24小时reconfirm，说我们没有reconfirm，现在在waitlist里面了。
  其实我以前在网上定过火车票，并没有reconfirm一说，但是因为这次由于在官网没法支付，所以我是通过cleartrip支付的。
  所以我也不确定是否有reconfirm一说了。谁想到他越说越离谱，跟我们开始推荐100多美金的package的东西。我开始有些怀疑了，
  我让xujing把火车票有条款那几页拿出来给我看看。仔细看了好几遍，并没有看到reconfirm一说。我确认他是在骗我们，
  于是我跟clement和xujing说，我们走吧。我觉得他们在骗我们。我们起身准备走，骗子这下急了，说你们现在去哪里，火车站不让进，
  会把你们抓起来的（搞笑，我又不是没坐过印度火车，里面那么多人睡地上也没人理）。我说，你管我，我现在找个旅馆睡觉去不行吗？
  我们头也不回地离开了那个办公室，大概是因为去年南印的人太淳朴，回到北印的第一次，有点不适应这些骗子了。哈。
  """
  p.parse(content)

@log_n_time(1000)
def seg(b):
  content = u"""
  PREPAID TAXI去了NDSL。没想到刚到印度，又被骗了，不过对德里早有心理准备，
  所以对我们没造成太大影响。事情是这样，到了NDSL，也就是新德里车站（德里一共4个大的火车站），
  刚下出租车，几个貌似工作人员的人让我们从侧面有个可以到站台的楼梯上去。上去前还说要检查我们的车票。
  看了我们车票以后，JJWW说了很多，谁也没听明白。于是带我们到了对面一家办公室，看起来还有模有样，写着什么铁路的代理。
  然后那个人开始胡编乱造了，说在印度，网上订的火车票必须提前24小时reconfirm，说我们没有reconfirm，现在在waitlist里面了。
  其实我以前在网上定过火车票，并没有reconfirm一说，但是因为这次由于在官网没法支付，所以我是通过cleartrip支付的。
  所以我也不确定是否有reconfirm一说了。谁想到他越说越离谱，跟我们开始推荐100多美金的package的东西。我开始有些怀疑了，
  我让xujing把火车票有条款那几页拿出来给我看看。仔细看了好几遍，并没有看到reconfirm一说。我确认他是在骗我们，
  于是我跟clement和xujing说，我们走吧。我觉得他们在骗我们。我们起身准备走，骗子这下急了，说你们现在去哪里，火车站不让进，
  会把你们抓起来的（搞笑，我又不是没坐过印度火车，里面那么多人睡地上也没人理）。我说，你管我，我现在找个旅馆睡觉去不行吗？
  我们头也不回地离开了那个办公室，大概是因为去年南印的人太淳朴，回到北印的第一次，有点不适应这些骗子了。哈。
  """
  b.parse(content)

@log_n_time(1000)
def origin(s):
  content = u"""
    PREPAID TAXI去了NDSL。没想到刚到印度，又被骗了，不过对德里早有心理准备，
    所以对我们没造成太大影响。事情是这样，到了NDSL，也就是新德里车站（德里一共4个大的火车站），
    刚下出租车，几个貌似工作人员的人让我们从侧面有个可以到站台的楼梯上去。上去前还说要检查我们的车票。
    看了我们车票以后，JJWW说了很多，谁也没听明白。于是带我们到了对面一家办公室，看起来还有模有样，写着什么铁路的代理。
    然后那个人开始胡编乱造了，说在印度，网上订的火车票必须提前24小时reconfirm，说我们没有reconfirm，现在在waitlist里面了。
    其实我以前在网上定过火车票，并没有reconfirm一说，但是因为这次由于在官网没法支付，所以我是通过cleartrip支付的。
    所以我也不确定是否有reconfirm一说了。谁想到他越说越离谱，跟我们开始推荐100多美金的package的东西。我开始有些怀疑了，
    我让xujing把火车票有条款那几页拿出来给我看看。仔细看了好几遍，并没有看到reconfirm一说。我确认他是在骗我们，
    于是我跟clement和xujing说，我们走吧。我觉得他们在骗我们。我们起身准备走，骗子这下急了，说你们现在去哪里，火车站不让进，
    会把你们抓起来的（搞笑，我又不是没坐过印度火车，里面那么多人睡地上也没人理）。我说，你管我，我现在找个旅馆睡觉去不行吗？
    我们头也不回地离开了那个办公室，大概是因为去年南印的人太淳朴，回到北印的第一次，有点不适应这些骗子了。哈。
    """
  for i in s.seg_txt(content.encode('utf-8')):
    pass

def benchmark():
  p = PythonSeg()
  python_seg(p)

  b = BaseSeg()
  seg(b)

  s = Seg()
  origin(s)