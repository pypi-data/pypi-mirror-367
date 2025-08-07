from ....control.controllers import CommunicationController
from ....utils.abc_tables.device import DeviceController
from ....utils.table_types import Table, Device, RegisterFlag
from ....utils.tray_types import Tray, VialBar, FiftyFourVialPlate


class SampleInfo(DeviceController):
    def turn_off(self):
        raise NotImplementedError

    def turn_on(self):
        raise NotImplementedError

    def __init__(
        self, controller: CommunicationController, table: Table | Device, offline: bool
    ):
        super().__init__(controller, table, offline)

    def get_location(self) -> Tray:
        location = self._read_str_param(RegisterFlag.VIAL_NUMBER)
        try:
            return FiftyFourVialPlate.from_int(location)
        except ValueError:
            try:
                return VialBar(location)
            except ValueError:
                raise ValueError("Could not read vial location.")
