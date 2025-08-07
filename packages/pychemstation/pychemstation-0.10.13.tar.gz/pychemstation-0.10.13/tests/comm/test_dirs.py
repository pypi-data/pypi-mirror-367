import os
import unittest

from pychemstation.control.controllers import CommunicationController
from tests.constants import room


class TestComm(unittest.TestCase):
    """
    These tests should always work with an online controller.
    """

    def setUp(self):
        num = 242
        self.cs_dirs = room(num)
        self.comm = CommunicationController(comm_dir=self.cs_dirs)

    def test_load_dirs(self):
        meth, seq, data_dirs = self.comm.get_chemstation_dirs()
        data_dirs = [d.upper() for d in data_dirs]
        print(meth, seq, data_dirs)
        self.assertTrue(os.path.exists(meth))
        self.assertTrue(os.path.exists(seq))
        for data_dir in data_dirs:
            self.assertTrue(os.path.isdir(data_dir))


if __name__ == "__main__":
    unittest.main()
