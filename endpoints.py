"""
URLs for the endpoints for both the test and prod servers
"""

class Production:

    WSAA = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
    WSFEV1 = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"


class Testing:

    WSAA = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
    WSFEV1 = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
