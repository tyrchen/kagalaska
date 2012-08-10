# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from log import get_logger

import datetime

logger = get_logger()

def log_time(func):
  def wrapper(*args, **kwargs):
    begin = datetime.datetime.now()
    func(*args, **kwargs)
    end = datetime.datetime.now()

    timedelta = end - begin
    logger.info("func %s processed in %f" %(func.__name__, float(timedelta.total_seconds())))

    return func
  return wrapper

def test_n_time(n=100):
  def wrap(func):
    def wrapper(*args, **kwargs):
      begin = datetime.datetime.now()
      for i in range(n):
        res = func(*args, **kwargs)
      end = datetime.datetime.now()

      timedelta = end - begin
      logger.info("func %s processed %d times in %f" %(func.__name__, n, float(timedelta.total_seconds())))
      logger.info("func %s processed one time in %f" %(func.__name__, float(timedelta.total_seconds()/n)))
      return res
    return wrapper
  return wrap