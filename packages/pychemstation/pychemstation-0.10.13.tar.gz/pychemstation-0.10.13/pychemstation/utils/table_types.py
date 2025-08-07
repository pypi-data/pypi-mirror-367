from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeVar


class TableOperation(Enum):
    """
    MACROS related to editing and reading tables in Chemstation.
    """

    def __str__(self):
        return "%s" % self.value

    DELETE_TABLE = 'DelTab {register}, "{table_name}"'
    CREATE_TABLE = 'NewTab {register}, "{table_name}"'
    NEW_ROW = 'InsTabRow {register}, "{table_name}"'
    NEW_ROW_SPECIFIC = 'InsTabRow {register}, "{table_name}"'
    MOVE_ROW = 'MoveTabRow {register}, "{table_name}", {from_row}, {to_row}'
    DELETE_ROW = 'DelTabRow {register}, "{table_name}", {row}'
    EDIT_ROW_VAL = 'SetTabVal "{register}", "{table_name}", {row}, "{col_name}", {val}'
    EDIT_ROW_TEXT = (
        'SetTabText "{register}", "{table_name}", {row}, "{col_name}", "{val}"'
    )
    GET_ROW_VAL = 'TabVal("{register}", "{table_name}", {row}, "{col_name}")'
    GET_ROW_TEXT = 'TabText$("{register}", "{table_name}", {row}, "{col_name}")'
    GET_NUM_ROWS = 'Rows = TabHdrVal({register}, "{table_name}", "{col_name}")'
    GET_OBJ_HDR_VAL = 'ObjHdrVal("{register}", "{register_flag}")'
    GET_OBJ_HDR_TEXT = 'ObjHdrText$("{register}", "{register_flag}")'
    UPDATE_OBJ_HDR_VAL = 'SetObjHdrVal "{register}", "{register_flag}", {val}'
    UPDATE_OBJ_HDR_TEXT = 'SetObjHdrText "{register}", "{register_flag}", "{val}"'
    NEW_COL_TEXT = 'NewColText {register}, "{table_name}", "{col_name}", "{val}"'
    NEW_COL_VAL = 'NewColVal {register}, "{table_name}", "{col_name}", {val}'


