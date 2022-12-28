from pathlib import Path
import json
from typing import Dict, Any, Optional

import simple_websocket
from flask import render_template
from cockpit_types import CockpitModule, QueueSubscriber, DashboardItem
from cockpit import sock


class FuelModule(CockpitModule):
    """Fuel tank and scoop reporting"""
    def __init__(self):
        super(FuelModule, self).__init__("Fuel Manager",
                                         url_prefix="/fuel",
                                         root_path=str(Path(__file__).parent.absolute()))
        self.fuel_tanks = []
        self.max_capacity = 0.0

    def update_tank_capacity(self):
        total = 0.0
        for tank in self.fuel_tanks:
            words = tank.split("_")
            tank_size = words[-2]
            capacity = 1.0
            if tank_size == "size8":
                capacity = 256
            elif tank_size == "size7":
                capacity = 128
            elif tank_size == "size6":
                capacity = 64
            elif tank_size == "size5":
                capacity = 32
            elif tank_size == "size4":
                capacity = 16
            elif tank_size == "size3":
                capacity = 8
            elif tank_size == "size2":
                capacity = 4
            elif tank_size == "size1":
                capacity = 2
            total += capacity

        self.max_capacity = total

    @property
    def tank_capacity(self) -> float:
        return self.max_capacity

    def journal_entry(self, cmdr: str, is_beta: bool, system_name: str, station: str, entry: Dict[str, Any],
                      state: Dict[str, Any]):
        if entry.get("event", None) == "Loadout":
            self.fuel_tanks.clear()
            for item in entry.get("Modules", []):
                if "_fueltank_" in item.get("Item"):
                    self.fuel_tanks.append(item["Item"])
            self.update_tank_capacity()

    def has_page(self) -> bool:
        return True


module = FuelModule()


def plug() -> CockpitModule:
    return module


@module.route("/")
def fuel():
    return render_template("fuel.html", module=module)


@sock.route("/events", bp=module)
def events(ws: simple_websocket.Server):
    with module.subscribe("dashboard") as msgs:
        msgs: QueueSubscriber
        previous = ""
        while ws.connected:
            # send only fuel events to clients
            message: DashboardItem = msgs.queue.get()
            if message.entry:
                data = dict(message.entry.get("Fuel", {}))
                data["scooping"] = message.scooping
                data["low"] = message.low_fuel
                data["overheat"] = message.overheating
                module.max_capacity = max(module.max_capacity, data["FuelMain"])
                data["max"] = module.tank_capacity
                dump = json.dumps(data)
                if dump != previous:
                    data["timestamp"] = message.entry["timestamp"]
                    ws.send(json.dumps(data))
                previous = dump
