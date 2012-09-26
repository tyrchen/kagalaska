# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

class WorkerMixin(object):
  def start(self):
    raise NotImplemented

  def stop(self):
    raise NotImplemented

  def restart(self):
    self.stop()
    self.start()