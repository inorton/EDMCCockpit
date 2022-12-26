"""The CockpitService server plugin"""
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import os
import sys
import socket
from ttkHyperlinkLabel import HyperlinkLabel

from cockpit import CockpitServer

this = sys.modules[__name__]  # For holding module globals
this.port = 13302
plugin_name = "CockpitService"
server = CockpitServer()


def plugin_start3(plugindir: str) -> str:
    global server
    staticdir = os.path.join(plugindir, "static")
    server.setup(staticdir)
    server.start()
    return plugin_name


def plugin_app(parent: tk.Frame):
    """
    Create TK widgets for the EDMC main window
    """
    ipaddr = socket.gethostbyname(socket.gethostname())
    linktext = "http://{}:{}".format(ipaddr, server.port)
    frame = tk.Frame(parent)
    this.label = tk.Label(
        frame,
        text="Cockpit:",
        justify=tk.LEFT
    )
    this.label.grid(row=1, column=0, sticky=tk.W)
    this.link = HyperlinkLabel(
        frame, text=linktext, compound=tk.RIGHT, url=linktext, name='remotes')

    this.link.grid(row=1, column=1, sticky=tk.EW)
    return frame

