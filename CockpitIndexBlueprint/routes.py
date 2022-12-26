from flask import render_template
from pathlib import Path
from cockpit import server, CockpitServer
from cockpit_types import CockpitModule
from EDMarketConnector import appversion
import sys


class IndexModule(CockpitModule):

    def __init__(self):
        super(IndexModule, self).__init__("cockpit_home",
                                          url_prefix="/",
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
