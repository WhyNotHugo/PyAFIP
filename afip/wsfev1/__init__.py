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

from ..utils import AfipFormatMixin, AfipException
from model import *
from suds.client import Client


class InvoiceService(AfipFormatMixin):

    def __init__(self, endpoints, ticket, cuit):
        self.endpoints = endpoints
        self.client = Client(endpoints.WSFEV1)

        self.auth = self.client.factory.create('FEAuthRequest')
        self.auth.Token = ticket.token
        self.auth.Sign = ticket.sign
        self.auth.Cuit = cuit

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

    def get_receipt_types(self):
        response_xml = self.client.service.FEParamGetTiposCbte(self.auth)
        receipt_types = []
        for result in response_xml.ResultGet.CbteTipo:
            receipt_type = ReceiptType(result.Id,
                                       result.Desc.encode("UTF-8"))
            receipt_types.append(receipt_type)
        return receipt_types

    def get_concept_types(self):
        response_xml = self.client.service.FEParamGetTiposConcepto(self.auth)
        concept_types = []
        for result in response_xml.ResultGet.ConceptoTipo:
            concept_type = ConceptType(result.Id,
                                       result.Desc.encode("UTF-8"))
            concept_types.append(concept_type)
        return concept_types

    def get_document_types(self):
        response_xml = self.client.service.FEParamGetTiposDoc(self.auth)
        document_types = []
        for result in response_xml.ResultGet.DocTipo:
            document_type = DocumentType(result.Id,
                                         result.Desc.encode("UTF-8"))
            document_types.append(document_type)
        return document_types

    def get_vat_types(self):
        response_xml = self.client.service.FEParamGetTiposIva(self.auth)
        vat_types = []
        for result in response_xml.ResultGet.IvaTipo:
            vat_type = VatType(result.Id,
                               result.Desc.encode("UTF-8"))
            vat_types.append(vat_type)
        return vat_types

    def get_currency_types(self):
        response_xml = self.client.service.FEParamGetTiposMonedas(self.auth)
        currency_types = []
        for result in response_xml.ResultGet.Moneda:
            currency_type = VatType(result.Id,
                                    result.Desc.encode("UTF-8"))
            currency_types.append(currency_type)
        return currency_types

    # Optional data types?

    # Tax (tribute) types?

    def get_sales_points(self):
        response_xml = self.client.service.FEParamGetPtosVenta(self.auth)
        sales_points = []
        for result in response_xml.ResultGet.PtoVenta:
            sales_point = SalesPoint(result.Nro,
                                     result.EmisionTipo,
                                     result.Bloqueado != "N",
                                     result.FchBaja)
            sales_points.append(sales_point)
        return sales_points

    # Currency quotes? (useless since only PES is available ATM)

    def ping(self):
        response_xml = self.client.service.FEDummy(self.auth)
        response = {
            "AppServer": response_xml.AppServer,
            "DbServer": response_xml.DbServer,
            "AuthServer": response_xml.AuthServer
        }
        return response

    def last_authorized_id(self, sales_point, invoice_type):
        response_xml = self.client.service. \
            FECompUltimoAutorizado(self.auth, sales_point, invoice_type)
        return response_xml.CbteNro

    # TODO: get_invoice: FECompConsultar
