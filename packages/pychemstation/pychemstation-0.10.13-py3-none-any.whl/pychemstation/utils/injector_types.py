from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from pychemstation.utils.tray_types import Tray


class SourceType(Enum):
    DEFAULT = "ActualPosition"
    SPECIFIC_LOCATION = "ActualPositionPlusLocation"
    LOCATION = "Location"


class Mode(Enum):
    DEFAULT = "Default"
    SET = "Set"


@dataclass
class Draw:
    amount: Optional[float] = None
    location: Optional[Tray] = None
    source: Optional[Tray] = None


@dataclass
class DrawDefaultVolume:
    location: Optional[Tray] = None


@dataclass
class DrawDefaultLocation:
    amount: Optional[float] = None


@dataclass
class DrawDefault:
    pass


@dataclass
class Wait:
    duration: Union[int, float]


@dataclass
class Inject:
    pass


class RemoteCommand(Enum):
    START = "START"
    NOT_READY = "NOT_READY"
    STOP = "STOP"
    READY = "READY"
    PREPARE = "PREPARE"


@dataclass
class Remote:
    command: RemoteCommand
    duration: int


InjectorFunction = Union[
    Draw, DrawDefault, DrawDefaultVolume, DrawDefaultLocation, Wait, Inject, Remote
]


@dataclass
class InjectorTable:
    functions: List[InjectorFunction]
