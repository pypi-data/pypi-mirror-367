"""Module for HPLC chromatogram data loading and manipulating"""

import os
import time
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


from ..utils.parsing import CHFile
from ..analysis.base_spectrum import AbstractSpectrum

ACQUISITION_PARAMETERS = "acq.txt"

# format used in acquisition parameters
TIME_FORMAT = "%Y-%m-%d %H-%M-%S"
SEQUENCE_TIME_FORMAT = "%Y-%m-%d %H-%M"


class AgilentHPLCChromatogram(AbstractSpectrum):
    """Class for HPLC spectrum (chromatogram) loading and handling."""

    AXIS_MAPPING = {"x": "min", "y": "mAu"}

    INTERNAL_PROPERTIES = {
        "baseline",
        "parameters",
        "data_path",
    }

    # set of properties to be saved
    PUBLIC_PROPERTIES = {
        "x",
        "y",
        "peaks",
        "timestamp",
    }

    def __init__(self, path=None, autosaving=False):
        if path is not None:
            os.makedirs(path, exist_ok=True)
            self.path = path
        else:
            self.path = os.path.join("../utils", "hplc_data")
            os.makedirs(self.path, exist_ok=True)

        super().__init__(path=path, autosaving=autosaving)

    def attach_spectrum(self, x, y):
        # loading all data
        super().load_spectrum(x, y, timestamp="NA")

    def load_spectrum(self, data_path, channel="A"):
        """Loads the spectra from the given folder.

        Args:
            data_path (str): Path where HPLC data has been saved.
        """

        # to avoid dropping parameters when called in parent class
        if self.x is not None:
            if self.autosaving:
                self.save_data(filename=f"{data_path}_{channel}")
                self._dump()

        # get raw data
        x, y = self.extract_rawdata(data_path, channel)

        # get timestamp
        tstr = data_path.split(".")[0].split("_")[-1]
        timestamp = "NA"
        try:
            timestamp = time.mktime(time.strptime(tstr, TIME_FORMAT))
        except ValueError:
            pass

        # loading all data
        super().load_spectrum(x, y, timestamp)

    ### PUBLIC METHODS TO LOAD RAW DATA ###

    def extract_rawdata(
        self, experiment_dir: str, channel: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Reads raw data from Chemstation .CH files.

        :param experiment_dir: .D directory with the .CH files

        :returns: np.array(times), np.array(values)   Raw chromatogram data
        """
        filename = os.path.join(experiment_dir, f"DAD1{channel}")
        npz_file = filename + ".npz"

        if os.path.exists(npz_file):
            # already processed
            data = np.load(npz_file)
            return data["times"], data["values"]
        else:
            self.logger.debug("NPZ file not found. First time loading data.")
            ch_file = filename + ".ch"
            data = CHFile(ch_file)
            np.savez_compressed(npz_file, times=data.times, values=data.values)
            return np.array(data.times), np.array(data.values)


@dataclass
class AgilentChannelChromatogramData:
    A: AgilentHPLCChromatogram
    B: AgilentHPLCChromatogram
    C: AgilentHPLCChromatogram
    D: AgilentHPLCChromatogram
    E: AgilentHPLCChromatogram
    F: AgilentHPLCChromatogram
    G: AgilentHPLCChromatogram
    H: AgilentHPLCChromatogram

    @classmethod
    def from_dict(cls, chroms: Dict[str, AgilentHPLCChromatogram]):
        keys = chroms.keys()
        class_keys = vars(AgilentChannelChromatogramData)["__annotations__"].keys()
        if set(class_keys) == set(keys):
            return AgilentChannelChromatogramData(
                A=chroms["A"],
                B=chroms["B"],
                C=chroms["C"],
                D=chroms["D"],
                E=chroms["E"],
                F=chroms["F"],
                G=chroms["G"],
                H=chroms["H"],
            )
        else:
            err = f"{keys} don't match {class_keys}"
            raise KeyError(err)
