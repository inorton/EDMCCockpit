"""Base classes for Cockpit Service"""
from typing import Dict, Any, Optional, Set

from libs import Flask
from threading import Thread
from pathlib import Path
from cockpit_types import CockpitModule


HTTP_PORT = 13302
LISTEN_ADDR = "0.0.0.0"
SERVER_ROOT = Path(__file__).parent.absolute() / "root"
app = Flask("EDMC Cockpit", root_path=str(SERVER_ROOT), static_folder=None)

routes: Set[str] = set()


class CockpitServer(Thread):

    def __init__(self, flask_app):
        super(CockpitServer, self).__init__()
        self.daemon = True
        self.port = HTTP_PORT
        self.app = flask_app
        self.modules: Dict[str, CockpitModule] = {}

    def run(self) -> None:
        self.app.run(host=LISTEN_ADDR, port=HTTP_PORT, use_reloader=False)

    def register_module(self, module: CockpitModule, path: Optional[str] = None):
        if module and module.name:
            if module.name in self.modules:
                raise KeyError(module.name)
            self.modules[module.name] = module
            self.app.register_blueprint(module, url_prefix=path)
            module.app = self.app
            return module
        return None

    def journal_entry(self,
                      cmdr: str,
                      is_beta: bool,
                      system_name: str,
                      station: str,
                      entry: Dict[str, Any],
                      state: Dict[str, Any]
                      ) -> Optional[str]:
        for module in self.modules:
            module: CockpitModule
            err: Optional[str] = module.journal_entry(cmdr, is_beta, system_name, station, entry, state)
            if err:
                print(f"cockpit module '{module.name}' journal error: '{err}'")
        return None


server = CockpitServer(app)
