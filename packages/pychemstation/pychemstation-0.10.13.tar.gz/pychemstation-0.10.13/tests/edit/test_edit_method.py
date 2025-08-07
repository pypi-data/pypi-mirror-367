import random
import unittest

from pychemstation.utils.macro import Command
from pychemstation.utils.method_types import (
    TimeTableEntry,
    MethodDetails,
    HPLCMethodParams,
)
from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_METHOD,
)


class TestMethod(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    num = 242
    hplc_controller = set_up_utils(num, offline=False, runs=False)

    def setUp(self):
        self.hplc_controller.send(
            Command.SAVE_METHOD_CMD.value.format(
                commit_msg="method saved by pychemstation"
            )
        )
        self.hplc_controller.switch_method(DEFAULT_METHOD)

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_edit_method_flow_and_om(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(
            name=DEFAULT_METHOD + ".M",
            timetable=[
                TimeTableEntry(start_time=1.0, organic_modifer=20.0, flow=0.65),
                TimeTableEntry(start_time=2.0, organic_modifer=30.0, flow=0.55),
                TimeTableEntry(start_time=2.5, organic_modifer=60.0, flow=0.45),
                TimeTableEntry(start_time=3.0, organic_modifer=80.0, flow=0.35),
                TimeTableEntry(start_time=3.5, organic_modifer=100.0, flow=0.25),
            ],
            stop_time=5.0,
            post_time=1.0,
            params=HPLCMethodParams(organic_modifier=3.0, flow=0.75),
        )
        try:
            self.hplc_controller.edit_method(new_method, save=True)
            self.assertEqual(new_method, self.hplc_controller.load_method())
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_edit_method_only_om(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(
            name=DEFAULT_METHOD + ".M",
            timetable=[
                TimeTableEntry(start_time=1.0, organic_modifer=15.23),
                TimeTableEntry(start_time=2.0, organic_modifer=34.44),
                TimeTableEntry(start_time=2.5, organic_modifer=66.23),
                TimeTableEntry(start_time=3.0, organic_modifer=88.3),
                TimeTableEntry(start_time=3.5, organic_modifer=98.23),
            ],
            stop_time=12.3,
            post_time=3.4,
            params=HPLCMethodParams(organic_modifier=7.23, flow=0.65),
        )
        try:
            self.hplc_controller.edit_method(new_method, save=True)
            self.assertEqual(new_method, self.hplc_controller.load_method())
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_edit_method_only_flow(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(
            name=DEFAULT_METHOD + ".M",
            timetable=[
                TimeTableEntry(start_time=1.0, flow=0.56),
                TimeTableEntry(start_time=2.0, flow=0.76),
                TimeTableEntry(start_time=2.5, flow=0.23),
                TimeTableEntry(start_time=3.0, flow=0.89),
                TimeTableEntry(start_time=3.5, flow=0.65),
            ],
            stop_time=5.9,
            post_time=2.3,
            params=HPLCMethodParams(organic_modifier=6.87, flow=0.65),
        )
        try:
            self.hplc_controller.edit_method(new_method, save=True)
            self.assertEqual(new_method, self.hplc_controller.load_method())
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_edit_method_some_flow_some_om(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = MethodDetails(
            name=DEFAULT_METHOD + ".M",
            timetable=[
                TimeTableEntry(start_time=1.0, flow=0.56),
                TimeTableEntry(start_time=2.0, organic_modifer=10.2, flow=0.76),
                TimeTableEntry(start_time=2.5, organic_modifer=16.2),
                TimeTableEntry(start_time=3.0, flow=0.89),
                TimeTableEntry(start_time=3.5, organic_modifer=98.3, flow=0.65),
            ],
            stop_time=5.9,
            post_time=2.3,
            params=HPLCMethodParams(organic_modifier=7.23, flow=0.65),
        )
        try:
            self.hplc_controller.edit_method(new_method, save=True)
            self.assertEqual(new_method, self.hplc_controller.load_method())
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_update_method_components(self):
        new_flow = random.randint(1, 10) / 10
        self.hplc_controller.method_controller.edit_flow(new_flow=new_flow)
        new_post_time = random.randint(1, 6)
        self.hplc_controller.method_controller.edit_post_time(
            new_post_time=new_post_time
        )
        new_stop_time = random.randint(1, 20)
        self.hplc_controller.method_controller.edit_stop_time(
            new_stop_time=new_stop_time
        )
        new_om = random.randint(1, 50)
        self.hplc_controller.method_controller.edit_initial_om(new_om=new_om)
        method_details = self.hplc_controller.load_method()
        self.assertEqual(method_details.params.flow, new_flow)
        self.assertEqual(method_details.post_time, new_post_time)
        self.assertEqual(method_details.stop_time, new_stop_time)
        self.assertEqual(method_details.params.organic_modifier, new_om)

    def test_update_only_timetable(self):
        start_time_1 = random.randint(1, 10)
        starting_og = random.randint(1, 50)
        timetable_flow = random.randint(1, 10) / 10
        timetable = [
            TimeTableEntry(
                start_time=start_time_1,
                organic_modifer=starting_og,
                flow=timetable_flow,
            ),
            TimeTableEntry(
                start_time=start_time_1 + 5, organic_modifer=78, flow=1 - timetable_flow
            ),
        ]
        self.hplc_controller.method_controller.edit_method_timetable(timetable)
        method_details = self.hplc_controller.load_method()
        for i, a_b in enumerate(zip(timetable, method_details.timetable)):
            method_a = a_b[0]
            method_b = a_b[1]
            self.assertAlmostEqual(method_a.start_time, method_b.start_time)
            self.assertAlmostEqual(method_a.organic_modifer, method_b.organic_modifer)
            self.assertAlmostEqual(method_a.flow, method_b.flow)


if __name__ == "__main__":
    unittest.main()
