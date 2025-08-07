import os
import time
import unittest


from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    DEFAULT_SEQUENCE,
)


class TestSequence(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    def setUp(self):
        num = 242
        self.hplc_controller = set_up_utils(num, offline=False, runs=True)
        self.other_default = DEFAULT_METHOD_242 if num == 242 else DEFAULT_METHOD_254
        self.hplc_controller.switch_sequence(DEFAULT_SEQUENCE)

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_run_sequence_no_stall(self):
        self.hplc_controller.preprun()
        self.hplc_controller.run_sequence(stall_while_running=False)
        time_left, done = self.hplc_controller.check_sequence_complete()
        sequence_dir = self.hplc_controller.sequence_controller.data_files[-1].dir
        child_dir = self.hplc_controller.sequence_controller.data_files[-1].child_dirs[
            0
        ]
        self.assertIsNotNone(sequence_dir)
        self.assertIsNotNone(child_dir)
        self.assertTrue(os.path.isdir(sequence_dir))
        self.assertTrue(os.path.isdir(child_dir))
        while not done:
            time.sleep(time_left / 2)
            time_left, done = self.hplc_controller.check_sequence_complete()
        _ = self.hplc_controller.get_last_run_sequence_data()
        uv = self.hplc_controller.get_last_run_sequence_data(read_uv=True)
        reports = self.hplc_controller.get_last_run_sequence_reports()
        files = self.hplc_controller.get_last_run_sequence_file_paths()
        for file in files.child_dirs:
            self.assertTrue(os.path.isdir(file))
        for i, report in enumerate(reports):
            self.assertIsNotNone(report.vial_location)
            self.assertIsNotNone(report.solvents)
            self.assertTrue(210 in list(uv[i].keys()))

    def test_run_sequence_stall(self):
        self.hplc_controller.preprun()
        self.hplc_controller.run_sequence(stall_while_running=True)
        time_left, done = self.hplc_controller.check_sequence_complete()
        self.assertTrue(done)
        self.assertEqual(time_left, 0)
        sequence_dir = self.hplc_controller.get_last_run_sequence_file_paths().dir
        child_dir = self.hplc_controller.get_last_run_sequence_file_paths().child_dirs[
            0
        ]
        self.assertIsNotNone(sequence_dir)
        self.assertIsNotNone(child_dir)
        self.assertTrue(os.path.isdir(sequence_dir))
        self.assertTrue(os.path.isdir(child_dir))
        _ = self.hplc_controller.get_last_run_sequence_data()
        uv = self.hplc_controller.get_last_run_sequence_data(read_uv=True)
        reports = self.hplc_controller.get_last_run_sequence_reports()
        for i, report in enumerate(reports):
            self.assertIsNotNone(report.vial_location)
            self.assertIsNotNone(report.solvents)
            self.assertTrue(210 in list(uv[i].keys()))


if __name__ == "__main__":
    unittest.main()
