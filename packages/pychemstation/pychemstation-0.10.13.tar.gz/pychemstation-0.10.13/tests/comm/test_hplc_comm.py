import unittest

from pychemstation.utils.macro import Command, HPLCAvailStatus, HPLCRunningStatus
from tests.constants import (
    DEFAULT_METHOD,
    clean_up,
    set_up_utils,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
)


class TestOnline(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    def setUp(self):
        num = 242
        self.hplc_controller = set_up_utils(num, offline=False, runs=False)
        self.other_default = DEFAULT_METHOD_242 if num == 242 else DEFAULT_METHOD_254

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_status_check_standby(self):
        self.hplc_controller.standby()
        self.assertTrue(
            self.hplc_controller.status()
            in [HPLCAvailStatus.STANDBY, HPLCRunningStatus.NOTREADY]
        )

    def test_status_check_preprun(self):
        self.hplc_controller.preprun()
        self.assertTrue(
            self.hplc_controller.status()
            in [
                HPLCAvailStatus.PRERUN,
                HPLCAvailStatus.STANDBY,
                HPLCRunningStatus.NOTREADY,
            ]
        )

    def test_send_command(self):
        try:
            self.hplc_controller.send(Command.GET_METHOD_CMD)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_send_str(self):
        try:
            self.hplc_controller.send("Local TestNum")
            self.hplc_controller.send("TestNum = 0")
            self.hplc_controller.send("Print TestNum")
            self.hplc_controller.send("response_num = TestNum")
            self.hplc_controller.send("Print response_num")
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_get_num(self):
        try:
            self.hplc_controller.send("response_num = 10")
            res = self.hplc_controller.receive().num_response
            self.assertEqual(res, 10)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_get_response(self):
        try:
            self.hplc_controller.switch_method(method_name=DEFAULT_METHOD)
            self.hplc_controller.send(Command.GET_METHOD_CMD)
            res = self.hplc_controller.receive()
            self.assertTrue(DEFAULT_METHOD in res.string_response)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")


if __name__ == "__main__":
    unittest.main()
