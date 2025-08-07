import unittest

from pychemstation.utils.macro import Command
from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_METHOD,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    gen_rand_method,
)


class TestMethod(unittest.TestCase):
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

    def test_method_switch_load(self):
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        self.assertEqual(
            DEFAULT_METHOD, self.hplc_controller.check_loaded_method()[:-2]
        )
        try:
            self.hplc_controller.switch_method("GENERAL-POROSHELL-JD")
            self.assertEqual(
                "GENERAL-POROSHELL-JD", self.hplc_controller.check_loaded_method()[:-2]
            )
        except Exception:
            self.hplc_controller.switch_method("WM_GENERAL_POROSHELL")
            self.assertEqual(
                "WM_GENERAL_POROSHELL", self.hplc_controller.check_loaded_method()[:-2]
            )

    def test_load_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = gen_rand_method()
        try:
            self.hplc_controller.edit_method(new_method)
            loaded_method = self.hplc_controller.load_method()
            self.assertAlmostEqual(
                new_method.params.organic_modifier,
                loaded_method.params.organic_modifier,
            )
            self.assertAlmostEqual(
                new_method.timetable[0].organic_modifer,
                loaded_method.timetable[0].organic_modifer,
            )
            self.assertAlmostEqual(
                new_method.params.flow, loaded_method.params.flow, places=1
            )
        except Exception as e:
            self.fail(f"Should have not failed: {e}")


if __name__ == "__main__":
    unittest.main()
