"""
Abstract module containing shared logic for Method and Sequence tables.

Authors: Lucy Hao
"""

from __future__ import annotations

import abc
from abc import abstractmethod
from collections.abc import Callable
from typing import Optional, Union

from result import Err, Result

from ..macro import Command, Response
from ..method_types import MethodDetails, PType, Param
from ..sequence_types import SequenceTable
from ..table_types import Table, RegisterFlag, TableOperation, Device
from ...control.controllers import CommunicationController

TableType = Union[MethodDetails, SequenceTable]


class ABCTableController(abc.ABC):
    """Abstract controller for all table-like objects in Chemstation.
    :param controller: controller for sending MACROs to Chemstation
    :param table: contains register keys needed for accessing table in Chemstation.
    """

    def __init__(
        self,
        controller: Optional[CommunicationController],
        table: Table | Device,
    ):
        self.controller = controller
        self.table_locator = table
        self.table_state: Optional[TableType] = None

    def __new__(cls, *args, **kwargs):
        if cls is ABCTableController:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls, *args, **kwargs)

    @abstractmethod
    def download(self):
        pass

    @abc.abstractmethod
    def get_row(self, row: int):
        pass

    def receive(self) -> Result[Response, str]:
        if self.controller:
            for _ in range(10):
                try:
                    return self.controller.receive()
                except IndexError:
                    continue
            return Err("Could not parse response")
        else:
            raise ValueError("Controller is offline!")

    def send(self, cmd: Union[Command, str]):
        if not self.controller:
            raise RuntimeError(
                "Communication controller must be initialized before sending command. It is currently in offline mode."
            )
        self.controller.send(cmd)

    def sleepy_send(self, cmd: Union[Command, str]):
        if self.controller:
            self.controller.sleepy_send(cmd)
        else:
            raise ValueError("Controller is offline")

    def sleep(self, seconds: int):
        """Tells the HPLC to wait for a specified number of seconds.

        :param seconds: number of seconds to wait
        """
        self.send(Command.SLEEP_CMD.value.format(seconds=seconds))

    def get_num(self, row: int, col_name: RegisterFlag) -> Union[int, float]:
        if isinstance(self.table_locator, Table) and self.controller:
            return self.controller.get_num_val(
                TableOperation.GET_ROW_VAL.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    row=row,
                    col_name=col_name.value,
                )
            )
        else:
            raise ValueError("Controller is offline")

    def get_text(self, row: int, col_name: RegisterFlag) -> str:
        if isinstance(self.table_locator, Table) and self.controller:
            return self.controller.get_text_val(
                TableOperation.GET_ROW_TEXT.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    row=row,
                    col_name=col_name.value,
                )
            )
        else:
            raise ValueError("Controller is offline")

    def add_new_col_num(self, col_name: RegisterFlag, val: Union[int, float]):
        if not (isinstance(val, int) or isinstance(val, float)):
            raise ValueError(f"{val} must be an int or float.")
        if isinstance(self.table_locator, Table) and self.controller:
            self.sleepy_send(
                TableOperation.NEW_COL_VAL.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    col_name=col_name,
                    val=val,
                )
            )
        else:
            raise ValueError("require table, not device")

    def add_new_col_text(self, col_name: RegisterFlag, val: str):
        if not isinstance(val, str):
            raise ValueError(f"{val} must be a str.")
        if isinstance(self.table_locator, Table) and self.controller:
            self.sleepy_send(
                TableOperation.NEW_COL_TEXT.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    col_name=col_name,
                    val=val,
                )
            )
        else:
            raise ValueError("require table not device")

    def _edit_row_num(
        self, col_name: RegisterFlag, val: Union[int, float], row: Optional[int] = None
    ):
        if not (isinstance(val, int) or isinstance(val, float)):
            raise ValueError(f"{val} must be an int or float.")
        num_rows = self.get_row_count_safely()
        if row and num_rows < row:
            raise ValueError("Not enough rows to edit!")

        if isinstance(self.table_locator, Table) and self.controller:
            self.sleepy_send(
                TableOperation.EDIT_ROW_VAL.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    row=row if row is not None else "response_num",
                    col_name=col_name,
                    val=val,
                )
            )

    def _edit_row_text(
        self, col_name: RegisterFlag, val: str, row: Optional[int] = None
    ):
        if not isinstance(val, str):
            raise ValueError(f"{val} must be a str.")
        num_rows = self.get_row_count_safely()
        if row and num_rows < row:
            raise ValueError("Not enough rows to edit!")

        if isinstance(self.table_locator, Table) and self.controller:
            self.sleepy_send(
                TableOperation.EDIT_ROW_TEXT.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    row=row if row is not None else "response_num",
                    col_name=col_name,
                    val=val,
                )
            )

    def delete_row(self, row: int):
        if isinstance(self.table_locator, Table) and self.controller:
            self.sleepy_send(
                TableOperation.DELETE_ROW.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    row=row,
                )
            )
        else:
            raise ValueError("controller is offline or given device, need table")

    def get_row_count_safely(self) -> int:
        row_count = self.get_num_rows()
        tries = 10
        i = 0
        while row_count.is_err() and i < tries:
            row_count = self.get_num_rows()
            i += 1
        if row_count.is_ok():
            return int(row_count.ok_value.num_response)
        else:
            raise ValueError("couldn't read row count, table might not exist")

    def add_row(self):
        """Adds a row to the provided table for currently loaded method or sequence."""
        previous_row_count = self.get_row_count_safely()
        self.sleepy_send(
            TableOperation.NEW_ROW.value.format(
                register=self.table_locator.register, table_name=self.table_locator.name
            )
        )
        new_row_count = self.get_row_count_safely()
        if previous_row_count + 1 != new_row_count:
            raise ValueError("Row could not be added.")

    def delete_table(self):
        """Deletes the table."""
        self.sleepy_send(
            TableOperation.DELETE_TABLE.value.format(
                register=self.table_locator.register, table_name=self.table_locator.name
            )
        )

    def new_table(self):
        """Creates the table."""
        self.send(
            TableOperation.CREATE_TABLE.value.format(
                register=self.table_locator.register, table_name=self.table_locator.name
            )
        )

    def get_num_rows(self) -> Result[Response, str]:
        if isinstance(self.table_locator, Table) and self.controller:
            self.send(
                Command.GET_ROWS_CMD.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    col_name=RegisterFlag.NUM_ROWS,
                )
            )
            res = self.controller.receive()
            if res.is_ok():
                return res
            else:
                return Err("No rows could be read.")
        else:
            raise ValueError(
                "controller was offline or was given a device and not a table"
            )

    def move_row(self, from_row: int, to_row: int):
        if isinstance(self.table_locator, Table) and self.controller:
            self.send(
                TableOperation.MOVE_ROW.value.format(
                    register=self.table_locator.register,
                    table_name=self.table_locator.name,
                    from_row=from_row,
                    to_row=to_row,
                )
            )
        else:
            raise ValueError("controller is offline or given device, need table")

    def _read_str_param(self, register_flag: RegisterFlag):
        if self.controller:
            try:
                return self.controller.get_text_val(
                    cmd=TableOperation.GET_OBJ_HDR_TEXT.value.format(
                        register=self.table_locator.register,
                        register_flag=register_flag,
                    )
                )
            except RuntimeError:
                return self.controller.get_text_val(
                    cmd=TableOperation.GET_OBJ_HDR_TEXT.value.format(
                        register=self.table_locator.register + "[2]",
                        register_flag=register_flag,
                    )
                )
        raise ValueError("Communication controller is not online!")

    def _read_num_param(self, register_flag: RegisterFlag):
        if self.controller:
            return self.controller.get_num_val(
                cmd=TableOperation.GET_OBJ_HDR_VAL.value.format(
                    register=self.table_locator.register,
                    register_flag=register_flag,
                )
            )
        raise ValueError("Communication controller is not online!")

    def _update_param(
        self, param: Param, register_num: Optional[int] = None, sleep: bool = True
    ):
        register = self.table_locator.register
        setting_command = (
            TableOperation.UPDATE_OBJ_HDR_VAL
            if param.ptype == PType.NUM
            else TableOperation.UPDATE_OBJ_HDR_TEXT
        )
        send_method: Callable = self.sleepy_send if sleep else self.send
        if isinstance(param.chemstation_key, list):
            for register_flag in param.chemstation_key:
                send_method(
                    setting_command.value.format(
                        register=f"{register}[{str(register_num)}]"
                        if register_num
                        else register,
                        register_flag=register_flag,
                        val=param.val,
                    )
                )
        else:
            register_flag = param.chemstation_key
            send_method(
                setting_command.value.format(
                    register=f"{register}[{str(register_num)}]"
                    if register_num
                    else register,
                    register_flag=register_flag,
                    val=param.val,
                )
            )
        self.download()
