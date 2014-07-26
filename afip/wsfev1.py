#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Hugo Osvaldo Barrera <hugo@barrera.io>
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


from suds.client import Client

from utils import AfipFormatMixin, AfipException


class Invoice:

    def __init__(self, invoice_type, amount, sales_point):
        self.amount = amount
        self.invoice_type = invoice_type
        self.sales_point = sales_point
        self.details = []

    def add_detail(self, detail):
        self.details.append(detail)


class InvoiceDetail:

    def __init__(self, concept, document_type, document_number, from_invoice,
                 to_invoice, date, total, service_from_date, service_to_date,
                 expiration_date, net_untaxed=0, net_taxed=None,
                 exempt_amount=0, tax_amount=0, currency="PES",
                 currency_quote="1.0000"):
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
        self.service_from_date = service_from_date
        self.service_to_date = service_to_date
        self.expiration_date = expiration_date
        self.currency = currency
        self.currency_quote = currency_quote

        self.vats = []

    def add_vat(self, vat):
        self.vats.append(vat)


class Vat:

    def __init__(self, type, base, amount):
        self.type = type
        self.base = base
        self.amount = amount


class InvoiceService(AfipFormatMixin):

    def __init__(self, endpoints, ticket, cuit):
        self.endpoints = endpoints
        self.client = Client(endpoints.WSFEV1)

        self.auth = self.client.factory.create('FEAuthRequest')
        self.auth.Token = ticket.token
        self.auth.Sign = ticket.sign
        self.auth.Cuit = cuit

    def last_authorized_id(self, sales_point, invoice_type):
        response_xml = self.client.service. \
            FECompUltimoAutorizado(self.auth, sales_point, invoice_type)
        return response_xml.CbteNro

    def authorize_invoice(self, invoice):
        req = self.client.factory.create('FECAERequest')

        # req.FeCabReq = self.client.factory.create('FECabRequest')
        req.FeCabReq.CantReg = invoice.amount
        req.FeCabReq.PtoVta = invoice.sales_point
        req.FeCabReq.CbteTipo = invoice.invoice_type

        for detail in invoice.details:
            detail_req = self.client.factory.create('FECAEDetRequest')
            detail_req.Concepto = detail.concept
            detail_req.DocTipo = detail.document_type
            detail_req.DocNro = detail.document_number
            detail_req.CbteDesde = detail.from_invoice
            detail_req.CbteHasta = detail.to_invoice
            detail_req.CbteFch = self.format_short_date(detail.date)
            detail_req.ImpTotal = detail.total
            detail_req.ImpTotConc = detail.net_untaxed
            detail_req.ImpNeto = detail.net_taxed
            detail_req.ImpOpEx = detail.exempt_amount
            detail_req.ImpTrib = detail.tax_amount
            detail_req.FchServDesde = self \
                .format_short_date(detail.service_from_date)
            detail_req.FchServHasta = self \
                .format_short_date(detail.service_to_date)
            detail_req.FchVtoPago = self \
                .format_short_date(detail.expiration_date)
            detail_req.MonId = detail.currency
            detail_req.MonCotiz = detail.currency_quote

            detail.vat_amount = 0
            for vat in detail.vats:
                vat_req = self.client.factory.create('AlicIva')
                vat_req.Id = vat.type
                vat_req.BaseImp = vat.base
                vat_req.Importe = vat.amount
                detail.vat_amount += vat.amount
                detail_req.Iva.AlicIva.append(vat_req)
            detail_req.ImpIVA = detail.vat_amount

            req.FeDetReq.FECAEDetRequest.append(detail_req)

        response_xml = self.client.service.FECAESolicitar(self.auth, req)

        cae_data = response_xml.FeDetResp.FECAEDetResponse[0]
        if cae_data.Resultado != "A" and hasattr(response_xml, "Errors"):
            raise AfipException(response_xml.Errors.Err[0])
        elif cae_data.Resultado != "A":
            raise AfipException(cae_data.Observaciones.Obs[0])

        invoice.cae = cae_data.CAE
        invoice.cae_expiration = cae_data.CAEFchVto
