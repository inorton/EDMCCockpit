"""Base classes for Cockpit Service"""
from easyhttpd import ServerThread

HTTP_PORT = 13302


class CockpitServer(ServerThread):

    def __init__(self):
        super(CockpitServer, self).__init__(HTTP_PORT)

