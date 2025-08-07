"""
Abstract module containing shared logic for Method and Sequence tables.

Authors: Lucy Hao
"""

from __future__ import annotations

import abc
import math
import os
import time
import warnings
from typing import Dict, List, Optional, Tuple, Union, Set

import polling
import rainbow as rb
from result import Err, Ok, Result

from ..macro import HPLCRunningStatus, Command
from ..method_types import MethodDetails
from ..sequence_types import SequenceTable
from ..table_types import Table, T
from ...analysis.chromatogram import (
    AgilentChannelChromatogramData,
    AgilentHPLCChromatogram,
)

from .table import ABCTableController
from ...analysis.process_report import (
    ReportType,
    AgilentReport,
    CSVProcessor,
    TXTProcessor,
)
from ...control.controllers import CommunicationController

TableType = Union[MethodDetails, SequenceTable]


class RunController(ABCTableController, abc.ABC):
    """Abstract controller for all tables that can trigger runs on Chemstation.

    :param controller: the controller for sending MACROs, must be initialized for a run to be triggered.
    :param src: complete directory path where files containing run parameters are stored.
    :param data_dirs: list of complete directories that Chemstation will write data to.
    :param table: contains register keys for accessing table in Chemstation.
    :param offline: whether the communication controller is online.
    """

    def __init__(
        self,
        controller: Optional[CommunicationController],
        src: Optional[str],
        data_dirs: Optional[List[str]],
        table: Table,
        offline: bool = False,
    ):
        super().__init__(controller=controller, table=table)
        self.table_state: Optional[TableType] = None
        self.curr_run_starting_time: Optional[float] = None
        self.timeout: Optional[float] = None
        self.current_run_child_files: Set[str] = set()

        if not offline:
            if src and not os.path.isdir(src):
                raise FileNotFoundError(f"dir: {src} not found.")
            if data_dirs:
                for d in data_dirs:
                    if not os.path.isdir(d):
                        raise FileNotFoundError(f"dir: {d} not found.")
                    if r"\\" in d:
                        raise ValueError("Data directories should not be raw strings!")
            if src and data_dirs:
                self.src: str = src
                self.data_dirs: List[str] = data_dirs

        self.spectra: dict[str, AgilentHPLCChromatogram] = {
            "A": AgilentHPLCChromatogram(),
            "B": AgilentHPLCChromatogram(),
            "C": AgilentHPLCChromatogram(),
            "D": AgilentHPLCChromatogram(),
            "E": AgilentHPLCChromatogram(),
            "F": AgilentHPLCChromatogram(),
            "G": AgilentHPLCChromatogram(),
            "H": AgilentHPLCChromatogram(),
        }
        self.uv: Dict[int, AgilentHPLCChromatogram] = {}
        self.data_files: List = []

    def __new__(cls, *args, **kwargs):
        if cls is RunController:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    @abc.abstractmethod
    def _fuzzy_match_most_recent_folder(self, most_recent_folder: T) -> Result[T, str]:
        pass

    @abc.abstractmethod
    def get_data(
        self, custom_path: Optional[str] = None
    ) -> Union[List[AgilentChannelChromatogramData], AgilentChannelChromatogramData]:
        pass

    @abc.abstractmethod
    def get_data_uv(
        self, custom_path: str | None = None
    ) -> Dict[int, AgilentHPLCChromatogram]:
        pass

    @abc.abstractmethod
    def get_report(
        self, custom_path: str, report_type: ReportType = ReportType.TXT
    ) -> List[AgilentReport]:
        pass

    def check_hplc_is_running(self) -> bool:
        if self.controller:
            try:
                started_running = polling.poll(
                    lambda: isinstance(self.controller.get_status(), HPLCRunningStatus),
                    step=1,
                    max_tries=20,
                )
            except Exception as e:
                print(e)
                return False
            if started_running:
                self.curr_run_starting_time = time.time()
            return started_running
        else:
            raise ValueError("Controller is offline")

    def check_hplc_run_finished(self) -> Tuple[float, bool]:
        if self.controller:
            try:
                _, current_run_file = self.get_current_run_data_dir_file()
                sample_file, extension, _ = current_run_file.partition(".D")
                self.current_run_child_files.add(sample_file)
            except Exception:
                pass
            done_running = self.controller.check_if_not_running()
            if self.curr_run_starting_time and self.timeout:
                time_passed = time.time() - self.curr_run_starting_time
                if time_passed > self.timeout:
                    enough_time_passed = time_passed >= self.timeout
                    run_finished = enough_time_passed and done_running
                    if run_finished:
                        self._reset_time()
                        return 0, run_finished
                else:
                    time_left = self.timeout - time_passed
                    return time_left, self.controller.check_if_not_running()
            return 0, self.controller.check_if_not_running()
        raise ValueError("Controller is offline!")

    def check_hplc_done_running(self) -> Ok[T] | Err[str]:
        """Checks if ChemStation has finished running and can read data back

        :return: Data file object containing most recent run file information.
        """
        self.current_run_child_files = set()
        if self.timeout is not None:
            finished_run = False
            minutes = math.ceil(self.timeout / 60)
            try:
                finished_run = not polling.poll(
                    lambda: self.check_hplc_run_finished()[1],
                    max_tries=minutes - 1,
                    step=50,
                )
            except (
                polling.TimeoutException,
                polling.PollingException,
                polling.MaxCallException,
            ):
                try:
                    finished_run = polling.poll(
                        lambda: self.check_hplc_run_finished()[1],
                        timeout=self.timeout / 2,
                        step=1,
                    )
                except (
                    polling.TimeoutException,
                    polling.PollingException,
                    polling.MaxCallException,
                ):
                    pass
        else:
            raise ValueError("Timeout value is None, no comparison can be made.")

        check_folder = self._fuzzy_match_most_recent_folder(self.data_files[-1])
        if check_folder.is_ok() and finished_run:
            return check_folder
        elif check_folder.is_ok():
            try:
                finished_run = polling.poll(
                    lambda: self.check_hplc_run_finished()[1], max_tries=10, step=50
                )
                if finished_run:
                    return check_folder
            except Exception:
                self._reset_time()
                return self.data_files[-1]
        return Err("Run not may not have completed.")

    def get_uv_spectrum(self, path: str):
        data_uv = rb.agilent.chemstation.parse_file(os.path.join(path, "DAD1.UV"))
        times = data_uv.xlabels
        wavelengths = data_uv.ylabels
        absorbances = data_uv.data.transpose()
        for i, w in enumerate(wavelengths):
            self.uv[w] = AgilentHPLCChromatogram()
            self.uv[w].attach_spectrum(times, absorbances[i])

    def get_report_details(
        self, path: str, report_type: ReportType = ReportType.TXT
    ) -> AgilentReport:
        if report_type is ReportType.TXT:
            txt_report = TXTProcessor(path).process_report()
            if txt_report.is_ok():
                return txt_report.ok_value
            elif txt_report.is_err():
                raise ValueError(txt_report.err_value)
        if report_type is ReportType.CSV:
            csv_report = CSVProcessor(path).process_report()
            if csv_report.is_ok():
                return csv_report.ok_value
            elif csv_report.is_err():
                raise ValueError(csv_report.err_value)
        raise ValueError("Expected one of ReportType.TXT or ReportType.CSV")

    def get_spectrum_at_channels(self, data_path: str):
        """Load chromatogram for any channel in spectra dictionary."""
        for channel, spec in self.spectra.items():
            try:
                spec.load_spectrum(data_path=data_path, channel=channel)
            except FileNotFoundError:
                self.spectra[channel] = AgilentHPLCChromatogram()
                warning = f"No data at channel: {channel}"
                warnings.warn(warning)

    def _reset_time(self):
        self.curr_run_starting_time = None
        self.timeout = None

    def get_current_run_data_dir_file(self) -> Tuple[str, str]:
        self.send(Command.GET_CURRENT_RUN_DATA_DIR)
        full_path_name = self.receive()
        self.send(Command.GET_CURRENT_RUN_DATA_FILE)
        current_sample_file = self.receive()
        if full_path_name.is_ok() and current_sample_file.is_ok():
            if os.path.isdir(full_path_name.ok_value.string_response) and os.path.isdir(
                os.path.join(
                    full_path_name.ok_value.string_response,
                    current_sample_file.ok_value.string_response,
                )
            ):
                return (
                    full_path_name.ok_value.string_response,
                    current_sample_file.ok_value.string_response,
                )
        raise ValueError("Couldn't read data dir and file or doesn't exist yet.")
