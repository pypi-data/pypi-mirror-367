import os
import random
import shutil

from pychemstation.control import HPLCController
from pychemstation.utils.macro import Command
from pychemstation.utils.method_types import (
    HPLCMethodParams,
    MethodDetails,
    TimeTableEntry,
)
from pychemstation.utils.sequence_types import SampleType, SequenceEntry
from pychemstation.utils.tray_types import FiftyFourVialPlate, VialBar

VIAL_PLATES = [
    FiftyFourVialPlate.from_str("P1-A7"),
    FiftyFourVialPlate.from_str("P1-B4"),
    FiftyFourVialPlate.from_str("P1-C2"),
    FiftyFourVialPlate.from_str("P1-D8"),
    FiftyFourVialPlate.from_str("P1-E3"),
    FiftyFourVialPlate.from_str("P1-F5"),
    # plate 2
    FiftyFourVialPlate.from_str("P2-A7"),
    FiftyFourVialPlate.from_str("P2-B2"),
    FiftyFourVialPlate.from_str("P2-C1"),
    FiftyFourVialPlate.from_str("P2-D8"),
    FiftyFourVialPlate.from_str("P2-E3"),
    FiftyFourVialPlate.from_str("P2-F6"),
]

DEFAULT_METHOD = "GENERAL-POROSHELL-OPT"
DEFAULT_METHOD_242 = "GENERAL-POROSHELL-JD"
DEFAULT_METHOD_254 = "GENERAL-POROSHELL-30sec_Isohold"
DEFAULT_SEQUENCE = "hplc_testing"

# CONSTANTS: paths only work in Hein group HPLC machine in room 242
# DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
DEFAULT_COMMAND_PATH = os.getcwd()

# these CONSTANTS work in rm 254
DEFAULT_COMMAND_PATH_254 = "D:\\git_repositories\\hplc_comm\\"


def room(num: int):
    if num == 242:
        return DEFAULT_COMMAND_PATH
    elif num == 254:
        return DEFAULT_COMMAND_PATH_254
    else:
        return os.getcwd()


def gen_rand_method():
    org_modifier = int(random.random() * 10)
    max_run_time = int(random.random() * 10)
    post_run_time = int(random.random() * 10)
    flow = float(random.random() * 10) / 10
    flow_1 = float(random.random() * 10) / 10
    flow_2 = float(random.random() * 10) / 10
    return MethodDetails(
        name=DEFAULT_METHOD,
        timetable=[
            TimeTableEntry(start_time=0.10, organic_modifer=org_modifier, flow=flow_1),
            TimeTableEntry(
                start_time=1,
                organic_modifer=100 - int(random.random() * 10),
                flow=flow_2,
            ),
        ],
        stop_time=max_run_time,
        post_time=post_run_time,
        params=HPLCMethodParams(organic_modifier=org_modifier, flow=flow),
    )


seq_entry = SequenceEntry(
    vial_location=VialBar.ONE,
    method=DEFAULT_METHOD,
    num_inj=int(random.random() * 10),
    inj_vol=int(random.random() * 10),
    sample_name="Test",
    data_file="Test",
    sample_type=SampleType(int(random.random() * 3)),
)


def set_up_utils(
    num: int, offline: bool = False, runs: bool = False, mock: bool = True
) -> HPLCController:
    comm_dir = room(num)
    if not offline:
        if not os.path.exists(comm_dir):
            raise FileNotFoundError(
                f"{comm_dir} does not exist on your system. If you would like to run tests, please change this path."
            )

    controller = HPLCController(
        offline=offline,
        comm_dir=comm_dir,
        debug=True,
    )
    if not offline:
        controller.send(
            Command.SAVE_METHOD_CMD.value.format(
                commit_msg="method saved by pychemstation"
            )
        )
        controller.send(Command.SAVE_SEQUENCE_CMD)
        if runs:
            controller.instrument_on()
            controller.preprun()
        else:
            controller.instrument_off()
    return controller


def clean_up(hplc_controller: HPLCController):
    if hasattr(hplc_controller.method_controller, "data_dirs") and hasattr(
        hplc_controller.sequence_controller, "data_dirs"
    ):
        files = hplc_controller.method_controller.data_files + [
            d.dir for d in hplc_controller.sequence_controller.data_files
        ]
        data_dirs = hplc_controller.method_controller.data_dirs
        for folder in files:
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                for data_dir in data_dirs:
                    possible_path = os.path.join(data_dir, folder)
                    if os.path.isdir(possible_path):
                        shutil.rmtree(possible_path)
