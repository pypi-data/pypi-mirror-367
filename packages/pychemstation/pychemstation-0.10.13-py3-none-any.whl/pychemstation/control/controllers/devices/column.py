from typing import List, Dict

from ....control.controllers import CommunicationController
from ....utils.abc_tables.device import DeviceController
from ....utils.macro import Command
from ....utils.method_types import Param, PType
from ....utils.table_types import Device, Table, RegisterFlag


class ColumnController(DeviceController):
    def __init__(
        self, controller: CommunicationController, table: Table | Device, offline: bool
    ):
        super().__init__(controller, table, offline)
        if not self.offline:
            self.display_to_internal: Dict[str, str] = {
                display_name: real_name
                for display_name, real_name in zip(
                    self.check_available_column_positions(),
                    self._internal_column_positions(),
                )
            }
            self.internal_to_display: Dict[str, str] = dict(
                map(reversed, self.display_to_internal.items())  # type: ignore
            )

    def check_column_position(self):
        return self.internal_to_display[
            self._read_str_param(register_flag=RegisterFlag.COLUMN_POSITION)
        ]

    def _internal_column_positions(self) -> List[str]:
        return self._read_str_param(
            register_flag=RegisterFlag.AVAIL_COLUMN_POSITIONS
        ).split("|")

    def check_available_column_positions(self) -> List[str]:
        return self._read_str_param(
            register_flag=RegisterFlag.AVAIL_COLUMN_DISPLAY_VALUES
        ).split("|")

    def change_column_position(self, column: str):
        if column not in self.display_to_internal.keys():
            raise ValueError(f"Please use one of: {self.display_to_internal.keys()}")
        self._update_param(
            Param(
                ptype=PType.STR,
                chemstation_key=RegisterFlag.COLUMN_POSITION,
                val=self.display_to_internal[column],
            ),
        )

    def turn_off(self):
        self.sleepy_send(Command.COLUMN_OFF_CMD)
        pass

    def turn_on(self):
        self.sleepy_send(Command.COLUMN_ON_CMD)

    def download(self):
        self.sleepy_send("DownloadRCMethod THM1")
