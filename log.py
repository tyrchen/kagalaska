# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from const import LOG_FILE, LOG_LEVEL, LOG_FORMATTER

def get_logger():
  import logging

  logger = logging.getLogger()
  handle = logging.FileHandler(LOG_FILE)

  formatter = logging.Formatter(LOG_FORMATTER)
  handle.setFormatter(formatter)

  logger.addHandler(handle)
  logger.setLevel(LOG_LEVEL)

  return logger