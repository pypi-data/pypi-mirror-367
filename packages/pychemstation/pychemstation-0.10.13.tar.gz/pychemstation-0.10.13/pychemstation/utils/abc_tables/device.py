from __future__ import annotations

from abc import ABC, abstractmethod

from .table import ABCTableController
from ..table_types import Table, Device
from ...control.controllers import CommunicationController


class DeviceController(ABCTableController, ABC):
    """Abstract controller representing tables that contain device information.

    :param controller: controller for sending MACROs
    :param table: contains register keys for accessing table in Chemstation
    :param offline: whether the communication controller is online.
    """

    def get_row(self, row: int):
        raise NotImplementedError

    def __init__(
        self, controller: CommunicationController, table: Table | Device, offline: bool
    ):
        super().__init__(controller=controller, table=table)
        self.offline = offline

    def __new__(cls, *args, **kwargs):
        if cls is ABCTableController:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def download(self):
        raise NotImplementedError

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def turn_on(self):
        pass
