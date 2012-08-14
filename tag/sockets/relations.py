# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.models import TagManager

import logging
import json

logger = logging.getLogger(__name__)

RELATIONS_UNIX_DOMAIN = settings.RELATIONS_UNIX_DOMAIN

class RelationProtocol(protocol.Protocol):
  def dataReceived(self, data):
    results = self.factory.traverse(data)
    self.transport.write(results)

class RelationFactory(protocol.Factory):
  protocol = RelationProtocol

  def __init__(self, service):
    self.service = service

  def traverse(self, data):
    json_data =json.loads(data.decode('utf-8'))

    words = json_data['words']
    return json.dumps(self.service.traverse(words)).encode('utf-8')

def run():
  service = TagManager()

  print("Start relation Service")
  reactor.listenUNIX(RELATIONS_UNIX_DOMAIN, RelationFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
