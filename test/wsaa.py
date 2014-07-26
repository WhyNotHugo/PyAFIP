#!/usr/bin/env python2

from afip.endpoints import Testing
from afip.wsaa import AuthorizationTicket

ticket = AuthorizationTicket(Testing(), "hyperion.key", "hyperion.crt", "wsfe")
ticket.login()

print(ticket.dump())
