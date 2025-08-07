"""
Module to provide API for higher-level HPLC actions.

Authors: Lucy Hao
"""

from __future__ import annotations

import os.path
from typing import Dict, List, Optional, Tuple, Union

from .controllers.devices.column import ColumnController
from .controllers.devices.dad import DADController
from .controllers.devices.injector import InjectorController
from .controllers.data_aq.sequence import SequenceController, MethodController
from .controllers.devices.pump import PumpController
from .controllers.devices.sample_info import SampleInfo
from ..analysis import AgilentHPLCChromatogram, AgilentChannelChromatogramData
from ..analysis.process_report import AgilentReport, ReportType
from ..control.controllers import CommunicationController
from ..utils.injector_types import InjectorTable
from ..utils.macro import Command, Response, Status
from ..utils.method_types import MethodDetails
from ..utils.sequence_types import SequenceTable, SequenceDataFiles
from ..utils.table_types import Table, Device


class HPLCController:
    # tables
    METHOD_TIMETABLE = Table(register="RCPMP1Method[1]", name="Timetable")

    SEQUENCE_TABLE = Table(register="_sequence[1]", name="SeqTable1")

    INJECTOR_TABLE = Table(register="RCWLS1Pretreatment[1]", name="InstructionTable")

    PUMP_DEVICE = Device(register="RCPMP1Status")

    INJECTOR_DEVICE = Device(register="RCWLS1Method")

    SAMPLE_INFO = Table(register="_CONFIG", name="SampleInfo")

    COLUMN_TEMP_DEVICE = Device(register="RCTHM1Method")

    DAD_DEVICE = Device(register="RCDAD1Method")

    def __init__(
        self,
        comm_dir: str,
        method_dir: Optional[str] = None,
        sequence_dir: Optional[str] = None,
        extra_data_dirs: Optional[List[str]] = None,
        offline: bool = False,
        debug: bool = False,
    ):
        """Initialize HPLC controller. The `hplc_talk.mac` macro file must be loaded in the Chemstation software.
        `comm_dir` must match the file path in the macro file. All file paths are normal strings, with the left slash
        double escaped: "C:\\my_folder\\"

        :param comm_dir: Name of directory for communication, where ChemStation will read and write from. Can be any existing directory.
        the first one in the list. In other words, the first dir in the list is highest prio. Must be "normal" strings and not r-strings.
        :raises FileNotFoundError: If either `data_dir`, `method_dir`, `sequence_dir`, `sequence_data_dir`or `comm_dir` is not a valid directory.
        """
        self.comm: CommunicationController = CommunicationController(
            comm_dir=comm_dir, debug=debug, offline=offline
        )
        data_dirs: List[str] = []
        if not offline:
            if not method_dir or not sequence_dir or not extra_data_dirs:
                method_dir, sequence_dir, data_dirs = self.comm.get_chemstation_dirs()
            if extra_data_dirs:
                data_dirs.extend(extra_data_dirs)
            data_dirs = list(set([os.path.normpath(p) for p in data_dirs]))
        if (method_dir and sequence_dir and data_dirs and not offline) or offline:
            self.method_controller: MethodController = MethodController(
                controller=self.comm,
                src=method_dir,
                data_dirs=data_dirs,
                table=self.METHOD_TIMETABLE,
                offline=offline,
                injector=InjectorController(
                    controller=self.comm, table=self.INJECTOR_TABLE, offline=offline
                ),
                pump=PumpController(
                    controller=self.comm, table=self.PUMP_DEVICE, offline=offline
                ),
                dad=DADController(
                    controller=self.comm, table=self.DAD_DEVICE, offline=offline
                ),
                column=ColumnController(
                    controller=self.comm, table=self.COLUMN_TEMP_DEVICE, offline=offline
                ),
                sample_info=SampleInfo(
                    controller=self.comm, table=self.SAMPLE_INFO, offline=offline
                ),
            )
            self.sequence_controller: SequenceController = SequenceController(
                controller=self.comm,
                src=sequence_dir,
                data_dirs=data_dirs,
                table=self.SEQUENCE_TABLE,
                method_controller=self.method_controller,
                offline=offline,
            )
        elif not offline and (not method_dir or not sequence_dir or not data_dirs):
            raise ValueError(
                f"Expected a method dir: {method_dir}, sequence dir: {sequence_dir} and data dirs:{data_dirs} but one was None."
            )
        else:
            raise ValueError("Expected error occured, please try again.")

    def send(self, cmd: Union[Command, str]):
        """Sends any Command or string to Chemstation.

        :param cmd: the macro to send to Chemstation
        """
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode."
            )
        self.comm.send(cmd)

    def receive(self) -> None | Response | str:
        """Get the most recent response from Chemstation.

        :return: most recent response from the most recently sent MACRO that returned a response.
        """
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode."
            )
        res = self.comm.receive()
        if res.is_ok():
            return res.ok_value
        else:
            return res.err_value

    def status(self) -> Status:
        """Get the current status of the HPLC machine.

        :return: current status of the HPLC machine; Status types can be found in `pychemstation.utils.macro`
        """
        if not self.comm:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode."
            )
        return self.comm.get_status()

    def switch_method(self, method_name: str):
        """Allows the user to switch between pre-programmed methods. No need to append '.M'
        to the end of the method name. For example. for the method named 'General-Poroshell.M',
        only 'General-Poroshell' is needed.

        :param method_name: any available method in Chemstation method directory
        :raises  IndexError: Response did not have expected format. Try again.
        :raises  AssertionError: The desired method is not selected. Try again.
        """
        self.method_controller.switch(method_name)

    def switch_sequence(self, sequence_name: str):
        """Allows the user to switch between pre-programmed sequences. The sequence name does not need the '.S' extension.
         For example: for the method named 'mySeq.S', only 'mySeq' is needed.

        :param sequence_name: The name of the sequence file
        """
        self.sequence_controller.switch(sequence_name)

    def run_method(
        self,
        experiment_name: str,
        add_timestamp: bool = True,
        stall_while_running: bool = True,
    ):
        """This is the preferred method to trigger a run.
        Starts the currently selected method, storing data
        under the <data_dir>/<experiment_name>.D folder.
        Device must be ready.

        :param experiment_name: Name of the experiment
        :param stall_while_running: whether to return or stall while HPLC runs.
        :param add_timestamp: whether to append a timestamp in '%Y-%m-%d-%H-%M' format to end of experiment name.
        """
        self.method_controller.run(
            experiment_name=experiment_name,
            stall_while_running=stall_while_running,
            add_timestamp=add_timestamp,
        )

    def stop_method(self):
        """Stops the current running method, manual intervention may be needed."""
        self.method_controller.stop()

    def run_sequence(self, stall_while_running: bool = True):
        """Starts the currently loaded sequence, storing data
        under one of the data_dirs/<sequence table name> folder.
        Device must be ready.

        :param stall_while_running: whether to return or stall while HPLC runs.
        """
        self.sequence_controller.run(stall_while_running=stall_while_running)

    def check_method_complete(self) -> Tuple[float, int]:
        """Check if the currently running method (if any) is done.

        :returns: the percent of the method run completed, and whether the run is complete.
        """
        return self.method_controller.check_hplc_run_finished()

    def check_sequence_complete(self) -> Tuple[float, int]:
        """Check if the currently running sequence (if any) is done.

        :return: the percent of the sequence run completed, and whether the run is complete.
        """
        return self.sequence_controller.check_hplc_run_finished()

    def edit_method(self, updated_method: MethodDetails, save: bool = False):
        """Updated the currently loaded method in ChemStation with provided values.

        :param updated_method: the method with updated values, to be sent to Chemstation to modify the currently loaded method.
        :param save: whether this method should be saved to disk, or just modified.
        """
        self.method_controller.edit(updated_method, save)

    def edit_sequence(self, updated_sequence: SequenceTable):
        """Updates the currently loaded sequence table with the provided table, and saves the sequence.

        :param updated_sequence: The sequence table to be written to the currently loaded sequence table.
        """
        self.sequence_controller.edit(updated_sequence)

    def get_last_run_method_file_path(self) -> str:
        """Get the folder (ending with .D) for last run method.

        :return: Complete path for method run.
        """
        if len(self.method_controller.data_files) > 0:
            return self.method_controller.data_files[-1]
        else:
            raise UserWarning("No data yet!")

    def get_last_run_method_report(
        self,
        custom_path: Optional[str] = None,
        report_type: ReportType = ReportType.CSV,
    ) -> AgilentReport:
        """Return data contained in the REPORT files. Use `aghplctools` if you want more report processing utility.

        :param custom_path: path to sequence folder
        :param report_type: read either the TXT or CSV version
        :return: report data for method
        """
        return self.method_controller.get_report(
            custom_path=custom_path, report_type=report_type
        )[0]

    def get_last_run_method_data(
        self, read_uv: bool = False, custom_path: Optional[str] = None
    ) -> Dict[int, AgilentHPLCChromatogram] | AgilentChannelChromatogramData:
        """Returns the last run method data.

        :param custom_path: If you want to just load method data but from a file path. This file path must be the complete file path.
        :param read_uv: whether to also read the UV file
        """
        if read_uv:
            return self.method_controller.get_data_uv(custom_path=custom_path)
        else:
            return self.method_controller.get_data(custom_path=custom_path)

    def get_last_run_sequence_file_paths(self) -> SequenceDataFiles:
        """Get the sequence folder and all run folders (ending with .D).

        :return: `SequenceDataFiles` containing complete path locations for sequence folder and all runs.
        """
        if len(self.sequence_controller.data_files):
            self.sequence_controller._fuzzy_match_most_recent_folder(
                most_recent_folder=self.sequence_controller.data_files[-1],
            )
            return self.sequence_controller.data_files[-1]
        else:
            raise UserWarning("No data files yet!")

    def get_last_run_sequence_reports(
        self,
        custom_path: Optional[str] = None,
        report_type: ReportType = ReportType.CSV,
    ) -> List[AgilentReport]:
        """Return data contained in the REPORT files. Use `aghplctools` if you want more report processing utility.

        :param custom_path: path to sequence folder
        :param report_type: read either the TXT or CSV version
        :return: list of reports for each row
        """
        return self.sequence_controller.get_report(
            custom_path=custom_path, report_type=report_type
        )

    def get_last_run_sequence_data(
        self, read_uv: bool = False, custom_path: Optional[str] = None
    ) -> (
        List[Dict[int, AgilentHPLCChromatogram]] | List[AgilentChannelChromatogramData]
    ):
        """Returns data for all rows in the last run sequence data.

        :param custom_path: If you want to just load sequence data but from a file path. This file path must be the complete file path.
        :param read_uv: whether to also read the UV file
        """
        if read_uv:
            return self.sequence_controller.get_data_mult_uv(custom_path=custom_path)
        else:
            return self.sequence_controller.get_data(custom_path=custom_path)

    def check_loaded_sequence(self) -> str:
        """Returns the name of the currently loaded sequence."""
        return self.sequence_controller.get_current_sequence_name()

    def check_loaded_method(self) -> str:
        """Returns the name of the currently loaded method."""
        return self.method_controller.get_current_method_name()

    def load_method(self) -> MethodDetails:
        """Returns details of the currently loaded method, such as its starting modifier conditions and timetable."""
        return self.method_controller.load()

    def load_sequence(self) -> SequenceTable:
        """Returns the currently loaded sequence."""
        return self.sequence_controller.load()

    def load_injector_program(self) -> InjectorTable | None:
        return self.method_controller.injector.load()

    def load_sample_location(self):
        self.method_controller.get_location()

    def standby(self):
        """Switches all modules in standby mode. All lamps and pumps are switched off."""
        self.send(Command.STANDBY_CMD)

    def preprun(self):
        """Prepares all modules for run. All lamps and pumps are switched on."""
        self.send(Command.PREPRUN_CMD)

    def lamp_on(self):
        """Turns the UV lamp on."""
        self.method_controller.dad.turn_on()

    def lamp_off(self):
        """Turns the UV lamp off."""
        self.method_controller.dad.turn_off()

    def pump_on(self):
        """Turns on the pump on."""
        self.method_controller.pump.turn_on()

    def pump_off(self):
        """Turns the pump off."""
        self.method_controller.pump.turn_off()

    def instrument_off(self):
        """Shuts the entire instrument off, including pumps, lamps, thermostat."""
        self.send(Command.INSTRUMENT_OFF)

    def instrument_on(self):
        """Turns the entire instrument on, including pumps, lamps, thermostat."""
        self.send(Command.INSTRUMENT_ON)
