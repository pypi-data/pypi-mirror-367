import unittest

from pychemstation.utils.macro import Command
from tests.constants import (
    DEFAULT_METHOD,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    clean_up,
    set_up_utils,
)


class TestColumn(unittest.TestCase):
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

    def test_edit_exist_col(self):
        old_position = (
            self.hplc_controller.method_controller.column.check_column_position()
        )
        pos_to_change = (
            "Position 1 (Port 1 -> 2)"
            if old_position not in "Position 1 (Port 1 -> 2)"
            else "Position 2 (Port 1 -> 10)"
        )
        self.hplc_controller.method_controller.column.change_column_position(
            column=pos_to_change
        )
        new_position = (
            self.hplc_controller.method_controller.column.check_column_position()
        )
        self.assertEqual(pos_to_change, new_position)
        self.hplc_controller.method_controller.column.change_column_position(
            column=old_position
        )

    def test_edit_non_exist(self):
        try:
            self.hplc_controller.method_controller.column.change_column_position(
                column="test"
            )
            self.fail()
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
