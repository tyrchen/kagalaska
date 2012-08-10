# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from const import RELATIONS_PATH

def to_str(obj):
  if isinstance(obj, unicode):
    return obj.encode('utf-8')
  elif isinstance(obj, str):
    return obj
  else:
    return obj

def to_unicode(obj):
  if isinstance(obj, str):
    return obj.decode('utf-8')
  else:
    return obj

class TagFileHelper(object):
  def __init__(self, path=RELATIONS_PATH):
    self.path = path

  def load_from_file(self):
    file = open(self.path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines:
      yield self.decode(line)

  def to_file(self, name, parents):
    import codecs
    recode = self.encode(name, parents)

    file = codecs.open(self.path, mode='a', encoding='utf-8')
    file.write(recode)
    file.close()

  def decode(self, recode):
    recode = to_unicode(recode)
    name, score, parents = recode.split('\t')
    return {
      'name': name.strip(),
      'score': int(score.strip()),
      'parents': filter(None, parents.strip().split(','))
    }

  def encode(self, name, parents):
    return '%s\t%s\n' %(name, ','.join(parents))
