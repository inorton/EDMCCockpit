from pathlib import Path
import json
import simple_websocket
from flask import render_template
from cockpit_types import CockpitModule, QueueSubscriber
from cockpit import sock


class JournalEndpointModule(CockpitModule):
    """Websocket for Journal events (builtin)"""
    def __init__(self):
        super(JournalEndpointModule, self).__init__("journal",
                                                    url_prefix="/journal",
                                                    root_path=str(Path(__file__).parent.absolute()))

    @property
    def has_page(self) -> bool:
        return True


journal_module = JournalEndpointModule()


@journal_module.route("/")
def raw_page():
    return render_template("journal.html", module=journal_module)


@sock.route("/events", bp=journal_module)
def events(ws: simple_websocket.Server):
    with journal_module.subscribe("journal") as msgs:
        msgs: QueueSubscriber
        while True:
            # send each message to the client
            message = msgs.queue.get()
            if message.entry:
                ws.send(json.dumps(message.entry))


def plug() -> CockpitModule:
    return journal_module
