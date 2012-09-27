# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings
from twisted.internet import protocol, reactor
from tag.managers import TagRankService
from tag.sockets.mixins import DispatchMixin

import logging
import json

logger = logging.getLogger(__name__)

RELATIONS_UNIX_DOMAIN = settings.RELATIONS_UNIX_DOMAIN

class RelationProtocol(protocol.Protocol, DispatchMixin):
  def dataReceived(self, data):
    response = self.dispatch(data, self.factory)
    self.transport.write(response)

class RelationFactory(protocol.Factory):
  protocol = RelationProtocol

  def __init__(self, service):
    self.service = service

  def traverse(self, **json_data):
    words = json_data['words']
    return json.dumps(self.service.traverse(words)).encode('utf-8')

def run():
  service = TagRankService()

  print("Start relation Service")
  reactor.listenUNIX(RELATIONS_UNIX_DOMAIN, RelationFactory(service))
  try:
    reactor.run()
  except Exception, err:
    logger.info(err)
