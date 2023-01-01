"""Base classes for Cockpit Service"""
import socket
from typing import Dict, Any, Optional
from libs import Flask, Sock
from threading import Thread
from pathlib import Path
import importlib.util
import importlib.machinery
from cockpit_types import CockpitModule


HTTP_PORT = 13302
LISTEN_ADDR = "0.0.0.0"
SERVER_ROOT = Path(__file__).parent.absolute() / "root"  # intentionally empty

MODULES_DIR = Path(__file__).parent.absolute() / "CockpitModules"

app = Flask("EDMC Cockpit", root_path=str(SERVER_ROOT), static_folder=None)
sock = Sock(app)


class CockpitServer(Thread):

    def __init__(self, flask_app):
        super(CockpitServer, self).__init__()
        self.daemon = True
        self.port = HTTP_PORT
        self.app = flask_app
        self.modules: Dict[str, CockpitModule] = {}
        self.ipaddr = socket.gethostbyname(socket.gethostname())

    def run(self) -> None:
        self.app.run(host=LISTEN_ADDR, port=HTTP_PORT, use_reloader=False, debug=True)

    def register_module(self, module: CockpitModule):
        if module and module.name:
            if module.name in self.modules:
                raise KeyError(module.name)
            self.modules[module.name] = module
            self.app.register_blueprint(module, url_prefix=module.url_prefix)
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
        for module in self.modules.values():
            module: CockpitModule
            err: Optional[str] = module.journal_entry(cmdr, is_beta, system_name, station, entry, state)
            if err:
                print(f"cockpit module '{module.name}' journal error: '{err}'")
        return None

    def dashboard_entry(self,
                        cmdr: str,
                        is_beta: bool,
                        entry: Dict[str, Any]
                        ) -> None:
        for module in self.modules.values():
            module: CockpitModule
            module.dashboard_entry(cmdr, is_beta, entry)

    def load_modules(self):
        modules = MODULES_DIR.glob("*")
        for item in modules:
            if item.is_dir():
                module = load_module(item)
                if module:
                    self.register_module(module)


def load_module(folder: Path) -> Optional[CockpitModule]:
    """load a cockpit module from a folder and return the blueprint"""
    routes_file = [x for x in folder.glob("routes.py")]
    if routes_file:
        name = f"{folder.name}.routes"
        loader = importlib.machinery.SourceFileLoader(name, str(routes_file[0]))
        spec = importlib.util.spec_from_loader(name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        if "plug" in dir(module):
            return module.plug()
    return None


server = CockpitServer(app)
server.load_modules()

