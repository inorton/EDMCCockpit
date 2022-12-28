import contextlib
from abc import ABC
from dataclasses import dataclass
from threading import Lock
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from flask import Blueprint
from uuid import uuid4
from cockpit_utils import BufferQueue
import edmc_data


@dataclass
class DashboardItem:
    cmdr: str
    is_beta: bool
    entry: Dict[str, Any]

    @property
    def flags(self) -> int:
        return int(self.entry.get("Flags", 0))

    @property
    def flags2(self) -> int:
        return int(self.entry.get("Flags2", 0))

    @property
    def docked(self) -> bool:
        return (self.flags & edmc_data.FlagsDocked) != 0

    @property
    def scooping(self) -> bool:
        return (self.flags & edmc_data.FlagsScoopingFuel) != 0

    @property
    def low_fuel(self) -> bool:
        return (self.flags & edmc_data.FlagsLowFuel) != 0

    @property
    def overheating(self) -> bool:
        return (self.flags & edmc_data.FlagsOverHeating) != 0

@dataclass
class JournalItem:
    cmdr: str
    is_beta: bool
    system: str
    station: str
    entry: Dict[str, Any]
    state: Dict[str, Any]


class QueueSubscriber:
    """Recieve mesages"""
    def __init__(self):
        self.id = uuid4()
        self.queue = BufferQueue(maxsize=10)

    def __hash__(self):
        return self.id.__hash__()


class CockpitModule(Blueprint, ABC):
    """Base class of all cockpit modules"""

    def __init__(self, name: str,
                 root_path: Optional[str] = None,
                 url_prefix: Optional[str] = None,
                 template_folder: Optional[Union[str, Path]] = None,
                 static_folder: Optional[Union[str, Path]] = None):

        if template_folder is None:
            template_folder = "templates"
        if static_folder is None:
            static_folder = "static"

        super(CockpitModule, self).__init__(name, __name__,
                                            url_prefix=url_prefix,
                                            root_path=root_path,
                                            template_folder=template_folder,
                                            static_folder=static_folder)
        self._lock = Lock()
        self.subscribers: Dict[str, List[QueueSubscriber]] = {
            "journal": [],
            "dashboard": []
        }
    @property
    def has_page(self) -> bool:
        return True

    def _subscribe(self, busname: str, subscriber: QueueSubscriber):
        with self._lock:
            if busname not in self.subscribers:
                raise KeyError(busname)
            self.subscribers[busname].append(subscriber)

    def _unsubscribe(self, remove: QueueSubscriber):
        if not remove:
            return
        with self._lock:
            for busname in self.subscribers:
                if remove in self.subscribers[busname]:
                    self.subscribers[busname].remove(remove)

    @contextlib.contextmanager
    def subscribe(self, busname: str) -> QueueSubscriber:
        """temporarily subscribe to a queue"""
        target = QueueSubscriber()
        self._subscribe(busname, target)
        yield target
        self._unsubscribe(target)

    def journal_entry(self,
                      cmdr: str,
                      is_beta: bool,
                      system_name: str,
                      station: str,
                      entry: Dict[str, Any],
                      state: Dict[str, Any]
                      ) -> Optional[str]:
        """Enqueue a journal entry to the module queue buffer"""
        try:
            item = JournalItem(cmdr=cmdr,
                               is_beta=is_beta,
                               system=system_name,
                               station=station,
                               entry=entry,
                               state=state)
            send_to: List[QueueSubscriber] = []
            with self._lock:
                for subscriber in self.subscribers.get("journal", []):
                    send_to.append(subscriber)
            # reduce thread blocking
            for subscriber in send_to:
                subscriber.queue.put(item)

        except Exception as err:
            return str(err)

    def dashboard_entry(self, cmdr: str, is_beta: bool, entry: Dict[str, Any]):
        item = DashboardItem(cmdr=cmdr,
                             is_beta=is_beta,
                             entry=entry)
        send_to: List[QueueSubscriber] = []
        with self._lock:
            for subscriber in self.subscribers.get("dashboard", []):
                send_to.append(subscriber)
        # reduce thread blocking
        for subscriber in send_to:
            subscriber.queue.put(item)
