from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Union
from flask import Blueprint

from dashboard import dashboard
from cockpit_utils import BufferQueue


@dataclass
class JournalItem:
    cmdr: str
    is_beta: bool
    system: str
    station: str
    entry: Dict[str, Any]
    state: Dict[str, Any]


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

    journal = BufferQueue(maxsize=100)

    @property
    def dashboard(self):
        return dashboard

    def journal_entry(self,
                      cmdr: str,
                      is_beta: bool,
                      system_name: str,
                      station: str,
                      entry: Dict[str, Any],
                      state: Dict[str, Any]
                      ) -> Optional[str]:
        try:
            item = JournalItem(cmdr=cmdr,
                               is_beta=is_beta,
                               system=system_name,
                               station=station,
                               entry=entry,
                               state=state)
            self.journal.put(item)
        except Exception as err:
            return str(err)
