# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from const import RELATIONS_UNIX_DOMAIN
from twisted.internet import protocol, reactor
from log import get_logger
from services.manager import TagManager

import json
logger = get_logger()

class RelationProtocol(protocol.Protocol):
  def dataReceived(self, data):
    results = self.factory.traverse(data)
    self.transport.write(results)

class RelationFactory(protocol.Factory):
  protocol = RelationProtocol

  def __init__(self, service):
    self.service = service

  def traverse(self, words):
    words = words.decode('utf-8')
    return json.dumps(self.service.traverse(words)).encode('utf-8')

def run():
  service = TagManager()

  print("Start relation Service")
  reactor.listenUNIX(RELATIONS_UNIX_DOMAIN, RelationFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
