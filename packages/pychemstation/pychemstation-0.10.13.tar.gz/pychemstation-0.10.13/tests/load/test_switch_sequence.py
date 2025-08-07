import unittest

from tests.constants import (
    clean_up,
    set_up_utils,
    DEFAULT_SEQUENCE,
)


class TestSequence(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    num = 242
    hplc_controller = set_up_utils(num, offline=False, runs=False)

    def setUp(self):
        self.hplc_controller.switch_sequence(DEFAULT_SEQUENCE)

    def tearDown(self):
        clean_up(self.hplc_controller)

    def test_load(self):
        try:
            seq = self.hplc_controller.load_sequence()
            self.assertTrue(len(seq.rows) > 0)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_switch_seq(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")

    def test_read_seq(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            table = self.hplc_controller.load_sequence()
            self.assertTrue(table)
        except Exception as e:
            self.fail(f"Should have not expected: {e}")


if __name__ == "__main__":
    unittest.main()
