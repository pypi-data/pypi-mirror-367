from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

from .table_types import RegisterFlag


class PType(Enum):
    STR = "str"
    NUM = "num"


@dataclass
class Param:
    ptype: PType
    val: Union[float, int, str, Any]
    chemstation_key: Union[RegisterFlag, list[RegisterFlag]]


@dataclass
class HPLCMethodParams:
    """The starting conditions of a run that are displayed in the Chemstation GUI for the pump."""

    organic_modifier: float
    flow: float
    pressure: Optional[float] = None  # TODO: find this


@dataclass
class TimeTableEntry:
    """Row in a method timetable."""

    start_time: float
    organic_modifer: Optional[float] = None
    flow: Optional[float] = None


@dataclass
class MethodDetails:
    """An Agilent Chemstation method

    :param name: the name of the method, should be the same as the Chemstation method name.
    :param timetable: list of entries in the method timetable
    :param stop_time: the time the method stops running after the last timetable entry. If `None`, won't be set.
    :param post_time: the amount of time after the stoptime that the pumps keep running,
        based on settings in the first row of the timetable. If `None`, won't be set.
    :param params: the organic modifier (pump B) and flow rate displayed for the method (the time 0 settings)
    """

    name: str
    params: HPLCMethodParams
    timetable: list[TimeTableEntry]
    stop_time: Optional[float] = None
    post_time: Optional[float] = None
