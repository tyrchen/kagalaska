# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management.base import BaseCommand
from tag import run_tag_rank
from tag import run_relations

patterns = {
  'wordseg': run_tag_rank,
  'relations': run_relations
}
help = "args list: %r" %patterns.keys()

class Command(BaseCommand):

  def handle(self, *args, **options):
    if len(args) < 1:
      print(u'需要参数')
      print(help)
      exit(1)

    args = args[0]

    if args not in patterns:
      print(u'参数不合法')
      print("args list: %r" %patterns.keys())
      exit(1)

    func = patterns[args]
    func()
