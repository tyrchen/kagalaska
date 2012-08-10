# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from services.wordseg import start as wordseg

patterns = {
  'wordseg': wordseg,
}
help = "args list: %r" %patterns.keys()

if __name__ == '__main__':
  import sys
  if len(sys.argv) < 2:
    print(u'需要参数')
    print(help)
    exit(1)

  args = sys.argv[1]

  if args not in patterns:
    print(u'参数不合法')
    print("args list: %r" %patterns.keys())
    exit(1)

  func = patterns[args]
  func()


  