import os
import random
import string
import unittest

from pychemstation.analysis.process_report import ReportType
from pychemstation.utils.sequence_types import SequenceDataFiles
from pychemstation.utils.tray_types import FiftyFourVialPlate, VialBar
from tests.constants import DEFAULT_SEQUENCE, VIAL_PLATES, clean_up, set_up_utils


class TestOffline(unittest.TestCase):
    """
    These tests should always work, while the controller is offline or online.
    """

    def setUp(self):
        self.hplc_controller = set_up_utils(-1, offline=True)
        self.cwd = os.getcwd()

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_vial_bar(self):
        self.assertTrue(VialBar.ONE == VialBar(1))

    def test_tray_nums_only(self):
        for i in range(len(VIAL_PLATES)):
            self.assertEqual(
                VIAL_PLATES[i], FiftyFourVialPlate.from_int(VIAL_PLATES[i].value())
            )

    def test_get_last_run_sequence(self):
        path = "hplc_testing 2025-03-27 17-13-47"
        self.hplc_controller.sequence_controller.data_files.append(
            SequenceDataFiles(
                sequence_name=DEFAULT_SEQUENCE, dir=os.path.join(self.cwd, path)
            )
        )
        try:
            most_recent_folder = self.hplc_controller.sequence_controller.data_files[-1]
            chrom = self.hplc_controller.get_last_run_sequence_data()
            report = self.hplc_controller.get_last_run_sequence_reports()
            check_folder = self.hplc_controller.sequence_controller._fuzzy_match_most_recent_folder(
                most_recent_folder=most_recent_folder,
            )
            self.assertEqual(check_folder.ok_value.dir, os.path.join(self.cwd, path))
            self.hplc_controller.sequence_controller.data_files[
                -1
            ].dir = check_folder.ok_value
            self.assertEqual(len(report), len(chrom))
            self.assertEqual(report[0].vial_location, FiftyFourVialPlate.from_int(4097))
            self.assertEqual(len(report[0].signals), 5)
        except Exception:
            self.fail()

    def test_plate_number(self):
        vial_letters = string.ascii_letters[0:6]
        vial_locations = [
            FiftyFourVialPlate.from_str(
                f"P{(random.randint(1, 2))}-{vial_letters[random.randint(0, 5)].capitalize()}{str(random.randint(1, 9))}"
            )
            for _ in range(50)
        ]
        for from_str in vial_locations:
            self.assertEqual(from_str, FiftyFourVialPlate.from_int(from_str.value()))

    def test_get_method_report(self):
        method_path = "0_2025-03-15 19-14-35.D"
        report = self.hplc_controller.get_last_run_method_report(
            custom_path=os.path.join(self.cwd, method_path), report_type=ReportType.CSV
        )
        self.assertEqual(report.vial_location, FiftyFourVialPlate.from_int(4096))
        self.assertEqual(len(report.signals), 5)

    def test_get_method_report_offname(self):
        method_path = "10 IS 2025-02-10 23-41-33_10_2025-02-11 02-21-44.D"
        report = self.hplc_controller.get_last_run_method_report(
            custom_path=os.path.join(self.cwd, method_path), report_type=ReportType.CSV
        )
        self.assertEqual(report.vial_location, FiftyFourVialPlate.from_int(4417))
        self.assertEqual(len(report.signals), 5)

    def test_get_seq_report(self):
        seq_path = "hplc_testing 2025-03-27 17-13-47"
        report = self.hplc_controller.get_last_run_sequence_reports(
            custom_path=os.path.join(self.cwd, seq_path), report_type=ReportType.CSV
        )
        self.assertEqual(len(report[0].signals[0].peaks), 12)
        self.assertEqual(report[0].vial_location, FiftyFourVialPlate.from_int(4097))

    def test_get_method_uv(self):
        method_path = "0_2025-03-15 19-14-35.D"
        try:
            self.hplc_controller.get_last_run_method_data(
                custom_path=os.path.join(self.cwd, method_path), read_uv=True
            )
        except Exception:
            self.fail("should not get here")
    
    def test_get_seq_data(self):
        seq_path = "hplc_testing 2025-03-27 17-13-47"
        try:
            data = self.hplc_controller.get_last_run_sequence_data(
                custom_path=os.path.join(self.cwd, seq_path)
            )
            self.assertEqual(len(data), 4)
        except Exception as e:
            self.fail(f"should not get here: {e}")

    def test_get_seq_uv(self):
        seq_path = "hplc_testing 2025-03-27 17-13-47"
        try:
            uv = self.hplc_controller.get_last_run_sequence_data(
                custom_path=os.path.join(self.cwd, seq_path), read_uv=True
            )
            uv_keys = list(uv[0].keys())
            self.assertTrue(uv_keys[0] in range(100, 400))
            self.assertTrue(uv_keys[0] in range(100, 400))
        except Exception:
            self.fail("should not get here")

    def test_get_sequence_files(self):
        self.hplc_controller.sequence_controller.data_files.append(
            SequenceDataFiles(
                dir=os.path.join(os.getcwd(), "hplc_testing 2025-03-27 17-13-47"),
                child_dirs=[],
                sequence_name=DEFAULT_SEQUENCE,
            )
        )
        files = self.hplc_controller.get_last_run_sequence_file_paths()
        self.assertTrue(os.path.isdir(files.dir))
        for child_dir in files.child_dirs:
            self.assertTrue(os.path.isdir(child_dir))
        self.assertTrue(len(files.child_dirs) == 4)

    def test_get_last_run_method(self):
        self.hplc_controller.method_controller.data_files.append(
            os.path.join(
                os.getcwd(), "10 IS 2025-02-10 23-41-33_10_2025-02-11 02-21-44.D"
            )
        )
        self.assertTrue(
            os.path.isdir(self.hplc_controller.get_last_run_method_file_path())
        )


if __name__ == "__main__":
    unittest.main()
