import io
import sys
import pyqrcode
import png
from flask import render_template, send_from_directory, send_file
from pathlib import Path
from cockpit import server, CockpitServer
from cockpit_types import CockpitModule
from config import appversion


class IndexModule(CockpitModule):
    """The EDMC Cockpit index module (builtin)"""
    def __init__(self):
        super(IndexModule, self).__init__("cockpit_home",
                                          url_prefix="/",
                                          static_folder="static",
                                          template_folder="templates",
                                          root_path=str(Path(__file__).parent.absolute()))

    @property
    def server(self) -> CockpitServer:
        return server

    @property
    def edmc_version(self) -> str:
        return str(appversion())

    @property
    def python_version(self) -> str:
        return str(sys.version)


home = IndexModule()


@home.route("/")
@home.route("/index.html")
def homepage():
    """Cockpit Homepage"""
    return render_template("index.html", module=home)


@home.route("/qrcode.png")
def qrcode_png():
    ipaddr = home.server.ipaddr
    port = home.server.port
    url = f"http://{ipaddr}:{port}"
    qrcode = pyqrcode.create(url)
    buffer = io.BytesIO()
    qrcode.png(buffer, scale=4)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@home.route("/favicon.ico")
def favicon():
    return send_from_directory(
        str(Path(home.root_path) / home.static_folder), "EDMarketConnector.ico",
        mimetype="image/vnd.microsoft.icon")


def plug() -> CockpitModule:
    return home
