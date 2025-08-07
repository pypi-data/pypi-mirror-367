from __future__ import annotations

import os
import time
import warnings
from typing import Dict, List, Optional, Union, Tuple

from result import Err, Result, Ok

from ..devices.column import ColumnController
from ..devices.dad import DADController
from ..devices.pump import PumpController
from ..devices.sample_info import SampleInfo
from ....analysis.chromatogram import (
    TIME_FORMAT,
    AgilentHPLCChromatogram,
    AgilentChannelChromatogramData,
)

from ....analysis.process_report import AgilentReport, ReportType
from ....control.controllers import CommunicationController
from ....utils.abc_tables.run import RunController
from ....utils.macro import Command
from ....utils.method_types import (
    HPLCMethodParams,
    MethodDetails,
    TimeTableEntry,
    Param,
    PType,
)
from ....utils.table_types import RegisterFlag, T, Table
from ..devices.injector import InjectorController
from ....utils.tray_types import Tray


class MethodController(RunController):
    """Class containing method related logic."""

    def __init__(
        self,
        controller: Optional[CommunicationController],
        src: Optional[str],
        data_dirs: Optional[List[str]],
        table: Table,
        offline: bool,
        injector: InjectorController,
        pump: PumpController,
        dad: DADController,
        column: ColumnController,
        sample_info: SampleInfo,
    ):
        self.injector = injector
        self.pump = pump
        self.dad = dad
        self.column = column
        self.sample_info = sample_info
        self.data_files: List[str] = []
        super().__init__(
            controller=controller,
            src=src,
            data_dirs=data_dirs,
            table=table,
            offline=offline,
        )

    def get_sample_location(self) -> Tray:
        return self.sample_info.get_location()

    def get_current_method_name(self) -> str:
        self.sleepy_send(Command.GET_METHOD_CMD)
        res = self.receive()
        if res.is_ok():
            return res.ok_value.string_response
        return "ERROR"

    def get_method_params(self) -> HPLCMethodParams:
        if self.controller:
            return HPLCMethodParams(
                organic_modifier=self.get_om(),
                flow=self.get_flow(),
            )
        raise ValueError("Communication controller is offline!")

    def get_row(self, row: int) -> TimeTableEntry:
        function = self.get_text(row, RegisterFlag.FUNCTION)
        if function == RegisterFlag.FLOW.value:
            return TimeTableEntry(
                start_time=self.get_num(row, RegisterFlag.TIME),
                organic_modifer=None,
                flow=self.get_num(row, RegisterFlag.TIMETABLE_FLOW),
            )
        if function == RegisterFlag.SOLVENT_COMPOSITION.value:
            return TimeTableEntry(
                start_time=self.get_num(row, RegisterFlag.TIME),
                organic_modifer=self.get_num(
                    row, RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION
                ),
                flow=None,
            )
        raise ValueError("Both flow and organic modifier are empty")

    def get_timetable(self, rows: int):
        uncoalesced_timetable_rows = [self.get_row(r + 1) for r in range(rows)]
        timetable_rows: Dict[str, TimeTableEntry] = {}
        for row in uncoalesced_timetable_rows:
            time_key = str(row.start_time)
            if time_key not in timetable_rows.keys():
                timetable_rows[time_key] = TimeTableEntry(
                    start_time=row.start_time,
                    flow=row.flow,
                    organic_modifer=row.organic_modifer,
                )
            else:
                if row.flow:
                    timetable_rows[time_key].flow = row.flow
                if row.organic_modifer:
                    timetable_rows[time_key].organic_modifer = row.organic_modifer
        entries = list(timetable_rows.values())
        entries.sort(key=lambda e: e.start_time)
        return entries

    def load(self) -> MethodDetails:
        rows = self.get_row_count_safely()
        method_name = self.get_method_name()
        timetable_rows = self.get_timetable(rows)
        params = self.get_method_params()
        stop_time = self.get_stop_time()
        post_time = self.get_post_time()
        self.table_state = MethodDetails(
            name=method_name,
            timetable=timetable_rows,
            stop_time=stop_time,
            post_time=post_time,
            params=params,
        )
        return self.table_state

    def get_method_name(self):
        self.send(Command.GET_METHOD_CMD)
        res = self.receive()
        method_name = res.ok_value.string_response
        return method_name

    def get_total_runtime(self) -> Union[int, float]:
        """Returns total method runtime in minutes."""
        return self.get_post_time() + self.get_stop_time()

    def current_method(self, method_name: str):
        """
        Checks if a given method is already loaded into Chemstation. Method name does not need the ".M" extension.

        :param method_name: a Chemstation method
        :return: True if method is already loaded
        """
        self.send(Command.GET_METHOD_CMD)
        parsed_response = self.receive()
        return method_name in parsed_response

    def switch(self, method_name: str, alt_method_dir: Optional[str] = None):
        """
        Allows the user to switch between pre-programmed methods. No need to append '.M'
        to the end of the method name. For example. for the method named 'General-Poroshell.M',
        only 'General-Poroshell' is needed.

        :param method_name: any available method in Chemstation method directory
        :param alt_method_dir: directory where the method resides
        :raise IndexError: Response did not have expected format. Try again.
        :raise AssertionError: The desired method is not selected. Try again.
        """
        method_dir = self.src if not alt_method_dir else alt_method_dir
        self.send(
            Command.SWITCH_METHOD_CMD_SPECIFIC.value.format(
                method_dir=method_dir, method_name=method_name
            )
        )
        time.sleep(2)
        self.send(Command.GET_METHOD_CMD)
        time.sleep(2)
        res = self.receive()
        if res.is_ok():
            parsed_response = res.ok_value.string_response
            assert parsed_response == f"{method_name}.M", "Switching Methods failed."
        self.table_state = None

    def edit(self, updated_method: MethodDetails, save: bool):
        """Updated the currently loaded method in ChemStation with provided values.

        :param updated_method: the method with updated values, to be sent to Chemstation to modify the currently loaded method.
        :param save: if false only modifies the method, otherwise saves to disk
        """
        self.table_state = updated_method
        # Method settings required for all runs
        self.update_method_params(
            new_flow=updated_method.params.flow,
            new_initial_om=updated_method.params.organic_modifier,
            new_stop_time=updated_method.stop_time,
            new_post_time=updated_method.post_time,
        )
        self.validate_timetable(updated_method.timetable)
        self.edit_method_timetable(updated_method.timetable)

        if save:
            self.save_method()

    def save_method(self):
        self.send(
            Command.SAVE_METHOD_CMD.value.format(
                commit_msg=f"saved method at {str(time.time())}"
            )
        )

    def _validate_organic_modifier(self, new_om):
        if not (isinstance(new_om, int) or isinstance(new_om, float)):
            raise ValueError("Organic modifier must be int or float")
        if new_om < 0:
            raise ValueError("Organic modifier must be positive")
        if new_om > 100:
            raise ValueError("Organic modifer must be less than 100.")

    def _validate_flow(self, new_flow):
        if not (isinstance(new_flow, int) or isinstance(new_flow, float)):
            raise ValueError("Flow must be int or float")
        if new_flow < 0:
            raise ValueError("Flow must be positive")
        if new_flow >= 5.0:
            raise ValueError("Flow must be less than 5.0")

    def validate_stop_time(self, new_stop_time):
        if not (isinstance(new_stop_time, int) or isinstance(new_stop_time, float)):
            raise ValueError("Stop time must be int or float")
        if new_stop_time < 0:
            raise ValueError("Stop time must be positive")

    def validate_post_time(self, new_post_time):
        if not (isinstance(new_post_time, int) or isinstance(new_post_time, float)):
            raise ValueError("Post time must be int or float")
        if new_post_time < 0:
            raise ValueError("Post time must be positive")

    def update_method_params(
        self,
        new_flow: Union[int, float],
        new_initial_om: Union[int, float],
        new_stop_time: Union[int, float] | None,
        new_post_time: Union[int, float] | None,
    ):
        self.delete_table()
        self._validate_flow(new_flow)
        self.validate_post_time(new_post_time)
        self._validate_organic_modifier(new_initial_om)
        self.validate_stop_time(new_stop_time)
        self.edit_flow(new_flow)
        self.edit_initial_om(new_initial_om)
        self.edit_stop_time(new_stop_time)
        self.edit_post_time(new_post_time)

    def download(self):
        self.sleepy_send("DownloadRCMethod PMP1")

    def _edit_row(
        self,
        row: TimeTableEntry,
        first_row: bool,
        time_added: bool,
        flow_added: bool,
        om_added: bool,
        function_added: bool,
    ) -> Tuple[bool, bool, bool, bool]:
        def add_time():
            nonlocal time_added
            nonlocal first_row
            if not time_added:
                self.add_new_col_num(col_name=RegisterFlag.TIME, val=row.start_time)
                time_added = True
            elif not first_row:
                self._edit_row_num(col_name=RegisterFlag.TIME, val=row.start_time)

        def add_flow():
            nonlocal flow_added
            nonlocal function_added
            if not flow_added:
                if not function_added:
                    self.add_new_col_text(
                        col_name=RegisterFlag.FUNCTION,
                        val=RegisterFlag.FLOW.value,
                    )
                    function_added = True
                else:
                    self._edit_row_text(
                        col_name=RegisterFlag.FUNCTION,
                        val=RegisterFlag.FLOW.value,
                    )
                self.add_new_col_num(
                    col_name=RegisterFlag.TIMETABLE_FLOW,
                    val=row.flow,
                )
                flow_added = True
            else:
                self._edit_row_text(
                    col_name=RegisterFlag.FUNCTION, val=RegisterFlag.FLOW.value
                )
                self._edit_row_num(col_name=RegisterFlag.TIMETABLE_FLOW, val=row.flow)

        def add_om():
            nonlocal om_added
            nonlocal function_added
            if not om_added:
                if not function_added:
                    self.add_new_col_text(
                        col_name=RegisterFlag.FUNCTION,
                        val=RegisterFlag.SOLVENT_COMPOSITION.value,
                    )
                    function_added = True
                else:
                    self._edit_row_text(
                        col_name=RegisterFlag.FUNCTION,
                        val=RegisterFlag.SOLVENT_COMPOSITION.value,
                    )
                self.add_new_col_num(
                    col_name=RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION,
                    val=row.organic_modifer,
                )
                om_added = True
            else:
                self._edit_row_text(
                    col_name=RegisterFlag.FUNCTION,
                    val=RegisterFlag.SOLVENT_COMPOSITION.value,
                )
                self._edit_row_num(
                    col_name=RegisterFlag.TIMETABLE_SOLVENT_B_COMPOSITION,
                    val=row.organic_modifer,
                )

        if row.organic_modifer:
            self.add_row()
            add_om()
            add_time()
        if row.flow:
            self.add_row()
            add_flow()
            add_time()
        self.download()
        return time_added, flow_added, om_added, function_added

    def edit_method_timetable(self, timetable_rows: List[TimeTableEntry]):
        self.get_num_rows()
        self.delete_table()
        res = self.get_num_rows()
        while not res.is_err():
            self.delete_table()
            res = self.get_num_rows()

        self.new_table()
        num_rows = self.get_row_count_safely()
        if num_rows != 0:
            raise ValueError("Should be zero rows!")

        time_added = False
        flow_added = False
        om_added = False
        function_added = False
        for i, row in enumerate(timetable_rows):
            time_added, flow_added, om_added, function_added = self._edit_row(
                row=row,
                first_row=i == 0,
                time_added=time_added,
                flow_added=flow_added,
                om_added=om_added,
                function_added=function_added,
            )

    def stop(self):
        """
        Stops the method run. A dialog window will pop up and manual intervention may be required.
        """
        self.send(Command.STOP_METHOD_CMD)

    def run(
        self,
        experiment_name: str,
        add_timestamp: bool = True,
        stall_while_running: bool = True,
    ):
        """
        :param experiment_name: Name of the experiment
        :param stall_while_running: whether to stall or immediately return
        :param add_timestamp: if should add timestamp to experiment name
        """
        hplc_is_running = False
        tries = 0
        while tries < 10 and not hplc_is_running:
            timestamp = time.strftime(TIME_FORMAT)
            self.send(
                Command.RUN_METHOD_CMD.value.format(
                    data_dir=self.data_dirs[0],
                    experiment_name=f"{experiment_name}_{timestamp}"
                    if add_timestamp
                    else experiment_name,
                )
            )

            hplc_is_running = self.check_hplc_is_running()
            tries += 1

        data_dir, data_file = self.get_current_run_data_dir_file()
        if not hplc_is_running:
            raise RuntimeError("Method failed to start.")

        self.data_files.append(os.path.join(os.path.normpath(data_dir), data_file))
        self.timeout = (self.get_total_runtime()) * 60

        if stall_while_running:
            run_completed = self.check_hplc_done_running()
            if run_completed.is_ok():
                self.data_files[-1] = run_completed.ok_value
            else:
                warnings.warn(run_completed.err_value)
        else:
            folder = self._fuzzy_match_most_recent_folder(self.data_files[-1])
            i = 0
            while folder.is_err() and i < 10:
                folder = self._fuzzy_match_most_recent_folder(self.data_files[-1])
                i += 1
            if folder.is_ok():
                self.data_files[-1] = folder.ok_value
            else:
                warning = f"Data folder {self.data_files[-1]} may not exist, returning and will check again after run is done."
                warnings.warn(warning)

    def _fuzzy_match_most_recent_folder(
        self, most_recent_folder: T
    ) -> Result[str, str]:
        if isinstance(most_recent_folder, str) or isinstance(most_recent_folder, bytes):
            if os.path.exists(most_recent_folder):
                return Ok(str(most_recent_folder))
            return Err("Folder not found!")
        raise ValueError("Folder is not a str or byte type.")

    def get_data(
        self, custom_path: Optional[str] = None
    ) -> AgilentChannelChromatogramData:
        custom_path = custom_path if custom_path else self.data_files[-1]
        self.get_spectrum_at_channels(custom_path)
        return AgilentChannelChromatogramData.from_dict(self.spectra)

    def get_data_uv(
        self, custom_path: Optional[str] = None
    ) -> dict[int, AgilentHPLCChromatogram]:
        custom_path = custom_path if custom_path else self.data_files[-1]
        self.get_uv_spectrum(custom_path)
        return self.uv

    def get_report(
        self,
        custom_path: Optional[str] = None,
        report_type: ReportType = ReportType.TXT,
    ) -> List[AgilentReport]:
        custom_path = self.data_files[-1] if not custom_path else custom_path
        metd_report = self.get_report_details(custom_path, report_type)
        chrom_data: List[AgilentHPLCChromatogram] = list(
            self.get_data(custom_path).__dict__.values()
        )
        for i, signal in enumerate(metd_report.signals):
            possible_data = chrom_data[i]
            if len(possible_data.x) > 0:
                signal.data = possible_data
        return [metd_report]

    def _validate_row(self, row: TimeTableEntry):
        if not (row.flow or row.organic_modifer):
            raise ValueError(
                "Require one of flow or organic modifier for the method timetable entry!"
            )
        if row.flow:
            self._validate_flow(row.flow)
        if row.organic_modifer:
            self._validate_organic_modifier(row.organic_modifer)

    def validate_timetable(self, timetable: List[TimeTableEntry]):
        start_time = 0.0
        for i, row in enumerate(timetable):
            if row.start_time > start_time:
                start_time = row.start_time
            elif row.start_time <= start_time:
                raise ValueError(
                    f"""Every row's start time must be larger than the previous start time. 
                    Row {i + 1} ({timetable[i].start_time}) has a smaller or equal starttime than row {i} ({start_time})"""
                )
            self._validate_row(row)

    def get_om(self):
        return self._read_num_param(RegisterFlag.SOLVENT_B_COMPOSITION)

    def get_flow(self):
        return self._read_num_param(RegisterFlag.FLOW)

    def get_post_time(self) -> Union[int, float]:
        return self._read_num_param(RegisterFlag.POST_TIME)

    def get_stop_time(self) -> Union[int, float]:
        return self._read_num_param(RegisterFlag.MAX_TIME)

    def edit_post_time(self, new_post_time: Optional[int | float]):
        if new_post_time:
            post_time: Param = Param(
                val=new_post_time,
                chemstation_key=RegisterFlag.POST_TIME,
                ptype=PType.NUM,
            )
            self._update_param(
                Param(
                    val="Set",
                    chemstation_key=RegisterFlag.POSTIME_MODE,
                    ptype=PType.STR,
                )
            )
            self._update_param(post_time)
        else:
            self._update_param(
                Param(
                    val="Off",
                    chemstation_key=RegisterFlag.POSTIME_MODE,
                    ptype=PType.STR,
                )
            )

    def edit_stop_time(self, new_stop_time: Optional[int | float]):
        if new_stop_time:
            stop_time: Param = Param(
                val=new_stop_time,
                chemstation_key=RegisterFlag.MAX_TIME,
                ptype=PType.NUM,
            )
            self._update_param(
                Param(
                    val="Set",
                    chemstation_key=RegisterFlag.STOPTIME_MODE,
                    ptype=PType.STR,
                )
            )
            self._update_param(stop_time)
        else:
            self._update_param(
                Param(
                    val="Off",
                    chemstation_key=RegisterFlag.STOPTIME_MODE,
                    ptype=PType.STR,
                )
            )

    def edit_flow(self, new_flow: Union[int, float]):
        flow: Param = Param(
            val=new_flow, chemstation_key=RegisterFlag.FLOW, ptype=PType.NUM
        )
        self._update_param(flow)

    def edit_initial_om(self, new_om: Union[int, float]):
        initial_organic_modifier: Param = Param(
            val=new_om,
            chemstation_key=RegisterFlag.SOLVENT_B_COMPOSITION,
            ptype=PType.NUM,
        )
        self._update_param(initial_organic_modifier)
