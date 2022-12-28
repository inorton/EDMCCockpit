from pathlib import Path
import json
import simple_websocket
from flask import render_template
from cockpit_types import CockpitModule, QueueSubscriber
from cockpit import sock


class DashboardEndpointModule(CockpitModule):
    """Websocket for status events (builtin)"""
    def __init__(self):
        super(DashboardEndpointModule, self).__init__("dash",
                                                      url_prefix="/dash",
                                                      root_path=str(Path(__file__).parent.absolute()))

    @property
    def has_page(self) -> bool:
        return True


dashboard_module = DashboardEndpointModule()


@dashboard_module.route("/")
def raw_page():
    return render_template("dash.html", module=dashboard_module)


@sock.route("/events", bp=dashboard_module)
def events(ws: simple_websocket.Server):
    with dashboard_module.subscribe("dashboard") as msgs:
        msgs: QueueSubscriber
        while True:
            # send each message to the client
            message = msgs.queue.get()
            if message.entry:
                ws.send(json.dumps(message.entry))


def plug() -> CockpitModule:
    return dashboard_module
