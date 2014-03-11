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


from lxml import etree
from lxml.builder import ElementMaker
from suds.client import Client

import utils


class ElectronicInvoiceService:

    PROD_WSDL = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"
    TEST_WSDL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"

    def __init__(self, token, sign, cuit, prod):
        if prod:
            url = ElectronicInvoiceService.PROD_WSDL
        else:
            url = ElectronicInvoiceService.TEST_WSDL
        self.client = Client(url)

        self.auth = self.client.factory.create('FEAuthRequest')
        self.auth.Token = token
        self.auth.Sign = sign
        self.auth.Cuit = cuit

    ### Services

    def last_authorized_id(self, url, punto_venta, tipo_comprobante):
        response_xml = self.client.service. \
            FECompUltimoAutorizado(self.auth, punto_venta, tipo_comprobante)
        return response_xml.CbteNro

    def authorize_invoice(self, invoice, *details):
        req = self.client.factory.create('FECAERequest')

        req.FeCabReq = invoice
        for d in details:
            req.FeDetReq.FECAEDetRequest.append(d)

        response_xml = self.client.service.FECAESolicitar(self.auth,
                                                          req)
        return response_xml

    ### Factory

    def new_invoice(self, amount, sales_point, invoice_type):
        req = self.client.factory.create('FECabRequest')
        req.CantReg = 1
        req.PtoVta = 1
        req.CbteTipo = 11
        return req

    def new_invoice_line(self, concept, doc_type, doc_num, num_from, num_to,
                         date, total, service_from, service_to, expiration):
        req = self.client.factory.create('FEDetRequest')
        req.Concepto = concept
        req.DocTipo = doc_type
        req.DocNro = doc_num
        req.CbteDesde = num_from
        req.CbteHasta = num_to
        req.CbteFch = date
        req.ImpTotal = total
        req.ImpTotConc = 0
        req.ImpNeto = total
        req.ImpOpEx = 0
        req.ImpTrib = 0
        req.ImpIVA = 0
        req.FchServDesde = service_from
        req.FchServHasta = service_to
        req.FchVtoPago = expiration
        req.MonId = "PES"
        req.MonCotiz = "1.0000"
        return req
