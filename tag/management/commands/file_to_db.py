# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.core.management.base import BaseCommand
from tag.utils.loaders import TagRelationLoader, TagScoreLoader, PlaceInfoLoader, NormalTagLoader

class Command(BaseCommand):
  args = '<"load_relations" | "load_score" | "load_place" | "load_normal" | "do_all" <OPTIONS>>'
  help = """
    Load data from file.
    Notice, if you haven't init db. You should do_all.
    Ensure, data file is in your settings or default paths.
    Args: load_relations, load_score, load_place, do_all
  """
  option_list = BaseCommand.option_list

  def handle(self, *args, **options):
    if len(args) != 1:
      print(self.help)
      exit(-1)

    item = args[0]

    if item == 'load_relations':
      self.load_relations()
    elif item == 'load_score':
      self.load_score()
    elif item == 'load_place':
      self.load_place_info()
    elif item == 'load_normal':
      self.load_normal_tag()
    elif item == 'do_all':
      self.load_place_info()
      self.load_normal_tag()
      self.load_relations()
      self.load_score()
    else:
      print(self.help)
      exit(-1)

  def load_relations(self):
    TagRelationLoader().load()

  def load_score(self):
    TagScoreLoader().load()

  def load_place_info(self):
    PlaceInfoLoader().load(to_db=True, to_tag=True)

  def load_normal_tag(self):
    NormalTagLoader().load()