# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

from django.conf import settings

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

def _smart_print(items, name=None):
  if name:
    print("########## %s ##########" % name)
  if isinstance(items, (list, tuple)):
    for item in items:
      _smart_print(item)
  elif isinstance(items, dict):
    for item in items.items():
      _smart_print(item)
  elif isinstance(items, (int, long, float, bool, basestring)):
    print(items)
  else:
    print(getattr(items, 'name', '') or getattr(items, 'slug', '')
      , items.__class__.__name__)

def _dummy_smart_print(items, name=None):
  pass

def rank_dict(aim_dict, top=0):
  items = aim_dict.items()

  def cmp(a, b):
    return -1 if a[1] < b[1] else 1
  sorted_items = sorted(items, cmp=cmp, reverse=True)

  if top <= 0:
    return sorted_items
  else:
    return sorted_items[:top]

def dict_from_items(aim_dict, items):
  for key, value in items:
    if key in aim_dict:
      aim_dict[key] += value
    else:
      aim_dict[key] = value
  return aim_dict

class TagFileHelper(object):
  def load_from_file(self):
    path = settings.RELATIONS_PATH
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines:
      yield self.decode(line)

  def load_relations(self):
    path = settings.TRAIN_RATE_PATH
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines:
      tokens = line.decode('utf-8').split('\t')
      yield (tokens[0].strip(), float(tokens[1].strip()))

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

smart_print = _dummy_smart_print