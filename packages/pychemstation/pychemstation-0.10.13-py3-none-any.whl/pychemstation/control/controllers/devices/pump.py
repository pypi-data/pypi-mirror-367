from __future__ import annotations

import warnings

from ....utils.macro import Command
from ....control.controllers import CommunicationController
from ....utils.abc_tables.device import DeviceController
from ....utils.device_types import (
    SolventBottle,
    MaybeBottle,
    MaybePumpPosition,
    PumpValve,
    PumpPosition,
)
from ....utils.table_types import Table, RegisterFlag, Device


class PumpController(DeviceController):
    def __init__(
        self, controller: CommunicationController, table: Table | Device, offline: bool
    ):
        super().__init__(controller, table, offline)
        self.A_position: MaybePumpPosition = (
            self.load_pump_position(PumpValve.A) if not offline else None
        )
        self.B_position: MaybePumpPosition = (
            self.load_pump_position(PumpValve.B) if not offline else None
        )
        self.A1: MaybeBottle = None
        self.A2: MaybeBottle = None
        self.B1: MaybeBottle = None
        self.B2: MaybeBottle = None
        self.waste_bottle: MaybeBottle = None

    def load_pump_position(self, pump_valve: PumpValve) -> PumpPosition:
        match pump_valve:
            case PumpValve.A:
                return PumpPosition.from_str(
                    self._read_str_param(RegisterFlag.PUMPCHANNEL_SELECTION)
                )
            case PumpValve.B:
                return PumpPosition.from_str(
                    self._read_str_param(RegisterFlag.PUMPCHANNEL2_SELECTION)
                )
            case _:
                raise ValueError("Expected one of PumpValve.A or PumpValve.B")

    def load_bottles(self):
        self.A1 = self.get_solvent_bottle_a1()
        self.A2 = self.get_solvent_bottle_a2()
        self.B1 = self.get_solvent_bottle_b1()
        self.B2 = self.get_solvent_bottle_b2()

    @property
    def rinse_method(self):
        return self._rinse_method

    @rinse_method.setter
    def rinse_method(self, new_rinse_method: str):
        self._rinse_method = new_rinse_method

    def turn_off(self):
        self.send(Command.PUMP_OFF_CMD)

    def turn_on(self):
        self.send(Command.PUMP_ON_CMD)

    def get_solvent_bottle_a1(self) -> SolventBottle:
        return SolventBottle(
            absolute_filled=self._read_num_param(
                RegisterFlag.BOTTLE_A1_ABSOLUTE_FILLING
            ),
            percent_filled=self._read_num_param(RegisterFlag.BOTTLE_A1_PERCENT_FILLING),
            max_volume=self._read_num_param(RegisterFlag.BOTTLE_A1_MAX),
            in_use=self.A_position == PumpPosition.ONE,
            user_name=self._read_str_param(RegisterFlag.BOTTLE_A1_USER_NAME),
            type=PumpValve.A,
        )

    def get_solvent_bottle_a2(self) -> SolventBottle:
        return SolventBottle(
            absolute_filled=self._read_num_param(
                RegisterFlag.BOTTLE_A2_ABSOLUTE_FILLING
            ),
            percent_filled=self._read_num_param(RegisterFlag.BOTTLE_A2_PERCENT_FILLING),
            max_volume=self._read_num_param(RegisterFlag.BOTTLE_A2_MAX),
            in_use=self.A_position == PumpPosition.TWO,
            user_name=self._read_str_param(RegisterFlag.BOTTLE_A2_USER_NAME),
            type=PumpValve.A,
        )

    def get_solvent_bottle_b1(self) -> SolventBottle:
        return SolventBottle(
            absolute_filled=self._read_num_param(
                RegisterFlag.BOTTLE_B1_ABSOLUTE_FILLING
            ),
            percent_filled=self._read_num_param(RegisterFlag.BOTTLE_B1_PERCENT_FILLING),
            max_volume=self._read_num_param(RegisterFlag.BOTTLE_B1_MAX),
            in_use=self.A_position == PumpPosition.ONE,
            user_name=self._read_str_param(RegisterFlag.BOTTLE_B1_USER_NAME),
            type=PumpValve.B,
        )

    def get_solvent_bottle_b2(self) -> SolventBottle:
        return SolventBottle(
            absolute_filled=self._read_num_param(
                RegisterFlag.BOTTLE_B2_ABSOLUTE_FILLING
            ),
            percent_filled=self._read_num_param(RegisterFlag.BOTTLE_B2_PERCENT_FILLING),
            max_volume=self._read_num_param(RegisterFlag.BOTTLE_B2_MAX),
            in_use=self.A_position == PumpPosition.TWO,
            user_name=self._read_str_param(RegisterFlag.BOTTLE_B2_USER_NAME),
            type=PumpValve.B,
        )

    def get_waste_bottle_stats(self):
        max_vol = None
        try:
            max_vol = self._read_num_param(RegisterFlag.WASTE_BOTTLE_MAX)
        except RuntimeError:
            warnings.warn(
                "No maximum volume available! All other SolventBottle parameters may not be reliable."
            )
        self.waste_bottle = SolventBottle(
            absolute_filled=self._read_num_param(RegisterFlag.WASTE_BOTTLE_PERCENT),
            percent_filled=self._read_num_param(RegisterFlag.WASTE_BOTTLE_ABSOLUTE),
            max_volume=max_vol,
            in_use=True,
            user_name="Waste Bottle",
            type=None,
        )
