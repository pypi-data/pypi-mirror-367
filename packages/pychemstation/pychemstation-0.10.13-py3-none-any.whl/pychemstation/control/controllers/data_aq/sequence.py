from __future__ import annotations

import os
import time
import warnings
from typing import Any, Dict, List, Optional, Union, Tuple

from result import Err, Ok, Result
from typing_extensions import override

from pychemstation.analysis.chromatogram import (
    AgilentChannelChromatogramData,
    AgilentHPLCChromatogram,
    SEQUENCE_TIME_FORMAT,
)

from ....analysis.process_report import AgilentReport, ReportType
from ....control.controllers.comm import CommunicationController
from ....utils.abc_tables.run import RunController
from ....utils.macro import Command
from ....utils.sequence_types import (
    InjectionSource,
    SampleType,
    SequenceDataFiles,
    SequenceEntry,
    SequenceTable,
)
from ....utils.table_types import RegisterFlag, T, Table
from ....utils.tray_types import FiftyFourVialPlate, VialBar, Tray
from . import MethodController


class SequenceController(RunController):
    """
    Class containing sequence related logic
    """

    def __init__(
        self,
        controller: Optional[CommunicationController],
        method_controller: MethodController,
        src: Optional[str],
        data_dirs: Optional[List[str]],
        table: Table,
        offline: bool,
    ):
        self.method_controller = method_controller
        self.data_files: List[SequenceDataFiles] = []
        super().__init__(
            controller=controller,
            src=src,
            data_dirs=data_dirs,
            table=table,
            offline=offline,
        )

    def load(self) -> SequenceTable:
        rows = self.get_row_count_safely()
        self.send(Command.GET_SEQUENCE_CMD)
        seq_name = self.receive()

        if seq_name.is_ok():
            self.table_state: SequenceTable = SequenceTable(
                name=seq_name.ok_value.string_response.partition(".S")[0],
                rows=[self.get_row(r + 1) for r in range(int(rows))],
            )
            return self.table_state
        else:
            raise RuntimeError(
                f"couldn't read rows or sequence name: {seq_name.err_value}"
            )

    @staticmethod
    def try_int(val: Any) -> Optional[int]:
        try:
            return int(val)
        except ValueError:
            return None

    @staticmethod
    def try_float(val: Any) -> Optional[float]:
        try:
            return float(val)
        except ValueError:
            return None

    @staticmethod
    def try_vial_location(val: Any) -> Tray:
        try:
            return VialBar(val) if val <= 10 else FiftyFourVialPlate.from_int(num=val)
        except ValueError:
            raise ValueError("Expected vial location, is empty.")

    def get_row(self, row: int) -> SequenceEntry:
        sample_name = self.get_sample_name(row)
        vial_location = self.get_vial_location(row)
        data_file = self.get_data_file(row)
        method = self.get_method(row)
        num_inj = self.get_num_inj(row)
        inj_vol = self.get_inj_vol(row)
        inj_source = self.get_inj_source(row)
        sample_type = self.get_sample_type(row)
        return SequenceEntry(
            sample_name=sample_name,
            vial_location=vial_location,
            method=None if len(method) == 0 else method,
            num_inj=num_inj,
            inj_vol=inj_vol,
            inj_source=inj_source,
            sample_type=sample_type,
            data_file=data_file,
        )

    def get_sample_type(self, row):
        return SampleType(self.get_num(row, RegisterFlag.SAMPLE_TYPE))

    def get_inj_source(self, row):
        return InjectionSource(self.get_text(row, RegisterFlag.INJ_SOR))

    def get_inj_vol(self, row):
        return self.try_float(self.get_text(row, RegisterFlag.INJ_VOL))

    def get_num_inj(self, row):
        return self.try_int(self.get_num(row, RegisterFlag.NUM_INJ))

    def get_method(self, row):
        return self.get_text(row, RegisterFlag.METHOD)

    def get_data_file(self, row):
        return self.get_text(row, RegisterFlag.DATA_FILE)

    def get_vial_location(self, row) -> Tray:
        return self.try_vial_location(
            self.try_int(self.get_num(row, RegisterFlag.VIAL_LOCATION))
        )

    def get_sample_name(self, row):
        return self.get_text(row, RegisterFlag.NAME)

    def switch(self, seq_name: str):
        """
        Switch to the specified sequence. The sequence name does not need the '.S' extension.

        :param seq_name: The name of the sequence file
        """
        self.send(f'_SeqFile$ = "{seq_name}.S"')
        self.send(f'_SeqPath$ = "{self.src}"')
        self.send(Command.SWITCH_SEQUENCE_CMD)
        time.sleep(2)
        parsed_response = self.get_current_sequence_name()

        assert parsed_response == f"{seq_name}.S", "Switching sequence failed."

    def get_current_sequence_name(self):
        self.send(Command.GET_SEQUENCE_CMD)
        time.sleep(2)
        parsed_response = self.receive().ok_value.string_response
        return parsed_response

    def edit(self, sequence_table: SequenceTable):
        """
        Updates the currently loaded sequence table with the provided table. This method will delete the existing sequence table and remake it.
        If you would only like to edit a single row of a sequence table, use `edit_sequence_table_row` instead.

        :param sequence_table:
        """
        self.table_state = sequence_table
        rows = self.get_row_count_safely()
        existing_row_num = rows
        wanted_row_num = len(sequence_table.rows)
        for i in range(int(existing_row_num)):
            self.delete_row(int(existing_row_num - i))
            self.send(Command.SAVE_SEQUENCE_CMD)
        for i in range(int(wanted_row_num)):
            self.add_row()
            self.download()
        self.send(Command.SWITCH_SEQUENCE_CMD)
        for i, row in enumerate(sequence_table.rows):
            self._edit_row(row=row, row_num=i + 1)
            self.sleep(1)
        self.download()
        self.send(Command.SWITCH_SEQUENCE_CMD)

    def _edit_row(self, row: SequenceEntry, row_num: int):
        """
        Edits a row in the sequence table. If a row does NOT exist, a new one will be created.

        :param row: sequence row entry with updated information
        :param row_num: the row to edit, based on 1-based indexing
        """
        num_rows = self.get_row_count_safely()
        while num_rows < row_num:
            self.add_row()
            self.download()
            num_rows = self.get_row_count_safely()
        if row.vial_location:
            self.edit_vial_location(row.vial_location, row_num, save=False)
        if row.method:
            self.edit_method_name(row.method, row_num, save=False)
        if row.num_inj:
            self.edit_num_injections(row.num_inj, row_num, save=False)
        if row.inj_vol:
            self.edit_injection_volume(row.inj_vol, row_num, save=False)
        if row.inj_source:
            self.edit_injection_source(row.inj_source, row_num, save=False)
        if row.sample_name:
            self.edit_sample_name(row.sample_name, row_num, save=False)
        if row.data_file:
            self.edit_data_file(row.data_file, row_num, save=False)
        if row.sample_type:
            self.edit_sample_type(row.sample_type, row_num, save=False)
        self.download()

    def edit_sample_type(
        self, sample_type: SampleType, row_num: int, save: bool = True
    ):
        if not isinstance(sample_type, SampleType):
            raise ValueError("`sample_type` should be of type `SampleType`")
        self._edit_row_num(
            row=row_num,
            col_name=RegisterFlag.SAMPLE_TYPE,
            val=sample_type.value,
        )
        if save:
            self.download()

    def edit_data_file(self, data_file: str, row_num: int, save: bool = True):
        self._edit_row_text(row=row_num, col_name=RegisterFlag.DATA_FILE, val=data_file)
        if save:
            self.download()

    def edit_sample_name(self, sample_name: str, row_num: int, save: bool = True):
        self._edit_row_text(row=row_num, col_name=RegisterFlag.NAME, val=sample_name)
        if save:
            self.download()

    def edit_injection_source(
        self, inj_source: InjectionSource, row_num: int, save: bool = True
    ):
        if not isinstance(inj_source, InjectionSource):
            raise ValueError("`inj_source` should be of type `InjectionSource`")
        self._edit_row_text(
            row=row_num, col_name=RegisterFlag.INJ_SOR, val=inj_source.value
        )
        if save:
            self.download()

    def edit_injection_volume(
        self, inj_vol: Union[int, float], row_num: int, save: bool = True
    ):
        self._edit_row_text(
            row=row_num, col_name=RegisterFlag.INJ_VOL, val=str(inj_vol)
        )
        if save:
            self.download()

    def edit_num_injections(self, num_inj: int, row_num: int, save: bool = True):
        self._edit_row_num(row=row_num, col_name=RegisterFlag.NUM_INJ, val=num_inj)
        if save:
            self.download()

    def edit_method_name(
        self, method: str, row_num: int, save: bool = True, override_check: bool = False
    ):
        method_dir = self.method_controller.src
        possible_path = os.path.join(method_dir, method) + ".M\\"
        if os.path.exists(possible_path):
            method = os.path.join(method_dir, method)
        elif not override_check:
            raise ValueError(
                "Method may not exist. If you would still like to use this method, set the `override_check` flag to `True`"
            )
        self._edit_row_text(row=row_num, col_name=RegisterFlag.METHOD, val=method)
        if save:
            self.download()

    def edit_vial_location(self, loc: Tray, row_num: int, save: bool = True):
        loc_num = -1
        try:
            previous_contents = self.get_row(row_num)
            if (
                isinstance(loc, VialBar)
                and isinstance(previous_contents.vial_location, VialBar)
                or isinstance(loc, FiftyFourVialPlate)
                and isinstance(previous_contents.vial_location, FiftyFourVialPlate)
            ):
                if isinstance(loc, VialBar):
                    loc_num = loc.value
                elif isinstance(loc, FiftyFourVialPlate):
                    loc_num = loc.value()
                self._edit_row_num(
                    row=row_num, col_name=RegisterFlag.VIAL_LOCATION, val=loc_num
                )
            elif isinstance(loc, VialBar) or isinstance(loc, FiftyFourVialPlate):
                self.add_row()
                previous_contents.vial_location = loc
                num_rows = self.get_row_count_safely()
                self._edit_row(previous_contents, num_rows)
                self.move_row(int(num_rows), row_num)
                self.delete_row(row_num + 1)
                self.download()
            else:
                raise ValueError(
                    "`loc` should be of type `VialBar`, `FiftyFourVialPlate`"
                )
        except Exception:
            if not (isinstance(loc, VialBar) or isinstance(loc, FiftyFourVialPlate)):
                raise ValueError(
                    "`loc` should be of type `VialBar`, `FiftyFourVialPlate`"
                )
            if isinstance(loc, VialBar):
                loc_num = loc.value
            elif isinstance(loc, FiftyFourVialPlate):
                loc_num = loc.value()
            self._edit_row_num(
                row=row_num, col_name=RegisterFlag.VIAL_LOCATION, val=loc_num
            )
        if save:
            self.download()

    def download(self):
        self.send(Command.SAVE_SEQUENCE_CMD)

    def run(self, stall_while_running: bool = True):
        """
        Starts the currently loaded sequence, storing data
        under the <data_dir>/<sequence table name> folder.
        Device must be ready.
        """

        current_sequence_name = self.get_current_sequence_name()
        if not self.table_state or self.table_state.name not in current_sequence_name:
            self.table_state = self.load()

        total_runtime = 0.0
        for entry in self.table_state.rows:
            curr_method_runtime = self.method_controller.get_total_runtime()
            loaded_method = self.method_controller.get_method_name().removesuffix(".M")
            if entry.method:
                method_path = entry.method.split(sep="\\")
                method_name = method_path[-1]
                if loaded_method != method_name:
                    method_dir = (
                        "\\".join(method_path[:-1]) + "\\"
                        if len(method_path) > 1
                        else None
                    )
                    self.method_controller.switch(
                        method_name=method_name, alt_method_dir=method_dir
                    )
                    curr_method_runtime = self.method_controller.get_total_runtime()
            total_runtime += curr_method_runtime

        timestamp = time.strftime(SEQUENCE_TIME_FORMAT)
        folder_name = f"{self.table_state.name} {timestamp}"

        self.send(Command.SAVE_METHOD_CMD)
        self.send(Command.SAVE_SEQUENCE_CMD)
        self.send(Command.RUN_SEQUENCE_CMD.value)
        self.timeout = total_runtime * 60

        tries = 10
        hplc_running = False
        for _ in range(tries):
            hplc_running = self.check_hplc_is_running()
            if hplc_running:
                break
            else:
                self.send(Command.RUN_SEQUENCE_CMD.value)

        if hplc_running:
            full_path_name, current_sample_file = self.try_getting_run_info(folder_name)
            if full_path_name and current_sample_file:
                data_file = SequenceDataFiles(
                    sequence_name=self.table_state.name,
                    dir=full_path_name,
                    child_dirs=[os.path.join(full_path_name, current_sample_file)],
                )
                self.data_files.append(data_file)
            else:
                raise ValueError("Data directory for sequence was not found.")

            if stall_while_running:
                run_completed = self.check_hplc_done_running()
                if run_completed.is_ok():
                    self.data_files[-1] = run_completed.ok_value
                else:
                    warnings.warn(run_completed.err_value)
        else:
            raise RuntimeError("Sequence run may not have started.")

    def try_getting_run_info(self, folder_name: str) -> Tuple[str, str | None]:
        full_path_name, current_sample_file = None, None
        for _ in range(5):
            try:
                full_path_name, current_sample_file = (
                    self.get_current_run_data_dir_file()
                )
            except ValueError:
                pass
            if current_sample_file and full_path_name:
                return full_path_name, current_sample_file
            elif full_path_name:
                return full_path_name, None
        raise ValueError("Could not get sequence data folder")

    @override
    def _fuzzy_match_most_recent_folder(
        self, most_recent_folder: T
    ) -> Result[SequenceDataFiles, str]:
        if isinstance(most_recent_folder, SequenceDataFiles):
            try:
                if most_recent_folder.dir and os.path.isdir(most_recent_folder.dir):
                    subdirs = [x[0] for x in os.walk(most_recent_folder.dir)]
                    most_recent_folder.child_dirs = [
                        f
                        for f in subdirs
                        if most_recent_folder.dir in f and ".D" in f and f[-1] == "D"
                    ]
                    return Ok(most_recent_folder)
                else:
                    return Err("No sequence folder found, please give the full path.")
            except Exception as e:
                error = f"Failed to get sequence folder: {e}"
                return Err(error)
        return Err("Expected SequenceDataFile type.")

    def get_data_mult_uv(self, custom_path: Optional[str] = None):
        seq_data_dir = (
            SequenceDataFiles(dir=custom_path, sequence_name="")
            if custom_path
            else self.data_files[-1]
        )
        search_folder = self._fuzzy_match_most_recent_folder(seq_data_dir)
        if search_folder.is_ok():
            seq_data_dir = search_folder.ok_value
        else:
            raise FileNotFoundError(search_folder.err_value)
        all_w_spectra: List[Dict[int, AgilentHPLCChromatogram]] = []
        for row in seq_data_dir.child_dirs:
            all_w_spectra.append(self.get_data_uv(custom_path=row))
        return all_w_spectra

    def get_data_uv(
        self, custom_path: Optional[str] = None
    ) -> Dict[int, AgilentHPLCChromatogram]:
        if isinstance(custom_path, str):
            self.get_uv_spectrum(custom_path)
            return self.uv
        raise ValueError(
            "Path should exist when calling from sequence. Provide a child path (contains the method)."
        )

    def get_data(
        self, custom_path: Optional[str] = None
    ) -> List[AgilentChannelChromatogramData]:
        print(custom_path)
        if custom_path:
            self.data_files.append(
               SequenceDataFiles(dir=custom_path, sequence_name="") 
            )
        seq_file_dir = self.data_files[-1]
        possible_seq_file_name = self._fuzzy_match_most_recent_folder(
            seq_file_dir
        )
        if possible_seq_file_name.is_ok():
            self.data_files[-1] = possible_seq_file_name.ok_value
        else:
            raise UserWarning(f"{possible_seq_file_name.err_value}")
        spectra: List[AgilentChannelChromatogramData] = []
        for row in self.data_files[-1].child_dirs:
            self.get_spectrum_at_channels(row)
            spectra.append(AgilentChannelChromatogramData.from_dict(self.spectra))
        return spectra

    def get_report(
        self,
        custom_path: Optional[str] = None,
        report_type: ReportType = ReportType.TXT,
    ) -> List[AgilentReport]:
        if custom_path:
            self.data_files.append(
                self._fuzzy_match_most_recent_folder(
                    most_recent_folder=SequenceDataFiles(
                        dir=custom_path,
                        sequence_name="NA",
                    ),
                ).ok_value
            )
        parent_dir = self.data_files[-1]
        parent_dir = self._fuzzy_match_most_recent_folder(
            most_recent_folder=parent_dir,
        ).ok_value
        assert len(parent_dir.child_dirs) != 0
        spectra = self.get_data()
        reports = []
        for i, child_dir in enumerate(parent_dir.child_dirs):
            metd_report = self.get_report_details(child_dir, report_type)
            child_spectra: List[AgilentHPLCChromatogram] = list(
                spectra[i].__dict__.values()
            )
            for j, signal in enumerate(metd_report.signals):
                assert len(metd_report.signals) <= len(child_spectra)
                try:
                    possible_data = child_spectra[j]
                    if len(possible_data.x) > 0:
                        signal.data = possible_data
                except IndexError:
                    raise ValueError(j)
            reports.append(metd_report)
        return reports
