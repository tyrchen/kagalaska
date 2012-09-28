# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

class NotExistsException(Exception):
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return self.name

  def __str__(self):
    return self.name

class MongoDBHandleException(Exception):
  def __init__(self, handle):
    self.handle = handle

  def __repr__(self):
    return self.handle

  def __str__(self):
    return self.handle

class NothingException(Exception):
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return self.name

  def __str__(self):
    return self.name