from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class Num(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9

    @classmethod
    def from_num(cls, num: int):
        num_mapping = {
            1: Num.ONE,
            2: Num.TWO,
            3: Num.THREE,
            4: Num.FOUR,
            5: Num.FIVE,
            6: Num.SIX,
            7: Num.SEVEN,
            8: Num.EIGHT,
            9: Num.NINE,
        }

        if num in num_mapping:
            return num_mapping[num]
        else:
            raise ValueError("Num must be between 1 and 9")


class Plate(Enum):
    ONE = -96
    TWO = 4000

    @classmethod
    def from_num(cls, plate: int) -> Plate:
        if 1 <= plate <= 2:
            return Plate.ONE if plate == 1 else Plate.TWO
        raise ValueError("Plate is one or 1 or 2")


class Letter(Enum):
    A = 4191
    B = 4255
    C = 4319
    D = 4383
    E = 4447
    F = 4511

    @classmethod
    def from_str(cls, let: str) -> Letter:
        letter_mapping = {
            "A": Letter.A,
            "B": Letter.B,
            "C": Letter.C,
            "D": Letter.D,
            "E": Letter.E,
            "F": Letter.F,
        }

        if let in letter_mapping:
            return letter_mapping[let]
        else:
            raise ValueError("Letter must be one of A to F")

    @classmethod
    def from_int(cls, num: int) -> Letter:
        letter_mapping = {
            "A": Letter.A,
            "B": Letter.B,
            "C": Letter.C,
            "D": Letter.D,
            "E": Letter.E,
            "F": Letter.F,
        }

        if num <= len(letter_mapping):
            return list(letter_mapping.values())[num]
        else:
            raise ValueError("Letter must be one of A to F")


@dataclass
class FiftyFourVialPlate:
    """Class to represent the 54 vial tray.

    :param plate: one of the two, (P1 or P2)
    :param letter: one of the rows, (A B C D E F)
    :param num: one of the columns, (1 2 3 4 5 6 7 8 9)

    Examples:
    >>> from pychemstation.utils.tray_types import FiftyFourVialPlate
    >>> FiftyFourVialPlate.from_str("P1-A2")
    >>> FiftyFourVialPlate(plate=Plate.TWO, letter=Letter.A, num=Num.THREE)
    """

    plate: Plate
    letter: Letter
    num: Num

    def value(self) -> int:
        return self.plate.value + self.letter.value + self.num.value

    @classmethod
    def from_tray_row_col(cls, tray: int, row: int, col: int):
        try:
            return FiftyFourVialPlate(
                plate=Plate.from_num(tray),
                letter=Letter.from_int(row),
                num=Num.from_num(col),
            )
        except Exception:
            raise ValueError("Could not parse tray location.")

    @classmethod
    def from_str(cls, loc: str):
        """Converts a string representing the vial location into numerical representation for Chemstation.

        :param loc: vial location
        :return: `FiftyFourVialPlate` object representing the vial location
        :raises: ValueError if string is invalid tray location

        Examples:
        >>> from pychemstation.utils.tray_types import FiftyFourVialPlate
        >>> vial_location = FiftyFourVialPlate.from_str("P2-F4")
        """
        if len(loc) != 5:
            raise ValueError(
                "Plate locations must be PX-LY, where X is either 1 or 2 and Y is 1 to 9"
            )
        try:
            plate = int(loc[1])
            letter = loc[3]
            num = int(loc[4])
            return FiftyFourVialPlate(
                plate=Plate.from_num(plate),
                letter=Letter.from_str(letter),
                num=Num.from_num(num),
            )
        except Exception:
            raise ValueError(
                "Plate locations must be PX-LY, where X is either 1 or 2 and Y is 1 to 9"
            )

    @classmethod
    def from_int(cls, num: int) -> Tray:
        """Converts an integer representation of a vial location to a `FiftyFourVialPlate` object

        :param num: numerical representation of a vial location
        :return: the proper vial location object
        :raises: ValueError no matching can be made

        Examples:
        >>> vial_location = FiftyFourVialPlate.from_int(4097)
        """
        if num in range(1, 11):
            return VialBar(num)

        row_starts = [
            # plate 1
            FiftyFourVialPlate.from_str("P1-F1"),
            FiftyFourVialPlate.from_str("P1-E1"),
            FiftyFourVialPlate.from_str("P1-D1"),
            FiftyFourVialPlate.from_str("P1-C1"),
            FiftyFourVialPlate.from_str("P1-B1"),
            FiftyFourVialPlate.from_str("P1-A1"),
            # plate 2
            FiftyFourVialPlate.from_str("P2-F1"),
            FiftyFourVialPlate.from_str("P2-E1"),
            FiftyFourVialPlate.from_str("P2-D1"),
            FiftyFourVialPlate.from_str("P2-C1"),
            FiftyFourVialPlate.from_str("P2-B1"),
            FiftyFourVialPlate.from_str("P2-A1"),
        ]

        # find which row
        possible_row = None
        for i in range(0, 6):
            p1_val = row_starts[i].value()
            p2_val = row_starts[6 + i].value()
            if num >= p2_val:
                possible_row = row_starts[6 + i]
            elif p1_val <= num < row_starts[-1].value():
                possible_row = row_starts[i]
            if possible_row:
                break

        # determine which num
        if possible_row:
            starting_loc = possible_row
            base_val = starting_loc.plate.value + starting_loc.letter.value
            for i in range(1, 10):
                if num - i == base_val:
                    return FiftyFourVialPlate(
                        plate=starting_loc.plate,
                        letter=starting_loc.letter,
                        num=Num.from_num(i),
                    )
        raise ValueError("Number didn't match any location. " + str(num))


class VialBar(Enum):
    """Class to represent the vial bar, has 10 locations.

    Examples:
    >>> vial_bar_2 = VialBar(2)
    >>> vial_bar_10 = VialBar.TEN
    """

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10


@dataclass
class LocationPlus:
    """Not sure what location refers to, but part the `Draw` function for specifying an `InjectorTable`"""

    unit: int
    tray: int
    row: int
    col: int


Tray = Union[FiftyFourVialPlate, VialBar, LocationPlus]
