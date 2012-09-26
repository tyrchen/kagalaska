# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import random

class ProxyServer(object):
  def __init__(self, name):
    self.name = name
    self.workers = {}

  def add_worker(self, worker):
    self.workers.update(
      {worker.name: worker}
    )

  def restart_worker(self, worker_name):
    worker = self.workers.get(worker_name, None)
    if worker:
      worker.restart()

  def __random_worker(self):
    if not self.workers:
      return None

    return random.choice(self.workers.values())

  def dispatch(self, func_name, params, work_name=''):
    if work_name in self.workers:
      worker = self.workers[work_name]
    else:
      worker = self.__random_worker()

    if not worker:
      raise ProxyException("No available workers for proxy server %s" %self.name)

    try:
      func = getattr(worker, func_name)
      return func(params)
    except Exception:
      raise ProxyException("No func named %s" % func_name)

class ProxyException(Exception):
  def __init__(self, name):
    super(Exception, self).__init__()
    self.name = name
  