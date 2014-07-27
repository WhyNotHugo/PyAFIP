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

from ..utils import GenericAfipType


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
        # TODO: calculate total with taxed+untaxed+exempt+vat+taxes
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

    # TODO: Add support for taxes


class Vat:

    def __init__(self, type, base, amount):
        self.type = type
        self.base = base
        self.amount = amount


class ReceiptType(GenericAfipType):
    pass


class ConceptType(GenericAfipType):
    pass


class DocumentType(GenericAfipType):
    pass


class VatType(GenericAfipType):
    pass


class SalesPoint:

    def __init__(self, number, type, blocked, deletion_date):
        self.number = number
        self.type = type
        self.blocked = blocked
        self.deletion_date = deletion_date

    def __repr__(self):
        return "Sales Point {}, uses {}, {}, deleted: {}" \
            .format(self.number, self.type,
                    "blocked" if self.blocked else "unblocked",
                    "No" if self.deletion_date == "NULL" else
                    self.deletion_date)
