import dataclasses
import time
from pathlib import Path
import json
from typing import Dict, Any, Optional, List

import simple_websocket
from flask import render_template
from cockpit_types import CockpitModule, QueueSubscriber, DashboardItem
from cockpit import sock


@dataclasses.dataclass
class RouteStar:
    name: str
    starclass: str

    @property
    def can_scoop(self) -> bool:
        return self.starclass in "KGBFOAM"


class FuelModule(CockpitModule):
    """Fuel tank and scoop reporting"""
    def __init__(self):
        super(FuelModule, self).__init__("Fuel Manager",
                                         url_prefix="/fuel",
                                         root_path=str(Path(__file__).parent.absolute()))
        self.fuel_tanks = []
        self.max_capacity = 0.0
        self.navroute: List[RouteStar] = []
        self.next_star: Optional[RouteStar] = None

    @property
    def calibrated(self) -> bool:
        return len(self.fuel_tanks) > 0

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
        event = entry.get("event", None)
        if event == "Loadout":
            self.fuel_tanks.clear()
            for item in entry.get("Modules", []):
                if "_fueltank_" in item.get("Item"):
                    self.fuel_tanks.append(item["Item"])
            self.update_tank_capacity()
        elif event == "NavRoute":
            route = entry.get("Route", [])
            self.navroute.clear()
            for jump in route:
                star = RouteStar(jump["StarSystem"], jump["StarClass"])
                self.navroute.append(star)
        elif event == "NavRouteClear":
            self.navroute.clear()
        elif event == "FSDTarget":
            next_star = RouteStar(entry["Name"], entry["StarClass"])
            self.next_star = next_star
        elif event == "FSDJump":
            # jumping, remove the star from the route
            self.navroute = [star for star in self.navroute if star.name != entry["StarSystem"]]

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
    scoop_start_fuel = 0
    scoop_start_time = 0

    with module.subscribe("dashboard") as msgs:
        msgs: QueueSubscriber
        previous = ""
        while ws.connected:
            # send only fuel events to clients
            message: DashboardItem = msgs.queue.get()
            if message.entry and "Fuel" in message.entry:
                data = dict(message.entry.get("Fuel", {}))
                if "FuelMain" not in data:
                    continue
                data["route"] = [{
                    "name": x.name,
                    "starclass": x.starclass,
                    "can_scoop": x.can_scoop,
                } for x in module.navroute]
                if module.next_star:
                    data["scoop_next"] = module.next_star.can_scoop
                data["scooping"] = message.scooping
                data["low"] = message.low_fuel
                data["overheat"] = message.overheating
                module.max_capacity = max(module.max_capacity, data["FuelMain"])
                data["max"] = module.tank_capacity
                data["calibrated"] = module.calibrated
                data["scoop_time"] = -1
                # calculate scoop ETC
                if not message.scooping:
                    scoop_start_time = 0
                else:
                    if scoop_start_time == 0:
                        scoop_start_time = time.monotonic()
                        scoop_start_fuel = data["FuelMain"]
                    else:
                        now = time.monotonic()
                        scoop_time = now - scoop_start_time
                        scoop_total = data["FuelMain"] - scoop_start_fuel
                        scoop_rate = scoop_total / scoop_time  # t/sec
                        remaining = module.tank_capacity - data["FuelMain"]
                        scoop_duration = int(remaining / scoop_rate)
                        data["scoop_time"] = scoop_duration

                dump = json.dumps(data)

                if dump == previous:
                    continue
                data["timestamp"] = message.entry["timestamp"]
                ws.send(json.dumps(data))
                previous = dump
