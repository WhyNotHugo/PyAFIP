#!/usr/bin/env python2

from afip.endpoints import Testing
from afip.wsaa import AuthorizationTicket
from afip.wsfev1 import InvoiceService, Invoice, InvoiceDetail, Vat
from datetime import datetime, timedelta

# run test/wsaa.py > ticket to generate a ticket file
ticket_data = open("ticket")
cuit = 20329642330

ticket = AuthorizationTicket(Testing(), "hyperion.key", "hyperion.crt", "wsfe")
ticket.load(ticket_data.read())

# ~~~ A-type invoice ~~~
print("~~~ Type C invoices ~~~")
invoice_type = 11

# ~~~ Test last_authorized_id ~~~
invoice_service = InvoiceService(Testing, ticket, cuit)
last_id = invoice_service.last_authorized_id(sales_point=1,
                                             invoice_type=invoice_type)
print("Last invoice of type {}: {}.".format(invoice_type, last_id))

# ~~~ Test authorize_invoice, C-type invoice ~~~

now = datetime.now()
expiration = now + timedelta(days=30)
invoice = Invoice(invoice_type=invoice_type, amount=1, sales_point=1)
invoice.add_detail(InvoiceDetail(concept=2,
                                 document_type=80,
                                 document_number="30710174500",
                                 from_invoice=last_id+1,
                                 to_invoice=last_id+1,
                                 date=now,
                                 total=1500,
                                 service_from_date=now,
                                 service_to_date=now,
                                 expiration_date=expiration)
                   )

invoice_service.authorize_invoice(invoice)
print("Validated invoice, CAE: {}, exp: {}.".format(invoice.cae,
                                                    invoice.cae_expiration))

# ~~~ A-type invoice ~~~
print("~~~ Type A invoices ~~~")
invoice_type = 1

# ~~~ Test last_authorized_id ~~~
invoice_service = InvoiceService(Testing, ticket, cuit)
last_id = invoice_service.last_authorized_id(sales_point=1,
                                             invoice_type=invoice_type)
print("Last invoice of type {}: {}.".format(invoice_type, last_id))

# ~~~ Test authorize_invoice ~~~

now = datetime.now()
expiration = now + timedelta(days=30)
invoice = Invoice(invoice_type=invoice_type, amount=1, sales_point=1)
invoice_detail = InvoiceDetail(concept=2,
                               document_type=80,
                               document_number="30710174500",
                               from_invoice=last_id+1,
                               to_invoice=last_id+1,
                               date=now,
                               total=1210,
                               net_taxed=1000,
                               vat_amount=210,
                               service_from_date=now,
                               service_to_date=now,
                               expiration_date=expiration)
invoice_detail.add_vat(Vat(type=5, base=1000, amount=210))
invoice.add_detail(invoice_detail)
invoice_service.authorize_invoice(invoice)
print("Validated invoice, CAE: {}, exp: {}.".format(invoice.cae,
                                                    invoice.cae_expiration))
