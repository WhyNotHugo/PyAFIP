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
from utils import BaseRequest
from suds.client import Client

import email
import random




class AuthenticationRequest(BaseRequest):

    TOKEN_XPATH = "/loginTicketResponse/credentials/token"
    SIGN_XPATH = "/loginTicketResponse/credentials/sign"

    def __init__(self, endpoints, key_file, crt_file, service):
        self.endpoints = endpoints

        random.seed(datetime.now())
        now = datetime.now()  # up to 24h old
        tomorrow = now + timedelta(hours=10)  # up to 24h in the future

        request_xml = (
            E.loginTicketRequest(
                {'version': '1.0'},
                E.header(
                    E.uniqueId(str(random.randint(0, 4294967295))),
                    E.generationTime(self.formatdate(now)),
                    E.expirationTime(self.formatdate(tomorrow)),
                ),
                E.service(service)
            )
        )
        self.request_xml = etree.tostring(request_xml, pretty_print=True)
        self.__sign(key_file, crt_file)

    def __sign(self, key_file, crt_file):
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

    def authenticate(self):
        client = Client(self.endpoints.WSAA)
        response_xml = client.service.loginCms(self.signed_request)

        response = etree.fromstring(response_xml.encode('utf-8'))
        self.token = response.xpath(self.TOKEN_XPATH)[0].text
        self.sign = response.xpath(self.SIGN_XPATH)[0].text

        return self.token, self.sign

if __name__ == "__main__":
    from endpoints import Testing
    request = AuthenticationRequest(Testing(), "hyperion.key",
                                        "hyperion.crt", "wsfe")
    token, sign = request.authenticate()

    print("token: {}\n\nsign: {}".format(token, sign))
