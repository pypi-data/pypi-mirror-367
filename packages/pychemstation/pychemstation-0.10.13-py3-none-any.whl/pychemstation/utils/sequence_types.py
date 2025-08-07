from __future__ import annotations

import os.path
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field
from pychemstation.utils.tray_types import Tray


@dataclass
class SequenceDataFiles:
    """Class to represent files generated during a sequence.

    :param sequence_name: the name of the sequence that is running
    :param dir: the complete path of the directory generated for the sequence
    :param child_dirs: the complete path of the files for sequence runs, contains the Chemstation data, `dir` and the sample run file.
    """

    sequence_name: str
    dir: str
    child_dirs: List[str] = field(default_factory=list)


class SampleType(Enum):
    SAMPLE = 1
    BLANK = 2
    CALIBRATION = 3
    CONTROL = 4

    @classmethod
    def _missing_(cls, value):
        return cls.SAMPLE


class InjectionSource(Enum):
    AS_METHOD = "As Method"
    MANUAL = "Manual"
    MSD = "MSD"
    HIP_ALS = "HipAls"

    @classmethod
    def _missing_(cls, value):
        return cls.HIP_ALS


@dataclass
class SequenceEntry:
    """Class to represent each row of a sequence file, maps one to one to Chemstation."""

    data_file: str
    vial_location: Tray
    sample_name: Optional[str] = None
    method: Optional[str] = None
    num_inj: Optional[int] = 1
    inj_vol: Optional[float] = 2
    inj_source: Optional[InjectionSource] = InjectionSource.HIP_ALS
    sample_type: Optional[SampleType] = SampleType.SAMPLE


@dataclass
class SequenceTable:
    """Class to represent a sequence file.

    :param name: name of the sequence
    :param rows: the entries
    """

    name: str
    rows: list[SequenceEntry]

    def __eq__(self, other) -> bool:
        if not isinstance(other, SequenceTable):
            return False

        equal = True
        for self_row, other_row in zip(self.rows, other.rows):
            equal &= self_row.vial_location == other_row.vial_location
            equal &= self_row.data_file == other_row.data_file
            if self_row.method and other_row.method:
                equal &= (
                    os.path.split(os.path.normpath(self_row.method))[-1]
                    == os.path.split(os.path.normpath(other_row.method))[-1]
                )
            equal &= self_row.num_inj == other_row.num_inj
            equal &= self_row.inj_vol == other_row.inj_vol
            equal &= self_row.inj_source == other_row.inj_source
            equal &= self_row.sample_name == other_row.sample_name
            equal &= self_row.sample_type == other_row.sample_type
        return equal
