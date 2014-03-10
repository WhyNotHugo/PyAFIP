#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Hugo Osvaldo Barrera <hugo@osvaldobarrera.com.ar>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from M2Crypto.BIO import MemoryBuffer
from M2Crypto.SMIME import SMIME
from StringIO import StringIO
from datetime import datetime, timedelta
from lxml import etree
from lxml.builder import E
from suds.client import Client

import email
import random


class AuthenticationRequest:

    PROD_WSDL = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
    TEST_WSDL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"

    TOKEN_XPATH = "/loginTicketResponse/credentials/token"
    SIGN_XPATH = "/loginTicketResponse/credentials/sign"

    def __init__(self, service):
        random.seed(datetime.now())
        now = datetime.now() # up to 24h old
        tomorrow = now + timedelta(hours=10) # up to 24h in the future

        request_xml = (
            E.loginTicketRequest(
                {'version': '1.0'},
                E.header(
                    E.uniqueId(str(random.randint(0, 4294967295))),
                    E.generationTime(now.isoformat()),
                    E.expirationTime(tomorrow.isoformat()),
                ),
                E.service(service)
            )
        )
        self.request_xml = etree.tostring(request_xml, pretty_print=True)

    def sign(self, key_file, crt_file):
        buf = MemoryBuffer(self.request_xml)

        smime = SMIME()
        smime.load_key(key_file, crt_file)

        signed_data = smime.sign(buf, 0)
        out = MemoryBuffer()
        smime.write(out, signed_data)

        mime_data = email.message_from_string(out.read())
        for part in mime_data.walk():
            if part.get_filename() == "smime.p7m":
                self.signed_request = part.get_payload(decode=False)
                return self

    def authenticate(self, url):
        client = Client(url)
        response_xml = client.service.loginCms(self.signed_request)

        response = etree.fromstring(response_xml.encode('utf-8'))
        self.token = response.xpath(self.TOKEN_XPATH)[0].text
        self.sign = response.xpath(self.SIGN_XPATH)[0].text

        return self.token, self.sign

if __name__ == "__main__":
    request = AuthenticationRequest("wsfe")
    signed_request = request.sign("hyperion.key", "hyperion.crt")
    token, sign = request.authenticate(AuthenticationRequest.PROD_WSDL)

    print("token: {}\nsign:{}".format(token, sign))
