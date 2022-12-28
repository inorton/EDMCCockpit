"""The CockpitService server plugin"""
from typing import Dict, Any
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import sys
import socket
from ttkHyperlinkLabel import HyperlinkLabel

from cockpit import server

this = sys.modules[__name__]  # For holding module globals
plugin_name = "CockpitService"


def plugin_start3(plugindir: str) -> str:
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


def journal_entry(cmdr: str,
                  is_beta: bool,
                  system_name: str,
                  station: str,
                  entry: Dict[str, Any],
                  state: Dict[str, Any]
                  ):
    return server.journal_entry(cmdr, is_beta, system_name, station, entry, state)


def dashboard_entry(cmdr: str, is_beta: bool, entry: Dict[str, Any]):
    server.dashboard_entry(cmdr, is_beta, entry)
