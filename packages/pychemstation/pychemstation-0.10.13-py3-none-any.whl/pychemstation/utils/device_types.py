from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class DADChannels:
    A: int
    A_ON: bool
    B: int
    B_ON: bool
    C: int
    C_ON: bool
    D: int
    D_ON: bool
    E: int
    E_ON: bool


class DADChannel(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class PumpPosition(Enum):
    ONE = 1
    TWO = 2

    @classmethod
    def from_str(cls, pos):
        match pos:
            case "Position1":
                return PumpPosition.ONE
            case "Position2":
                return PumpPosition.TWO
            case _:
                raise ValueError("Expected one of Position 1 or Position 2")

    def to_str(self):
        match self:
            case PumpPosition.ONE:
                return "Position1"
            case PumpPosition.TWO:
                return "Position2"
            case _:
                raise ValueError("Enum is one of ONE or TWO")


class PumpValve(Enum):
    A = "A"
    B = "B"


@dataclass
class SolventBottle:
    absolute_filled: float
    percent_filled: float
    type: Optional[PumpValve]
    in_use: bool
    user_name: str
    max_volume: Optional[float]


MaybeBottle = Optional[SolventBottle]
MaybePumpPosition = Optional[PumpPosition]


class SignalRead:
    on: bool
    wavelength: int
