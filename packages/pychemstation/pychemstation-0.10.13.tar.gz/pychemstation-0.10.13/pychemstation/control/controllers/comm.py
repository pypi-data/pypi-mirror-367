"""
Module to provide API for the communication with Agilent HPLC systems.

HPLCController sends commands to Chemstation software via a command file.
Answers are received via reply file. On the Chemstation side, a custom
Macro monitors the command file, executes commands and writes to the reply file.
Each command is given a number (cmd_no) to keep track of which commands have
been processed.

Authors: Alexander Hammer, Hessam Mehr, Lucy Hao
"""

import time
from typing import Optional, Union, Tuple, List

from result import Err, Ok, Result

from ...utils.abc_tables.abc_comm import ABCCommunicationController
from ...utils.macro import (
    Command,
    HPLCErrorStatus,
    Status,
    str_to_status,
)


class CommunicationController(ABCCommunicationController):
    """Class that communicates with Agilent using Macros

    :param comm_dir: the complete directory path that was used in the MACRO file, common file that pychemstation and Chemstation use to communicate.
    :param cmd_file: name of the write file that pychemstation writes MACROs to, in `comm_dir`
    :param reply_file: name of the read file that Chemstation replies to, in `comm_dir
    :param offline: whether or not communication with Chemstation is to be established
    :param debug: if True, prints all send MACROs to an out.txt file
    """

    def __init__(
        self,
        comm_dir: str,
        cmd_file: str = "cmd",
        reply_file: str = "reply",
        offline: bool = False,
        debug: bool = False,
    ):
        super().__init__(comm_dir, cmd_file, reply_file, offline, debug)

    def get_num_val(self, cmd: str) -> Union[int, float]:
        tries = 10
        for _ in range(tries):
            self.send(Command.GET_NUM_VAL_CMD.value.format(cmd=cmd))
            res = self.receive()
            if res.is_ok():
                return res.ok_value.num_response
        raise RuntimeError("Failed to get number.")

    def get_text_val(self, cmd: str) -> str:
        tries = 5
        for _ in range(tries):
            self.send(Command.GET_TEXT_VAL_CMD.value.format(cmd=cmd))
            res = self.receive()
            if res.is_ok():
                return res.ok_value.string_response
        raise RuntimeError("Failed to get string")

    def get_status(self) -> Status:
        """Get device status(es).

        :return: list of ChemStation's current status
        """
        self.send(Command.GET_STATUS_CMD)
        time.sleep(1)

        try:
            res = self.receive()
            if res.is_err():
                return HPLCErrorStatus.NORESPONSE
            if res.is_ok():
                parsed_response = self.receive().ok_value.string_response
                self._most_recent_hplc_status = str_to_status(parsed_response)
                return self._most_recent_hplc_status
            else:
                raise RuntimeError("Failed to get status")
        except IOError:
            return HPLCErrorStatus.NORESPONSE
        except IndexError:
            return HPLCErrorStatus.MALFORMED

    def _send(self, cmd: str, cmd_no: int, num_attempts=5) -> None:
        """Low-level execution primitive. Sends a command string to HPLC.

        :param cmd: string to be sent to HPLC
        :param cmd_no: Command number
        :param num_attempts: Number of attempts to send the command before raising exception.
        :raises IOError: Could not write to command file.
        """
        err = None
        for _ in range(num_attempts):
            time.sleep(1)
            try:
                with open(self.cmd_file, "w", encoding="utf8") as cmd_file:
                    cmd_file.write(f"{cmd_no} {cmd}")
            except IOError as e:
                err = e
                continue
            else:
                return
        else:
            raise IOError(f"Failed to send command #{cmd_no}: {cmd}.") from err

    def _receive(self, cmd_no: int, num_attempts=100) -> Result[str, str]:
        """Low-level execution primitive. Recives a response from HPLC.

        :param cmd_no: Command number
        :param num_attempts: Number of retries to open reply file
        :raises IOError: Could not read reply file.
        :return: Potential ChemStation response
        """
        err: Optional[Union[OSError, IndexError, ValueError]] = None
        err_msg = ""
        for _ in range(num_attempts):
            time.sleep(1)

            try:
                with open(self.reply_file, "r", encoding="utf_16") as reply_file:
                    response = reply_file.read()
            except OSError as e:
                err = e
                continue

            try:
                first_line = response.splitlines()[0]
                try:
                    response_no = int(first_line.split()[0])
                except ValueError as e:
                    err = e
                    err_msg = f"Caused by {first_line}"
            except IndexError as e:
                err = e
                continue

            # check that response corresponds to sent command
            if response_no == cmd_no:
                return Ok(response)
            else:
                continue
        else:
            return Err(
                f"Failed to receive reply to command #{cmd_no} due to {err} caused by {err_msg}."
            )

    def get_chemstation_dirs(self) -> Tuple[str, str, List[str]]:
        method_dir, sequence_dir, data_dirs = None, None, None
        for _ in range(10):
            self.send(Command.GET_METHOD_DIR)
            res = self.receive()
            if res.is_ok():
                method_dir = res.ok_value.string_response
            self.send(Command.GET_SEQUENCE_DIR)
            res = self.receive()
            if res.is_ok():
                sequence_dir = res.ok_value.string_response
            self.send(Command.GET_DATA_DIRS)
            res = self.receive()
            if res.is_ok():
                data_dirs = res.ok().string_response.split("|")
            if method_dir and sequence_dir and data_dirs:
                if not sequence_dir[0].isalpha():
                    sequence_dir = "C:" + sequence_dir
                if not method_dir[0].isalpha():
                    method_dir = "C:" + method_dir
                for i, data_dir in enumerate(data_dirs):
                    if not data_dir[0].isalpha():
                        data_dirs[i] = "C:" + data_dir
                return method_dir, sequence_dir, data_dirs
        raise ValueError(
            f"One of the method: {method_dir}, sequence: {sequence_dir} or data directories: {data_dirs} could not be found, please provide your own."
        )
