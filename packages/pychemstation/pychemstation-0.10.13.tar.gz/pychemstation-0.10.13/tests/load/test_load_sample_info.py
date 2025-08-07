import unittest

from pychemstation.utils.macro import Command
from tests.constants import (
    DEFAULT_METHOD,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    clean_up,
    set_up_utils,
)


class TestSampleInfo(unittest.TestCase):
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

    def test_load_bottles(self):
        print(self.hplc_controller.method_controller)


if __name__ == "__main__":
    unittest.main()
