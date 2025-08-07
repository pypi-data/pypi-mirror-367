import unittest

from pychemstation.utils.device_types import DADChannel
from pychemstation.utils.macro import Command
from tests.constants import (
    DEFAULT_METHOD,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    clean_up,
    set_up_utils,
)


class TestDAD(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    def setUp(self):
        num = 242
        self.hplc_controller = set_up_utils(num, offline=False, runs=False)
        self.hplc_controller.send(
            Command.SAVE_METHOD_CMD.value.format(
                commit_msg="method saved by pychemstation"
            )
        )
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        self.other_default = DEFAULT_METHOD_242 if num == 242 else DEFAULT_METHOD_254

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_edit_on_wavelength(self):
        self.hplc_controller.method_controller.dad.set_wavelength_usage(
            on=False, wavelength=DADChannel.A
        )
        self.hplc_controller.method_controller.dad.set_wavelength_usage(
            on=False, wavelength=DADChannel.C
        )
        self.hplc_controller.method_controller.dad.set_wavelength_usage(
            on=True, wavelength=DADChannel.E
        )
        wavelengthes = self.hplc_controller.method_controller.dad.load_wavelengths()
        self.assertFalse(wavelengthes.A_ON)
        self.assertFalse(wavelengthes.C_ON)
        self.assertTrue(wavelengthes.E_ON)


if __name__ == "__main__":
    unittest.main()
