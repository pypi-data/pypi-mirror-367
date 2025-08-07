import os
import unittest


from pychemstation.utils.sequence_types import (
    SequenceTable,
    SequenceEntry,
    InjectionSource,
    SampleType,
)
from pychemstation.utils.tray_types import (
    FiftyFourVialPlate,
    VialBar,
)
from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_METHOD_242,
    DEFAULT_METHOD_254,
    DEFAULT_SEQUENCE,
    DEFAULT_METHOD,
    VIAL_PLATES,
)


class TestSequence(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    def setUp(self):
        num = 242
        self.hplc_controller = set_up_utils(num, offline=False, runs=False)
        self.other_default = (
            os.path.join(self.hplc_controller.method_controller.src, DEFAULT_METHOD_242)
            if num == 242
            else os.path.join(
                self.hplc_controller.method_controller.src, DEFAULT_METHOD_254
            )
        )
        self.hplc_controller.switch_sequence(DEFAULT_SEQUENCE)
        self.meth_path = os.path.join(
            self.hplc_controller.method_controller.src, DEFAULT_METHOD
        )

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_tray_nums(self):
        seq_table = SequenceTable(
            name=DEFAULT_SEQUENCE,
            rows=[
                SequenceEntry(
                    vial_location=v,
                    method=self.meth_path,
                    num_inj=3,
                    inj_vol=4,
                    sample_name=str(v.value()),
                    data_file=str(v.value()),
                    sample_type=SampleType.SAMPLE,
                    inj_source=InjectionSource.HIP_ALS,
                )
                for v in VIAL_PLATES
            ],
        )
        self.hplc_controller.edit_sequence(seq_table)
        loaded_table = self.hplc_controller.load_sequence()
        for i in range(len(VIAL_PLATES)):
            self.assertTrue(
                VIAL_PLATES[i].value()
                == seq_table.rows[i].vial_location.value()
                == loaded_table.rows[i].vial_location.value()
            )

    def test_tray_num_bar_tray(self):
        vial_bar = SequenceTable(
            name=DEFAULT_SEQUENCE,
            rows=[
                SequenceEntry(
                    vial_location=VialBar.SEVEN,
                    method=self.meth_path,
                    num_inj=3,
                    inj_vol=4.0,
                    sample_name="asd",
                    data_file="asd",
                    sample_type=SampleType.SAMPLE,
                    inj_source=InjectionSource.HIP_ALS,
                ),
            ],
        )
        tray_loc = SequenceTable(
            name=DEFAULT_SEQUENCE,
            rows=[
                SequenceEntry(
                    vial_location=FiftyFourVialPlate.from_str("P2-A4"),
                    method=self.meth_path,
                    num_inj=3,
                    inj_vol=4.0,
                    sample_name="asd",
                    data_file="asd",
                    sample_type=SampleType.SAMPLE,
                    inj_source=InjectionSource.HIP_ALS,
                ),
            ],
        )
        self.hplc_controller.edit_sequence(vial_bar)
        self.assertTrue(self.hplc_controller.load_sequence(), vial_bar)
        self.hplc_controller.edit_sequence(tray_loc)
        self.assertTrue(self.hplc_controller.load_sequence(), tray_loc)

    def test_edit_entire_seq_table(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)

        try:
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=VialBar.SEVEN,
                        method=self.meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="asd",
                        data_file="asd",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate.from_str("P2-F2"),
                        method=self.meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="qwe",
                        data_file="qwe",
                        sample_type=SampleType.BLANK,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                    SequenceEntry(
                        vial_location=VialBar.ONE,
                        method=self.meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="Sampel2232",
                        data_file="Sampel2232",
                        sample_type=SampleType.CALIBRATION,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)
            self.assertEqual(seq_table, self.hplc_controller.load_sequence())
        except Exception:
            self.fail("Should have not occured")

    def test_edit_specific_rows(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        try:
            meth_path = os.path.join(
                self.hplc_controller.method_controller.src, DEFAULT_METHOD
            )
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=VialBar.TEN,
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="Sampel2",
                        data_file="Sampelasdas2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate.from_str("P2-F2"),
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="Sampel2",
                        data_file="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)
            seq_table.rows[0].vial_location = FiftyFourVialPlate.from_str("P1-F3")
            seq_table.rows[1].vial_location = VialBar.THREE
            seq_table.rows[0].sample_type = SampleType.BLANK
            seq_table.rows[0].inj_source = InjectionSource.MANUAL
            self.hplc_controller.edit_sequence(seq_table)
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)
            try:
                self.hplc_controller.sequence_controller.edit_sample_name("fail", 10)
                self.fail("need to throw")
            except ValueError:
                pass
        except Exception:
            self.fail("Should have not occured")

    def test_different_locations(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        meth_path = os.path.join(
            self.hplc_controller.method_controller.src, DEFAULT_METHOD
        )
        seq_table = SequenceTable(
            name=DEFAULT_SEQUENCE,
            rows=[
                SequenceEntry(
                    vial_location=VialBar.TEN,
                    method=meth_path,
                    num_inj=32,
                    inj_vol=2.0,
                    sample_name="hffgk",
                    data_file="Sampelasdas2",
                    sample_type=SampleType.SAMPLE,
                    inj_source=InjectionSource.HIP_ALS,
                ),
                SequenceEntry(
                    vial_location=FiftyFourVialPlate.from_str("P2-F2"),
                    method=meth_path,
                    num_inj=7,
                    inj_vol=4.0,
                    sample_name="Sampel2",
                    data_file="Sampel2",
                    sample_type=SampleType.BLANK,
                    inj_source=InjectionSource.MANUAL,
                ),
            ],
        )
        self.hplc_controller.edit_sequence(seq_table)
        self.hplc_controller.sequence_controller.edit_vial_location(
            FiftyFourVialPlate.from_str("P2-F1"), 1
        )
        seq_table.rows[0].vial_location = FiftyFourVialPlate.from_str("P2-F1")
        self.hplc_controller.sequence_controller.edit_vial_location(
            FiftyFourVialPlate.from_str("P1-D1"), 2
        )
        seq_table.rows[1].vial_location = FiftyFourVialPlate.from_str("P1-D1")
        self.assertEqual(seq_table, self.hplc_controller.load_sequence())

    def test_only_edit_certain_value(self):
        self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        try:
            meth_path = os.path.join(
                self.hplc_controller.method_controller.src, DEFAULT_METHOD
            )
            seq_table = SequenceTable(
                name=DEFAULT_SEQUENCE,
                rows=[
                    SequenceEntry(
                        vial_location=VialBar.TEN,
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="Sampel2",
                        data_file="Sampelasdas2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                    SequenceEntry(
                        vial_location=FiftyFourVialPlate.from_str("P2-F2"),
                        method=meth_path,
                        num_inj=3,
                        inj_vol=4.0,
                        sample_name="Sampel2",
                        data_file="Sampel2",
                        sample_type=SampleType.SAMPLE,
                        inj_source=InjectionSource.HIP_ALS,
                    ),
                ],
            )
            self.hplc_controller.edit_sequence(seq_table)

            seq_table.rows[0].vial_location = FiftyFourVialPlate.from_str("P1-F3")
            self.hplc_controller.sequence_controller.edit_vial_location(
                seq_table.rows[0].vial_location, 1
            )
            seq_table.rows[1].vial_location = VialBar.THREE
            self.hplc_controller.sequence_controller.edit_vial_location(
                seq_table.rows[1].vial_location, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].method = self.other_default
            self.hplc_controller.sequence_controller.edit_method_name(
                seq_table.rows[0].method, 1
            )
            seq_table.rows[1].method = self.other_default
            self.hplc_controller.sequence_controller.edit_method_name(
                seq_table.rows[1].method, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].num_inj = 10
            self.hplc_controller.sequence_controller.edit_num_injections(
                seq_table.rows[0].num_inj, 1
            )
            seq_table.rows[1].num_inj = 6
            self.hplc_controller.sequence_controller.edit_num_injections(
                seq_table.rows[1].num_inj, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].inj_vol = 4
            self.hplc_controller.sequence_controller.edit_injection_volume(
                seq_table.rows[0].inj_vol, 1
            )
            seq_table.rows[1].inj_vol = 0.6
            self.hplc_controller.sequence_controller.edit_injection_volume(
                seq_table.rows[1].inj_vol, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].sample_name = "change2"
            self.hplc_controller.sequence_controller.edit_sample_name(
                seq_table.rows[0].sample_name, 1
            )
            seq_table.rows[1].sample_name = "change5"
            self.hplc_controller.sequence_controller.edit_sample_name(
                seq_table.rows[1].sample_name, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].sample_type = SampleType.BLANK
            self.hplc_controller.sequence_controller.edit_sample_type(
                seq_table.rows[0].sample_type, 1
            )
            seq_table.rows[1].sample_type = SampleType.CALIBRATION
            self.hplc_controller.sequence_controller.edit_sample_type(
                seq_table.rows[1].sample_type, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            seq_table.rows[0].inj_source = InjectionSource.MANUAL
            self.hplc_controller.sequence_controller.edit_injection_source(
                seq_table.rows[0].inj_source, 1
            )
            seq_table.rows[1].inj_source = InjectionSource.AS_METHOD
            self.hplc_controller.sequence_controller.edit_injection_source(
                seq_table.rows[1].inj_source, 2
            )
            loaded_seq = self.hplc_controller.load_sequence()
            self.assertEqual(seq_table, loaded_seq)

            try:
                self.hplc_controller.sequence_controller.edit_sample_name("fail", 10)
                self.fail("need to throw")
            except ValueError:
                pass
            try:
                self.hplc_controller.sequence_controller.edit_sample_name(89, 2)
                self.fail("need to throw")
            except ValueError:
                pass
            try:
                self.hplc_controller.sequence_controller.edit_vial_location(89, 1)
                self.fail("need to throw")
            except ValueError:
                pass
        except Exception:
            self.fail("Should have not occured")


if __name__ == "__main__":
    unittest.main()
