# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.models import Place
from mixins import DispatchMixin

import logging
import json

logger = logging.getLogger(__name__)
PLACEINFO_UNIX_DOMAIN = settings.PLACEINFO_UNIX_DOMAIN

class PlaceInfoProtocol(protocol.Protocol, DispatchMixin):
  def dataReceived(self, data):
    response = self.dispatch(data, self.factory)
    self.transport.write(json.dumps(response).encode('utf-8'))

class PlaceInfoFactory(protocol.Factory):
  protocol = PlaceInfoProtocol

  def __init__(self, service):
    self.service = service

  def get_by_slug(self, **json_data):
    slugs = json_data['slugs']
    only = json_data.get('only', Place.ONLY_MAPPING['ONLY_USEFUL'])
    items = {}
    if isinstance(slugs, list):
      for slug in slugs:
        items.update({slug: self.service.get_by_slug(slug, only=only, json_format=True)})
    else:
      items.update({slugs: self.service.get_by_slug(slugs, only=only, json_format=True)})

    return items

def run():
  service = Place

  print("Start place_info Service")
  reactor.listenUNIX(PLACEINFO_UNIX_DOMAIN, PlaceInfoFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
