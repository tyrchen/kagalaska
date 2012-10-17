# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management import BaseCommand
from shadow.utils.migration import BaseInput
from tag.models import Place, Normal, Tag

class Command(BaseCommand):
  place_path = 'places.json'
  normal_path = 'normals.json'
  tag_path = 'tags.json'

  def handle(self, *args, **options):
    print("导入地点")
    self._do_place()
    print("导入普通标签")
    self._do_normal()
    print("导入标签")
    self._do_tag()

  def _do_place(self):
    b = BaseInput(self.place_path)
    print("删除所有地点")
    Place.delete_all()
    def callback(info):
      class_name = info.pop('proxy', 'PLACE')
      info.update({'class': class_name})
      place = Place(**info)
      place.save()
      print(info.get('slug', ''))
    b.input(callback)

  def _do_normal(self):
    b = BaseInput(self.normal_path)
    print("删除所有普通标签")
    Normal.delete_all()
    def callback(info):
      normal = Normal(**info)
      normal.save()
      print(info.get('slug', ''))
    b.input(callback)

  def _do_tag(self):
    b = BaseInput(self.tag_path)
    print("删除所有标签")
    Tag.delete_all()
    def callback(info):
      items = info.pop('items', [])
      items = items or []
      info.update({'items': items})
      tag = Tag(**info)
      tag.save()
      print(info.get('name', ''))
    b.input(callback)