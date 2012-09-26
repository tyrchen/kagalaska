# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management import BaseCommand
from django.conf import settings

import os
from tag.models import Tag

HOME = settings.DATA_PATH
DEFAULT_PATH = os.path.join(HOME, 'tags.dic')
class Command(BaseCommand):
  help = '将Tag内容导出'

  def handle(self, *args, **options):
    if args:
      path = args[0]
    else:
      path = DEFAULT_PATH

    tags = Tag.objects()
    first_line = '名字\t权重\t父标签\t等同于\t对应的元素\n'

    file = open(path, 'w')
    file.write(first_line.encode('utf-8'))
    for tag in tags:
      line = self.do_tag(tag)
      file.write(line)
    file.close()

  def do_tag(self, tag):
    name = getattr(tag, 'name', '')
    score = str(getattr(tag, 'score', 10.0))
    parents_list = getattr(tag, 'parents', [])
    equal_to = getattr(tag, 'equal_to', '')
    items_list = getattr(tag, 'items', [])

    parents = ','.join(parents_list)
    items = [item.get('slug', '') + '__' + item.get('class', 'NORMAL') for item in items_list]

    data = '%s\t%s\t%s\t%s\t%s\n' % (name, score, parents, equal_to, ','.join(items))
    return data.encode('utf-8')