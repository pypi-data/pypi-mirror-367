from typing import Union

from result import Result

from .mock_hplc import MockHPLC
from ..abc_tables.abc_comm import ABCCommunicationController
from ..macro import Status


class MockCommunicationController(ABCCommunicationController):
    def __init__(self, comm_dir: str):
        super().__init__(comm_dir)
        self.hplc = MockHPLC()

    def get_num_val(self, cmd: str) -> Union[int, float]:
        raise NotImplementedError

    def get_text_val(self, cmd: str) -> str:
        raise NotImplementedError

    def get_status(self) -> Status:
        raise NotImplementedError

    def _send(self, cmd: str, cmd_no: int, num_attempts=5) -> None:
        raise NotImplementedError

    def _receive(self, cmd_no: int, num_attempts=100) -> Result[str, str]:
        raise NotImplementedError
