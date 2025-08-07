from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


@dataclass
class Response:
    """Class representing a response from Chemstation"""

    string_response: str
    num_response: Union[int, float]


# Commands sent to the Chemstation Macro
# See https://www.agilent.com/cs/library/usermanuals/Public/MACROS.PDF
class Command(Enum):
    def __str__(self):
        return "%s" % self.value

    GET_NUM_VAL_CMD = "response_num = {cmd}"
    GET_TEXT_VAL_CMD = "response$ = {cmd}"
    RESET_COUNTER_CMD = "last_cmd_no = 0"
    GET_STATUS_CMD = "response$ = AcqStatus$"
    SLEEP_CMD = "Sleep {seconds}"
    STANDBY_CMD = "Standby"
    STOP_MACRO_CMD = "Stop"
    PREPRUN_CMD = "PrepRun"

    # Instrument Control
    LAMP_ON_CMD = "LampAll ON"
    LAMP_OFF_CMD = "LampAll OFF"
    PUMP_ON_CMD = "PumpAll ON"
    PUMP_OFF_CMD = "PumpAll OFF"
    COLUMN_ON_CMD = "ColumnAll ON"
    COLUMN_OFF_CMD = "ColumnAll OFF"
    INSTRUMENT_OFF = 'macro "SHUTDOWN.MAC" ,go'
    INSTRUMENT_ON = 'LIDoOperation "TURN_ON"'

    # Method and Sequence Related
    GET_METHOD_CMD = "response$ = _MethFile$"
    GET_ROWS_CMD = 'response_num = TabHdrVal({register}, "{table_name}", "{col_name}")'
    SWITCH_METHOD_CMD = "LoadMethod _MethPath$, _MethFile$"
    SWITCH_METHOD_CMD_SPECIFIC = 'LoadMethod "{method_dir}", "{method_name}.M"'
    START_METHOD_CMD = "StartMethod"
    RUN_METHOD_CMD = 'RunMethod "{data_dir}",, "{experiment_name}"'
    STOP_METHOD_CMD = "StopMethod"
    UPDATE_METHOD_CMD = "UpdateMethod"
    SWITCH_SEQUENCE_CMD = "LoadSequence _SeqPath$, _SeqFile$"
    SAVE_SEQUENCE_CMD = "SaveSequence _SeqPath$, _SeqFile$"
    SAVE_METHOD_CMD = 'SaveMethod _MethPath$, _MethFile$, "{commit_msg}"'
    GET_SEQUENCE_CMD = "response$ = _SeqFile$"
    RUN_SEQUENCE_CMD = "RunSequence"
    CURRENT_RUNNING_SEQ_LINE = "response_num = _SEQCURRLINE1"

    # Get directories
    GET_METHOD_DIR = "response$ = _METHPATH$"
    GET_SEQUENCE_DIR = "response$ = _SEQUENCEPATHS$"
    CONFIG_MET_PATH = "_CONFIGMETPATH"
    CONFIG_SEQ_PATH = "_CONFIGSEQPATH"
    GET_RUNNING_SEQUENCE_DIR = "response$ = _SEQPATHS$"
    GET_DATA_DIRS = "response$ = _DATAPATHS$"
    GET_CURRENT_RUN_DATA_DIR = "response$ = _DATAPath$"
    GET_CURRENT_RUN_DATA_FILE = "response$ = _DATAFILE1$"

    # Errors
    ERROR = "response$ = _ERRMSG$"


class HPLCRunningStatus(Enum):
    @classmethod
    def has_member_key(cls, key):
        return key in cls.__members__

    INJECTING = "INJECTING"
    PREPARING = "PREPARING"
    RUN = "RUN"
    NOTREADY = "NOTREADY"
    POSTRUN = "POSTRUN"
    RAWDATA = "RAWDATA"
    INITIALIZING = "INITIALIZING"
    NOMODULE = "NOMODULE"


class HPLCAvailStatus(Enum):
    @classmethod
    def has_member_key(cls, key):
        return key in cls.__members__

    PRERUN = "PRERUN"
    OFFLINE = "OFFLINE"
    STANDBY = "STANDBY"


class HPLCErrorStatus(Enum):
    @classmethod
    def has_member_key(cls, key):
        return key in cls.__members__

    ERROR = "ERROR"
    BREAK = "BREAK"
    NORESPONSE = "NORESPONSE"
    MALFORMED = "MALFORMED"


def str_to_status(
    status: str,
):
    if HPLCErrorStatus.has_member_key(status):
        return HPLCErrorStatus[status]
    if HPLCRunningStatus.has_member_key(status):
        return HPLCRunningStatus[status]
    if HPLCAvailStatus.has_member_key(status):
        return HPLCAvailStatus[status]
    raise KeyError(status)


Status = Union[HPLCRunningStatus, HPLCAvailStatus, HPLCErrorStatus]
