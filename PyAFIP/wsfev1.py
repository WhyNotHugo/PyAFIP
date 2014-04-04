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


class Invoice:

    def __init__(self, invoice_type, amount, sales_point):
        self.amount = amount
        self.invoice_type = invoice_type
        self.sales_point = sales_point


class InvoiceLine:

    def __init__(self, concept, document_type, document_number, from_invoice,
                 to_invoice, date, total, service_from_date, service_to_date,
                 expiration_date, net_untaxed=0, net_taxed=None,
                 exempt_amount=0, tax_amount=0, vat_amount=0,
                 currency="PES", currency_quote="1.0000"):
        self.concept = concept
        self.document_type = document_type
        self.document_number = document_number
        self.from_invoice = from_invoice
        self.to_invoice = to_invoice
        self.date = date
        self.total = total
        self.net_untaxed = net_untaxed
        self.net_taxed = net_taxed or total
        self.exempt_amount = exempt_amount
        self.tax_amount = tax_amount
        self.vat_amount = vat_amount
        self.service_from_date = service_from_date
        self.service_to_date = service_to_date
        self.expiration_date = expiration_date
        self.currency = currency
        self.currency_quote = currency_quote


class ElectronicInvoiceService:

    def __init__(self, endpoints, token, sign, cuit):
        self.endpoints = endpoints
        self.client = Client(endpoints.WSFEV1)

        self.auth = self.client.factory.create('FEAuthRequest')
        self.auth.Token = token
        self.auth.Sign = sign
        self.auth.Cuit = cuit

    def last_authorized_id(self, punto_venta, tipo_comprobante):
        response_xml = self.client.service. \
            FECompUltimoAutorizado(self.auth, punto_venta, tipo_comprobante)
        return response_xml.CbteNro

    def authorize_invoice(self, invoice, *invoice_lines):
        req = self.client.factory.create('FECAERequest')

        # req.FeCabReq = self.client.factory.create('FECabRequest')
        req.FeCabReq.CantReg = invoice.amount
        req.FeCabReq.PtoVta = invoice.sales_point
        req.FeCabReq.CbteTipo = invoice.invoice_type

        for line in invoice_lines:
            line_req = self.client.factory.create('FECAEDetRequest')
            line_req.Concepto = line.concept
            line_req.DocTipo = line.document_type
            line_req.DocNro = line.document_number
            line_req.CbteDesde = line.from_invoice
            line_req.CbteHasta = line.to_invoice
            line_req.CbteFch = line.date
            line_req.ImpTotal = line.total
            line_req.ImpTotConc = line.net_untaxed
            line_req.ImpNeto = line.net_taxed
            line_req.ImpOpEx = line.exempt_amount
            line_req.ImpTrib = line.tax_amount
            line_req.ImpIVA = line.vat_amount
            line_req.FchServDesde = line.service_from_date
            line_req.FchServHasta = line.expiration_date
            line_req.FchVtoPago = line.expiration_date
            line_req.MonId = line.currency,
            line_req.MonCotiz = line.currency_quote

            req.FeDetReq.FECAEDetRequest.append(line_req)

        response_xml = self.client.service.FECAESolicitar(self.auth, req)

        # TODO: parse this a bit
        return response_xml
