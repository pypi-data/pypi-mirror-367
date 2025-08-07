import unittest


from pychemstation.control.controllers.data_aq import (
    MethodController,
    SequenceController,
)
from pychemstation.control.controllers.devices import InjectorController
from pychemstation.utils.abc_tables.device import DeviceController
from pychemstation.utils.abc_tables.run import RunController
from pychemstation.utils.abc_tables.table import ABCTableController


class TestABC(unittest.TestCase):
    def test_fail_abc(self):
        try:
            _ = DeviceController(None, None, None)
            self.fail("shouldnt get here")
        except TypeError:
            try:
                _ = ABCTableController(None, None)
                self.fail("shouldnt get here")
            except TypeError:
                try:
                    _ = RunController(None, None, None, None, None)
                    self.fail("shouldnt get here")
                except TypeError:
                    pass

    def test_pass_child(self):
        try:
            _ = MethodController(
                None, None, [], None, None, None, pump=None, dad=None, column=None
            )
        except TypeError:
            self.fail("shouldnt get here")
        try:
            _ = SequenceController(None, None, None, [], None, None)
        except TypeError:
            self.fail("shouldnt get here")
        try:
            _ = InjectorController(None, None, None)
        except TypeError:
            self.fail("shouldnt get here")


if __name__ == "__main__":
    unittest.main()