class RegisterFlag(Enum):
    """
    Flags for accessing Chemstation parameters.
    """

    def __str__(self):
        return "%s" % self.value

    # sample info
    VIAL_NUMBER = "VialNumber"

    # for table
    NUM_ROWS = "NumberOfRows"

    # for Method
    SOLVENT_A_COMPOSITION = "PumpChannel_CompositionPercentage"
    SOLVENT_B_COMPOSITION = "PumpChannel2_CompositionPercentage"
    SOLVENT_C_COMPOSITION = "PumpChannel3_CompositionPercentage"
    SOLVENT_D_COMPOSITION = "PumpChannel4_CompositionPercentage"
    FLOW = "Flow"
    MAX_TIME = "StopTime_Time"
    POST_TIME = "PostTime_Time"
    COLUMN_OVEN_TEMP1 = "TemperatureControl_Temperature"
    COLUMN_OVEN_TEMP2 = "TemperatureControl2_Temperature"
    STOPTIME_MODE = "StopTime_Mode"
    POSTIME_MODE = "PostTime_Mode"
    TIME = "Time"
    TIMETABLE_SOLVENT_B_COMPOSITION = "SolventCompositionPumpChannel2_Percentage"
    TIMETABLE_FLOW = "FlowFlow"

    # for Method Timetable
    SOLVENT_COMPOSITION = "SolventComposition"
    PRESSURE = "Pressure"
    EXTERNAL_CONTACT = "ExternalContact"
    FUNCTION = "Function"

    # for Sequence
    VIAL_LOCATION = "Vial"
    NAME = "SampleName"
    METHOD = "Method"
    INJ_VOL = "InjVolume"
    INJ_SOR = "InjectionSource"
    NUM_INJ = "InjVial"
    SAMPLE_TYPE = "SampleType"
    DATA_FILE = "DataFileName"

    # for Injector Table
    ## Draw
    DRAW_SOURCE = "DrawSource"
    DRAW_VOLUME = "DrawVolume_Mode"
    DRAW_SPEED = "DrawSpeed_Mode"
    DRAW_OFFSET = "DrawOffset_Mode"
    DRAW_VOLUME_VALUE = "DrawVolume_Value"
    DRAW_LOCATION = "DrawLocation"
    DRAW_LOCATION_TRAY = "DrawLocationPlus_Tray"
    DRAW_LOCATION_UNIT = "DrawLocationPlus_Unit"
    DRAW_LOCATION_ROW = "DrawLocationPlus_Row"
    DRAW_LOCATION_COLUMN = "DrawLocationPlus_Column"
    ## Inject
    ## Wait
    ## Remote
    REMOTE = "RemoteLine"
    REMOTE_DUR = "RemoteDuration"
    # Injection Volume
    INJECTION_VOLUME = "Injection_Volume"

    ## For Pump
    ### Volume Status
    BOTTLE_A1_ABSOLUTE_FILLING = "BottleFilling_CurrentAbsolute"
    BOTTLE_A1_PERCENT_FILLING = "BottleFilling_CurrentPercent"
    BOTTLE_A1_MAX = "BottleFilling_MaximumAbsolute"

    BOTTLE_A2_ABSOLUTE_FILLING = "BottleFilling2_CurrentAbsolute"
    BOTTLE_A2_PERCENT_FILLING = "BottleFilling2_CurrentPercent"
    BOTTLE_A2_MAX = "BottleFilling2_MaximumAbsolute"

    BOTTLE_B1_ABSOLUTE_FILLING = "BottleFilling3_CurrentAbsolute"
    BOTTLE_B1_PERCENT_FILLING = "BottleFilling3_CurrentPercent"
    BOTTLE_B1_MAX = "BottleFilling3_MaximumAbsolute"

    BOTTLE_B2_ABSOLUTE_FILLING = "BottleFilling4_CurrentAbsolute"
    BOTTLE_B2_PERCENT_FILLING = "BottleFilling4_CurrentPercent"
    BOTTLE_B2_MAX = "BottleFilling4_MaximumAbsolute"

    WASTE_BOTTLE_ABSOLUTE = "WasteBottleFilling_CurrentAbsolute"
    WASTE_BOTTLE_PERCENT = "WasteBottleFilling_CurrentPercent"
    WASTE_BOTTLE_MAX = "WasteBottleFilling_MaximumPercent"

    ### Switching Solvent Bottles
    PUMPCHANNEL_USED = "PumpChannel_IsUsed"
    PUMPCHANNEL_SELECTION = "PumpChannel_SolventSelectionValvePosition"
    BOTTLE_A1_USER_NAME = "PumpChannel_Position1_UserName"
    BOTTLE_A2_USER_NAME = "PumpChannel_Position2_UserName"
    PUMPCHANNEL2_USED = "PumpChannel_IsUsed"
    PUMPCHANNEL2_SELECTION = "PumpChannel2_SolventSelectionValvePosition"
    BOTTLE_B1_USER_NAME = "PumpChannel2_Position1_UserName"
    BOTTLE_B2_USER_NAME = "PumpChannel2_Position2_UserName"

    # For Column
    AVAIL_COLUMN_DISPLAY_VALUES = "ColumnSwitchingValve_PositionDisplayValues"
    AVAIL_COLUMN_POSITIONS = "ColumnSwitchingValve_PositionValues"
    COLUMN_POSITION = "ColumnSwitchingValve_Position"

    # For DAD
    SIGNAL_A = "Signal_Wavelength"
    SIGNAL_B = "Signal2_Wavelength"
    SIGNAL_C = "Signal3_Wavelength"
    SIGNAL_D = "Signal4_Wavelength"
    SIGNAL_E = "Signal5_Wavelength"
    SIGNAL_A_USED = "Signal_IsUsed"
    SIGNAL_B_USED = "Signal2_IsUsed"
    SIGNAL_C_USED = "Signal3_IsUsed"
    SIGNAL_D_USED = "Signal4_IsUsed"
    SIGNAL_E_USED = "Signal5_IsUsed"


@dataclass
class Table:
    """
    Class for storing the keys needed to access certain register tables.
    """

    register: str
    name: str


@dataclass
class Device:
    """
    Class for storing the keys needed to access certain devices
    """

    register: str


T = TypeVar("T")
