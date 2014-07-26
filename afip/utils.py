import httplib
from httplib import HTTPConnection, HTTPS_PORT
import ssl
import socket
import sys
import logging


"""
See http://askubuntu.com/questions/116020/ for details on why the following is
necessary.
"""


class HTTPSConnection(HTTPConnection):

    "This class allows communication via SSL."
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ssl_version=ssl.PROTOCOL_TLSv1)

# now we override the one in httplib
httplib.HTTPSConnection = HTTPSConnection
# ssl_version corrections are done


def enableDebugLog():
    logger = logging.getLogger()
    logger.root.setLevel(logging.DEBUG)
    logger.root.addHandler(logging.StreamHandler(sys.stdout))


class AfipFormatMixin:

    def format_date(self, date):
        """
        Sometimes, and only sometimes, TESTING will complain about an invalid
        date format if you use .isoformat() for the authenticatión
        generationTime.

        This is the exact format their documentation uses.
        """
        return date.strftime("%Y-%m-%dT%H:%M:%S-00:00")

    def format_short_date(self, date):
        return date.strftime("%Y%m%d")


class AfipException(Exception):

    """
    Wraps around errors returns by AFIP's WS.
    """

    def __init__(self, err):
        Exception.__init__(self, "Error {}: {}"
                           .format(err.Code, err.Msg.encode("latin-1")))


class GenericAfipType:

    def __init__(self, id, description):
        self.id = id
        self.description = description

    def __repr__(self):
        return "{}: {}".format(self.id, self.description)
