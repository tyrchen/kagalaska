# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import json

class DispatchMixin(object):
  def dispatch(self, str_stream, item=None):
    json_data = json.loads(str_stream.decode('utf-8'))
    func_name = json_data.pop('func_name', '')
    if not item:
      func = getattr(self, func_name, None)
    else:
      func = getattr(item, func_name, None)

    if not func:
      return {'success': False}
    else:
      try:
        return func(**json_data) or {'success': False }
      except Exception:
        return {'success': False}

class ModifyMixin(object):
  def update(self, **kwargs):
    raise NotImplemented

  def add(self, **kwargs):
    raise NotImplemented

  def remove(self, **kwargs):
    raise NotImplemented

  def get(self, **kwargs):
    raise NotImplemented