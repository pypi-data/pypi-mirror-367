from __future__ import annotations

import warnings

from ...controllers import CommunicationController
from ....utils.abc_tables.device import DeviceController
from ....utils.device_types import DADChannels, DADChannel
from ....utils.macro import Command
from ....utils.method_types import Param, PType
from ....utils.table_types import RegisterFlag, Table, Device


class DADController(DeviceController):
    def __init__(
        self, controller: CommunicationController, table: Table | Device, offline: bool
    ):
        super().__init__(controller, table, offline)

    def download(self):
        self.sleepy_send("DownloadRCMethod DAD1")

    def turn_off(self):
        self.send(Command.LAMP_OFF_CMD)

    def turn_on(self):
        self.send(Command.LAMP_ON_CMD)

    def load_wavelengths(self) -> DADChannels:
        return DADChannels(
            A=self._read_num_param(RegisterFlag.SIGNAL_A),
            A_ON=bool(self._read_num_param(RegisterFlag.SIGNAL_A_USED)),
            B=self._read_num_param(RegisterFlag.SIGNAL_B),
            B_ON=bool(self._read_num_param(RegisterFlag.SIGNAL_B_USED)),
            C=self._read_num_param(RegisterFlag.SIGNAL_C),
            C_ON=bool(self._read_num_param(RegisterFlag.SIGNAL_C_USED)),
            D=self._read_num_param(RegisterFlag.SIGNAL_D),
            D_ON=bool(self._read_num_param(RegisterFlag.SIGNAL_D_USED)),
            E=self._read_num_param(RegisterFlag.SIGNAL_E),
            E_ON=bool(self._read_num_param(RegisterFlag.SIGNAL_E_USED)),
        )

    def edit_wavelength(self, signal: int, wavelength: DADChannel):
        warnings.warn("You may need to check that the wavelength is calibrated.")
        register = RegisterFlag.SIGNAL_A
        match wavelength:
            case DADChannel.A:
                register = RegisterFlag.SIGNAL_A
            case DADChannel.B:
                register = RegisterFlag.SIGNAL_B
            case DADChannel.C:
                register = RegisterFlag.SIGNAL_C
            case DADChannel.D:
                register = RegisterFlag.SIGNAL_D
            case DADChannel.E:
                register = RegisterFlag.SIGNAL_E
        self._update_param(
            Param(
                ptype=PType.NUM,
                val=signal,
                chemstation_key=register,
            )
        )
        self.download()

    def set_wavelength_usage(self, wavelength: DADChannel, on: bool):
        register = RegisterFlag.SIGNAL_A_USED
        match wavelength:
            case DADChannel.A:
                register = RegisterFlag.SIGNAL_A_USED
            case DADChannel.B:
                register = RegisterFlag.SIGNAL_B_USED
            case DADChannel.C:
                register = RegisterFlag.SIGNAL_C_USED
            case DADChannel.D:
                register = RegisterFlag.SIGNAL_D_USED
            case DADChannel.E:
                register = RegisterFlag.SIGNAL_E_USED
        self._update_param(
            Param(
                ptype=PType.NUM,
                val=int(on),
                chemstation_key=register,
            )
        )
        self.download()
