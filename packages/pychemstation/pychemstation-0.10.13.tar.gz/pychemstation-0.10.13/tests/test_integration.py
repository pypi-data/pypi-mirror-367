import os.path
import time
import unittest

from pychemstation.utils.method_types import (
    HPLCMethodParams,
    MethodDetails,
    TimeTableEntry,
)
from pychemstation.utils.sequence_types import (
    InjectionSource,
    SampleType,
    SequenceEntry,
    SequenceTable,
)
from pychemstation.utils.tray_types import FiftyFourVialPlate, Letter, Num, Plate
from tests.constants import (
    DEFAULT_METHOD,
    DEFAULT_SEQUENCE,
    clean_up,
    set_up_utils,
)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        num = 242
        self.hplc_controller = set_up_utils(num, offline=False, runs=True)

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_update_method_update_seq_table_run(self):
        try:
            loc = FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.ONE)
            loc1 = FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.FOUR)
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=loc,
                        sample_name="run0",
                        data_file="run0",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                    SequenceEntry(
                        vial_location=loc1,
                        sample_name="run1",
                        data_file="run1",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = MethodDetails(
                name=DEFAULT_METHOD,
                params=HPLCMethodParams(organic_modifier=5, flow=0.65),
                timetable=[
                    TimeTableEntry(start_time=1, organic_modifer=100, flow=0.65)
                ],
                stop_time=1,
                post_time=1,
            )
            self.hplc_controller.edit_method(rand_method, save=True)
            self.hplc_controller.preprun()
            self.hplc_controller.run_sequence()
            chrom = self.hplc_controller.get_last_run_sequence_data()
            uv = self.hplc_controller.get_last_run_sequence_data(read_uv=True)
            reports = self.hplc_controller.get_last_run_sequence_reports()
            paths = self.hplc_controller.get_last_run_sequence_file_paths()
            for child_dir in paths.child_dirs:
                self.assertTrue("run1" in child_dir or "run0" in child_dir)
            self.assertEqual(len(chrom), len(seq_table.rows))
            self.assertEqual(len(uv), len(seq_table.rows))
            report_vials = [reports[0].vial_location, reports[1].vial_location]
            self.assertTrue(loc1 in report_vials)
            self.assertTrue(loc in report_vials)
        except Exception:
            self.fail("Failed")

    def test_run_method_immidiate_return(self):
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        rand_method = MethodDetails(
            name=DEFAULT_METHOD,
            params=HPLCMethodParams(organic_modifier=5, flow=0.65),
            timetable=[
                TimeTableEntry(start_time=1.5, organic_modifer=50, flow=0.65),
                TimeTableEntry(start_time=3.5, organic_modifer=95, flow=0.65),
            ],
            stop_time=1,
            post_time=1,
        )
        self.hplc_controller.edit_method(rand_method, save=True)
        trys = 3
        paths = []
        vial_locations = []
        try:
            for _ in range(trys):
                self.hplc_controller.run_method(
                    experiment_name="test_experiment", stall_while_running=False
                )
                time_left, done = self.hplc_controller.check_method_complete()
                current_run_file = self.hplc_controller.get_last_run_method_file_path()
                self.assertTrue(os.path.isdir(current_run_file))
                paths.append(current_run_file)
                while not done:
                    time.sleep(abs(time_left / 2))
                    print(time_left)
                    time_left, done = self.hplc_controller.check_method_complete()
                chrom = self.hplc_controller.get_last_run_method_data()
                uv = self.hplc_controller.get_last_run_method_data(read_uv=True)
                report = self.hplc_controller.get_last_run_method_report()
                vial_locations.append(report.vial_location)
                self.assertEqual(report.signals[0].wavelength, 210)
                self.assertTrue(210 in uv.keys())
                self.assertTrue(len(chrom.A.x) > 0)
            self.assertTrue(len(set(paths)) == trys)
            for i in range(len(vial_locations) - 1):
                self.assertEqual(vial_locations[i], vial_locations[i + 1])
            for path in paths:
                self.assertTrue(os.path.isdir(path))
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_update_method_update_seq_table_run_immidiate_return(self):
        try:
            loc1 = FiftyFourVialPlate.from_str("P1-A1")
            loc2 = FiftyFourVialPlate.from_str("P1-A4")
            self.assertEqual(
                loc1, FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.ONE)
            )
            self.assertEqual(
                loc2, FiftyFourVialPlate(plate=Plate.ONE, letter=Letter.A, num=Num.FOUR)
            )
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=loc1,
                        sample_name="run0",
                        data_file="run0",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                    SequenceEntry(
                        vial_location=loc2,
                        sample_name="run1",
                        data_file="run1",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = MethodDetails(
                name=DEFAULT_METHOD,
                params=HPLCMethodParams(organic_modifier=5, flow=0.65),
                timetable=[
                    TimeTableEntry(start_time=0.5, organic_modifer=50, flow=0.65)
                ],
                stop_time=1,
                post_time=0.5,
            )
            self.hplc_controller.edit_method(rand_method, save=True)
            self.hplc_controller.preprun()
            self.hplc_controller.run_sequence(stall_while_running=False)
            time_left, done = self.hplc_controller.check_sequence_complete()
            while not done:
                time.sleep(time_left / 2)
                time_left, done = self.hplc_controller.check_sequence_complete()
            chrom = self.hplc_controller.get_last_run_sequence_data()
            uv = self.hplc_controller.get_last_run_sequence_data(read_uv=True)
            reports = self.hplc_controller.get_last_run_sequence_reports()
            paths = self.hplc_controller.get_last_run_sequence_file_paths()
            for child_dir in paths.child_dirs:
                self.assertTrue("run1" in child_dir or "run0" in child_dir)
            report_vials = [reports[0].vial_location, reports[1].vial_location]
            self.assertTrue(loc1 in report_vials)
            self.assertTrue(loc2 in report_vials)
            self.assertEqual(len(chrom), 2)
            self.assertEqual(len(uv), 2)
        except Exception:
            self.fail("Failed")

    def test_update_only_same_vial_location_type(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate.from_str("P1-A1"),
                        sample_name="run0",
                        data_file="run0",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate.from_str("P1-A4"),
                        sample_name="run1",
                        data_file="run1",
                        method=DEFAULT_METHOD,
                        inj_source=InjectionSource.HIP_ALS,
                        inj_vol=0.5,
                        num_inj=1,
                        sample_type=SampleType.SAMPLE,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)
            loc2 = FiftyFourVialPlate.from_str("P1-F7")
            loc1 = FiftyFourVialPlate.from_str("P1-A4")
            self.hplc_controller.sequence_controller.edit_vial_location(
                loc=loc1, row_num=1
            )
            self.hplc_controller.sequence_controller.edit_vial_location(
                loc=loc2, row_num=2
            )
            self.hplc_controller.preprun()
            self.hplc_controller.run_sequence(stall_while_running=False)
            time_left, done = self.hplc_controller.check_sequence_complete()
            while not done:
                time.sleep(time_left / 2)
                time_left, done = self.hplc_controller.check_sequence_complete()
            chrom = self.hplc_controller.get_last_run_sequence_data()
            uv = self.hplc_controller.get_last_run_sequence_data(read_uv=True)
            reports = self.hplc_controller.get_last_run_sequence_reports()
            paths = self.hplc_controller.get_last_run_sequence_file_paths()
            for child_dir in paths.child_dirs:
                self.assertTrue("run1" in child_dir or "run0" in child_dir)
            report_vials = [reports[0].vial_location, reports[1].vial_location]
            self.assertTrue(loc1 in report_vials)
            self.assertTrue(loc2 in report_vials)
            self.assertEqual(len(chrom), len(seq_table.rows))
            self.assertEqual(len(uv), len(seq_table.rows))
        except Exception:
            self.fail("Failed")


if __name__ == "__main__":
    unittest.main()
