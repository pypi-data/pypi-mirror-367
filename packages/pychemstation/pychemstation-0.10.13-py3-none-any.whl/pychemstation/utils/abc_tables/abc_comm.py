"""
Module to provide API for the communication with Agilent HPLC systems.

HPLCController sends commands to Chemstation software via a command file.
Answers are received via reply file. On the Chemstation side, a custom
Macro monitors the command file, executes commands and writes to the reply file.
Each command is given a number (cmd_no) to keep track of which commands have
been processed.

Authors: Alexander Hammer, Hessam Mehr, Lucy Hao
"""

import abc
import os
import time
from abc import abstractmethod
from typing import Union

from result import Err, Ok, Result

from ..macro import HPLCAvailStatus, Command, Response, Status


class ABCCommunicationController(abc.ABC):
    """Abstract class representing the communication controller.

    :param comm_dir: the complete directory path that was used in the MACRO file, common file that pychemstation and Chemstation use to communicate.
    :param cmd_file: name of the write file that pychemstation writes MACROs to, in `comm_dir`
    :param reply_file: name of the read file that Chemstation replies to, in `comm_dir
    :param offline: whether or not communication with Chemstation is to be established
    :param debug: if True, prints all send MACROs to an out.txt file
    """

    # maximum command number
    MAX_CMD_NO = 255

    def __init__(
        self,
        comm_dir: str,
        cmd_file: str = "cmd",
        reply_file: str = "reply",
        offline: bool = False,
        debug: bool = False,
    ):
        if not offline:
            self.debug = debug
            if os.path.isdir(comm_dir):
                self.cmd_file = os.path.join(comm_dir, cmd_file)
                self.reply_file = os.path.join(comm_dir, reply_file)
                self.cmd_no = 0
            else:
                raise FileNotFoundError(f"comm_dir: {comm_dir} not found.")

            # Create files for Chemstation to communicate with Python
            open(self.cmd_file, "a").close()
            open(self.reply_file, "a").close()

            self.reset_cmd_counter()
            self._most_recent_hplc_status: Status = self.get_status()

    @abstractmethod
    def get_num_val(self, cmd: str) -> Union[int, float]:
        pass

    @abstractmethod
    def get_text_val(self, cmd: str) -> str:
        pass

    @abstractmethod
    def get_status(self) -> Status:
        pass

    @abstractmethod
    def _send(self, cmd: str, cmd_no: int, num_attempts=5) -> None:
        pass

    @abstractmethod
    def _receive(self, cmd_no: int, num_attempts=100) -> Result[str, str]:
        pass

    def set_status(self):
        """Updates current status of HPLC machine"""
        self._most_recent_hplc_status = self.get_status()

    def check_if_not_running(self) -> bool:
        """Checks if HPLC machine is in an available state, meaning a state that data is not being written.

        :return: whether the HPLC machine is in a safe state to retrieve data back."""
        self.set_status()
        hplc_avail = isinstance(self._most_recent_hplc_status, HPLCAvailStatus)
        time.sleep(10)
        self.set_status()
        hplc_actually_avail = isinstance(self._most_recent_hplc_status, HPLCAvailStatus)
        time.sleep(10)
        self.set_status()
        hplc_final_check_avail = isinstance(
            self._most_recent_hplc_status, HPLCAvailStatus
        )
        return hplc_avail and hplc_actually_avail and hplc_final_check_avail

    def sleepy_send(self, cmd: Union[Command, str]):
        self.send("Sleep 0.1")
        self.send(cmd)
        self.send("Sleep 0.1")

    def send(self, cmd: Union[Command, str]):
        """Sends a command to Chemstation.

        :param cmd: Command to be sent to HPLC
        """
        if self.cmd_no == self.MAX_CMD_NO:
            self.reset_cmd_counter()

        cmd_to_send: str = cmd.value if isinstance(cmd, Command) else cmd
        self.cmd_no += 1
        self._send(cmd_to_send, self.cmd_no)
        if self.debug:
            f = open("out.txt", "a")
            f.write(cmd_to_send + "\n")
            f.close()

    def receive(self) -> Result[Response, str]:
        """Returns messages received in reply file.

        :return: ChemStation response
        """
        num_response_prefix = "Numerical Responses:"
        str_response_prefix = "String Responses:"
        possible_response = self._receive(self.cmd_no)
        if possible_response.is_ok():
            lines = possible_response.ok_value.splitlines()
            for line in lines:
                if str_response_prefix in line and num_response_prefix in line:
                    string_responses_dirty, _, numerical_responses = line.partition(
                        num_response_prefix
                    )
                    _, _, string_responses = string_responses_dirty.partition(
                        str_response_prefix
                    )
                    return Ok(
                        Response(
                            string_response=string_responses.strip(),
                            num_response=float(numerical_responses.strip()),
                        )
                    )
            return Err("Could not retrieve HPLC response")
        else:
            return Err(f"Could not establish response to HPLC: {possible_response}")

    def reset_cmd_counter(self):
        """Resets the command counter."""
        self._send(Command.RESET_COUNTER_CMD.value, cmd_no=self.MAX_CMD_NO + 1)
        self._receive(cmd_no=self.MAX_CMD_NO + 1)
        self.cmd_no = 0

    def stop_macro(self):
        """Stops Macro execution. Connection will be lost."""
        self.send(Command.STOP_MACRO_CMD)
