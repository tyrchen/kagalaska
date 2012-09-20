# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.models import Place

import logging
import json

logger = logging.getLogger(__name__)
PLACEINFO_UNIX_DOMAIN = settings.PLACEINFO_UNIX_DOMAIN

class PlaceInfoProtocol(protocol.Protocol):
  def dataReceived(self, data):
    results = self.factory.get_by_slug(data)
    self.transport.write(results)

class PlaceInfoFactory(protocol.Factory):
  protocol = PlaceInfoProtocol

  def __init__(self, service):
    self.service = service

  def get_by_slug(self, data):
    json_data =json.loads(data.decode('utf-8'))

    slugs = json_data['slugs']
    items = {}
    if isinstance(slugs, list):
      for slug in slugs:
        items.update({slug: self.service.get_by_slug(slug, json_format=True)})
    else:
      items.update({slugs: self.service.get_by_slug(slugs, json_format=True)})

    return json.dumps(items).encode('utf-8')

def run():
  service = Place

  print("Start place_info Service")
  reactor.listenUNIX(PLACEINFO_UNIX_DOMAIN, PlaceInfoFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
