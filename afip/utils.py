import sys
import logging


def enableDebugLog():
    logger = logging.getLogger()
    logger.root.setLevel(logging.DEBUG)
    logger.root.addHandler(logging.StreamHandler(sys.stdout))


class AfipFormatMixin:

    def format_date(self, date):
        """
        Sometimes, and only sometimes, TESTING will complain about an invalid
        date format if you use .isoformat() for the authentication
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
