# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management import BaseCommand
from tag.models import Place, Normal
from django.conf import settings

import os

BASE = settings.DATA_PATH
class Command(BaseCommand):
  args = "<<<place> | <normal>>>"

  def handle(self, *args, **options):
    arg = args[0]
    handler = getattr(self, 'do_%s' % arg)
    handler()

  def do_place(self):
    path = os.path.join(BASE, 'output_place.csv')
    file = open(path, 'w')
    for p in Place.objects():
      slug = getattr(p, 'slug', '')
      if not slug:
        continue

      name_en = getattr(p, 'name_en', '')
      name_zh = getattr(p, 'name_zh', '')
      centroid = getattr(p, 'centroid', [0.0, 0.0])
      lng, lat = centroid
      place_parent = getattr(p, 'place_parent', '')
      proxy = getattr(p, 'class', 'PLACE')
      info = '%s\t%s\t%s\t%.4f\t%.4f\t%s\t%s\n' % (slug, name_zh, name_en, lat, lng, place_parent, proxy)
      print(slug)
      file.write(info.encode('utf-8'))
    file.close()

  def do_normal(self):
    path = os.path.join(BASE, 'output_normal.csv')
    file = open(path, 'w')
    for n in Normal.objects():
      name = getattr(n, 'slug', '')
      if not name:
        return

      score = getattr(n, 'score', settings.NEW_WORD_DEFAULT_VALUE)
      info = '%s\t%f\n' % (name, score)
      print(name)
      file.write(info.encode('utf-8'))
    file.close()