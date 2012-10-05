# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management import BaseCommand
from tag import Tag
from tag.models import Normal

class Command(BaseCommand):
  help = '初始化数据库'
  args = "<<<PLACE> | <NORMAL> | <TAG> | <ALL>>>"
  file_path =  '/home/toureet/Desktop/tags_final.csv'

  def handle(self, *args, **options):
    print("Will delete the table of tags and normal tags, Y/n")
    delete = raw_input()
    if not delete == 'Y':
      return

    Tag.delete_all()
    Normal.delete_all()

    self.do_init()

  def do_init(self):
    file = open(self.file_path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines[1:]:
      info = line.decode('utf-8')[:-1]
      tag_name, score, parents_str, equal_to, items_str = info.split('\t')
      print(tag_name)
      score = 1.0
      items = []
      parents = parents_str.split(',')

      for item in items_str.split(','):
        name, class_name = item.split('__')
        if class_name == 'NORMAL':
          print("Save normal tag %s" % name)
          n = Normal(slug=name, score=score)
          n.save()
        items.append({
          'slug': name,
          'class': class_name
        })
      tag = Tag(name=tag_name, score=score, parents=parents, equal_to=equal_to,
                items=items)
      tag.save()

  def exit_with_info(self, info='参数不合法'):
    print(info)
    print(self.args)
    exit(-1)