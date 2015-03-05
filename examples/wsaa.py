#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from afip.endpoints import Testing
from afip.wsaa import AuthorizationTicket

# The key and certificate are the only values you should need to change.
ticket = AuthorizationTicket(Testing(), "hyperion.key", "hyperion.crt", "wsfe")
ticket.login()

print(ticket.dump())
