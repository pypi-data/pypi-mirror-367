from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AnalogOutput1:
    analog_zero: Optional[int] = field(
        default=None,
        metadata={
            "name": "AnalogZero",
            "type": "Element",
            "required": True,
        },
    )
    analog_att: Optional[int] = field(
        default=None,
        metadata={
            "name": "AnalogAtt",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class AnalogOutput2:
    analog_zero: Optional[int] = field(
        default=None,
        metadata={
            "name": "AnalogZero",
            "type": "Element",
            "required": True,
        },
    )
    analog_att: Optional[int] = field(
        default=None,
        metadata={
            "name": "AnalogAtt",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PostTime:
    post_time_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "PostTimeMode",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PrepareAutomation:
    do_prep_run_balance: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DoPrepRunBalance",
            "type": "Element",
            "required": True,
        },
    )
    do_start_run_balance: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DoStartRunBalance",
            "type": "Element",
            "required": True,
        },
    )
    do_post_run_balance: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DoPostRunBalance",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PrepareMode:
    balance_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "BalanceMode",
            "type": "Element",
            "required": True,
        },
    )
    headroom: Optional[int] = field(
        default=None,
        metadata={
            "name": "Headroom",
            "type": "Element",
            "required": True,
        },
    )
    smpgain: Optional[int] = field(
        default=None,
        metadata={
            "name": "SMPGain",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Signal:
    use_signal: Optional[bool] = field(
        default=None,
        metadata={
            "name": "UseSignal",
            "type": "Element",
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Element",
            "required": True,
        },
    )
    wavelength: Optional[int] = field(
        default=None,
        metadata={
            "name": "Wavelength",
            "type": "Element",
        },
    )
    bandwidth: Optional[int] = field(
        default=None,
        metadata={
            "name": "Bandwidth",
            "type": "Element",
        },
    )
    use_reference: Optional[bool] = field(
        default=None,
        metadata={
            "name": "UseReference",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SpectraAcquisition:
    spectra_range_from: Optional[int] = field(
        default=None,
        metadata={
            "name": "SpectraRangeFrom",
            "type": "Element",
            "required": True,
        },
    )
    spectra_range_to: Optional[int] = field(
        default=None,
        metadata={
            "name": "SpectraRangeTo",
            "type": "Element",
            "required": True,
        },
    )
    spectra_step: Optional[int] = field(
        default=None,
        metadata={
            "name": "SpectraStep",
            "type": "Element",
            "required": True,
        },
    )
    spectra_acq_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "SpectraAcqMode",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class StopTime:
    stop_time_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "StopTimeMode",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Signals:
    signal: List[Signal] = field(
        default_factory=List,
        metadata={
            "name": "Signal",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class DadMethod:
    module_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModuleType",
            "type": "Attribute",
            "required": True,
        },
    )
    schema_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemaVersion",
            "type": "Attribute",
            "required": True,
        },
    )
    schema_si: Optional[int] = field(
        default=None,
        metadata={
            "name": "schemaSI",
            "type": "Attribute",
            "required": True,
        },
    )
    module_options: Optional[object] = field(
        default=None,
        metadata={
            "name": "ModuleOptions",
            "type": "Attribute",
            "required": True,
        },
    )
    configuration_xml: Optional[str] = field(
        default=None,
        metadata={
            "name": "ConfigurationXml",
            "type": "Element",
            "required": True,
        },
    )
    timetable: Optional[object] = field(
        default=None,
        metadata={
            "name": "Timetable",
            "type": "Element",
        },
    )
    stop_time: Optional[StopTime] = field(
        default=None,
        metadata={
            "name": "StopTime",
            "type": "Element",
            "required": True,
        },
    )
    post_time: Optional[PostTime] = field(
        default=None,
        metadata={
            "name": "PostTime",
            "type": "Element",
            "required": True,
        },
    )
    delay: Optional[int] = field(
        default=None,
        metadata={
            "name": "Delay",
            "type": "Element",
            "required": True,
        },
    )
    analog_output1: Optional[AnalogOutput1] = field(
        default=None,
        metadata={
            "name": "AnalogOutput1",
            "type": "Element",
            "required": True,
        },
    )
    analog_output2: Optional[AnalogOutput2] = field(
        default=None,
        metadata={
            "name": "AnalogOutput2",
            "type": "Element",
            "required": True,
        },
    )
    signals: Optional[Signals] = field(
        default=None,
        metadata={
            "name": "Signals",
            "type": "Element",
            "required": True,
        },
    )
    peakwidth: Optional[int] = field(
        default=None,
        metadata={
            "name": "Peakwidth",
            "type": "Element",
            "required": True,
        },
    )
    slitwidth: Optional[int] = field(
        default=None,
        metadata={
            "name": "Slitwidth",
            "type": "Element",
            "required": True,
        },
    )
    uvlamp_required: Optional[bool] = field(
        default=None,
        metadata={
            "name": "UVLampRequired",
            "type": "Element",
            "required": True,
        },
    )
    vislamp_required: Optional[bool] = field(
        default=None,
        metadata={
            "name": "VISLampRequired",
            "type": "Element",
            "required": True,
        },
    )
    prepare_mode: Optional[PrepareMode] = field(
        default=None,
        metadata={
            "name": "PrepareMode",
            "type": "Element",
            "required": True,
        },
    )
    prepare_automation: Optional[PrepareAutomation] = field(
        default=None,
        metadata={
            "name": "PrepareAutomation",
            "type": "Element",
            "required": True,
        },
    )
    spectra_acquisition: Optional[SpectraAcquisition] = field(
        default=None,
        metadata={
            "name": "SpectraAcquisition",
            "type": "Element",
            "required": True,
        },
    )
