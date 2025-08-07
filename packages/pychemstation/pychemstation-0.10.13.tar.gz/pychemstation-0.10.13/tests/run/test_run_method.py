import os
import time
import unittest

from pychemstation.utils.macro import Command
from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_METHOD,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
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

    def test_method_no_stall(self):
        files = []
        tries = 2
        for _ in range(tries):
            self.hplc_controller.run_method(
                experiment_name="test_experiment", stall_while_running=False
            )
            time_left, done = self.hplc_controller.check_method_complete()
            while not done:
                time.sleep(time_left / 2)
                time_left, done = self.hplc_controller.check_method_complete()
            chrom = self.hplc_controller.get_last_run_method_data()
            uv = self.hplc_controller.get_last_run_method_data(read_uv=True)
            repos = self.hplc_controller.get_last_run_method_report()
            files.append(self.hplc_controller.get_last_run_method_file_path())
            self.assertEqual(repos.signals[0].wavelength, 210)
            self.assertIsNotNone(
                repos.signals[0].data,
            )
            self.assertTrue(210 in uv.keys())
            self.assertTrue(len(chrom.A.x) > 0)
        self.assertEqual(len(set(files)), tries)
        for file in files:
            self.assertTrue(os.path.isdir(file))

    def test_method_stall(self):
        files = []
        tries = 3
        for _ in range(tries):
            self.hplc_controller.run_method(experiment_name="test_experiment")
            chrom = self.hplc_controller.get_last_run_method_data()
            uv = self.hplc_controller.get_last_run_method_data(read_uv=True)
            repos = self.hplc_controller.get_last_run_method_report()
            files.append(self.hplc_controller.get_last_run_method_file_path())
            self.assertEqual(repos.signals[0].wavelength, 210)
            self.assertIsNotNone(
                repos.signals[0].data,
            )
            self.assertTrue(210 in uv.keys())
            self.assertTrue(len(chrom.A.x) > 0)
        self.assertEqual(len(set(files)), tries)
        for file in files:
            self.assertTrue(os.path.isdir(file))


if __name__ == "__main__":
    unittest.main()
