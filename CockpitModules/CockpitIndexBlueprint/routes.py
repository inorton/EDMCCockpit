from flask import render_template, send_from_directory
from pathlib import Path
from cockpit import server, CockpitServer
from cockpit_types import CockpitModule
from config import appversion
import sys


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


@home.route("/favicon.ico")
def favicon():
    return send_from_directory(
        str(Path(home.root_path) / home.static_folder), "EDMarketConnector.ico",
        mimetype="image/vnd.microsoft.icon")


def plug() -> CockpitModule:
    return home
