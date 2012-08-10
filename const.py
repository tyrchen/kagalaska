# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
import os

PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

# DATA PATH
WORDS_PATH = os.path.join(PROJECT_HOME, 'data', 'words.dic')
CHARS_PATH = os.path.join(PROJECT_HOME, 'data', 'chars.dic')
RELATIONS_PATH = os.path.join(PROJECT_HOME, 'data', 'relations')

# LOGGING
LOG_FILE = os.path.join(PROJECT_HOME, 'logs', 'kagalaska.log')
LOG_LEVEL = 'DEBUG'
LOG_FORMATTER = '%(asctime)s %(levelname)s %(message)s'

#UNIX_DOMAIN
WORDSEG_UNIX_DOMAIN = os.path.join(PROJECT_HOME, 'wordseg_unix_domain')
RELATIONS_UNIX_DOMAIN = os.path.join(PROJECT_HOME, 'relations_unix_domain')

#MONGO_DB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'kagalaska'
