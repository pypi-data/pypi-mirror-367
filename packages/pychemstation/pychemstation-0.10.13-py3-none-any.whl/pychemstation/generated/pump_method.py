from dataclasses import dataclass, field
from typing import List, Optional
from xml.etree.ElementTree import QName


@dataclass
class CompressA:
    compressibility_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompressibilityMode",
            "type": "Element",
            "required": True,
        },
    )
    compressibility_value_set: Optional[int] = field(
        default=None,
        metadata={
            "name": "CompressibilityValueSet",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class CompressB:
    compressibility_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompressibilityMode",
            "type": "Element",
            "required": True,
        },
    )
    compressibility_value_set: Optional[int] = field(
        default=None,
        metadata={
            "name": "CompressibilityValueSet",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Definition:
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
            "required": True,
        },
    )
    is_pure: Optional[bool] = field(
        default=None,
        metadata={
            "name": "IsPure",
            "type": "Element",
            "required": True,
        },
    )
    crc: Optional[int] = field(
        default=None,
        metadata={
            "name": "CRC",
            "type": "Element",
            "required": True,
        },
    )
    solvent_stripes: List[str] = field(
        default_factory=List,
        metadata={
            "name": "SolventStripes",
            "type": "Element",
            "min_occurs": 1,
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
    post_time_value: Optional[int] = field(
        default=None,
        metadata={
            "name": "PostTimeValue",
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
    stop_time_value: Optional[int] = field(
        default=None,
        metadata={
            "name": "StopTimeValue",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class StrokeA:
    automatic_stroke_calculation: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AutomaticStrokeCalculation",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class TimetableEntry:
    type_value: Optional[QName] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": "http://www.w3.org/2001/XMLSchema-instance",
            "required": True,
        },
    )
    object_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ObjectID",
            "type": "Attribute",
            "required": True,
        },
    )
    time: Optional[float] = field(
        default=None,
        metadata={
            "name": "Time",
            "type": "Element",
            "required": True,
        },
    )
    percent_a: Optional[int] = field(
        default=None,
        metadata={
            "name": "PercentA",
            "type": "Element",
            "required": True,
        },
    )
    percent_b: Optional[int] = field(
        default=None,
        metadata={
            "name": "PercentB",
            "type": "Element",
            "required": True,
        },
    )
    percent_c: Optional[int] = field(
        default=None,
        metadata={
            "name": "PercentC",
            "type": "Element",
            "required": True,
        },
    )
    percent_d: Optional[int] = field(
        default=None,
        metadata={
            "name": "PercentD",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SolventDescription:
    definition: Optional[Definition] = field(
        default=None,
        metadata={
            "name": "Definition",
            "type": "Element",
            "required": True,
        },
    )
    percent: Optional[int] = field(
        default=None,
        metadata={
            "name": "Percent",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Timetable:
    timetable_entry: List[TimetableEntry] = field(
        default_factory=List,
        metadata={
            "name": "TimetableEntry",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Channel1ExtendedSolventType:
    mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Element",
            "required": True,
        },
    )
    solvent_description: Optional[SolventDescription] = field(
        default=None,
        metadata={
            "name": "SolventDescription",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Channel2ExtendedSolventType:
    mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Element",
            "required": True,
        },
    )
    solvent_description: Optional[SolventDescription] = field(
        default=None,
        metadata={
            "name": "SolventDescription",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SolventElement:
    channel: Optional[str] = field(
        default=None,
        metadata={
            "name": "Channel",
            "type": "Element",
            "required": True,
        },
    )
    channel1_user_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Channel1UserName",
            "type": "Element",
            "required": True,
        },
    )
    channel2_user_name: Optional[object] = field(
        default=None,
        metadata={
            "name": "Channel2UserName",
            "type": "Element",
        },
    )
    selected_solvent_channel: Optional[str] = field(
        default=None,
        metadata={
            "name": "SelectedSolventChannel",
            "type": "Element",
            "required": True,
        },
    )
    used: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Used",
            "type": "Element",
            "required": True,
        },
    )
    percentage: Optional[int] = field(
        default=None,
        metadata={
            "name": "Percentage",
            "type": "Element",
            "required": True,
        },
    )
    channel1_extended_solvent_type: Optional[Channel1ExtendedSolventType] = field(
        default=None,
        metadata={
            "name": "Channel1ExtendedSolventType",
            "type": "Element",
            "required": True,
        },
    )
    channel2_extended_solvent_type: Optional[Channel2ExtendedSolventType] = field(
        default=None,
        metadata={
            "name": "Channel2ExtendedSolventType",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SolventComposition:
    solvent_element: List[SolventElement] = field(
        default_factory=List,
        metadata={
            "name": "SolventElement",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class PumpMethod:
    module_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModuleType",
            "type": "Attribute",
            "required": True,
        },
    )
    xsd_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "xsdName",
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
    timetable: Optional[Timetable] = field(
        default=None,
        metadata={
            "name": "Timetable",
            "type": "Element",
            "required": True,
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
    flow: Optional[float] = field(
        default=None,
        metadata={
            "name": "Flow",
            "type": "Element",
            "required": True,
        },
    )
    use_solvent_types: Optional[bool] = field(
        default=None,
        metadata={
            "name": "UseSolventTypes",
            "type": "Element",
            "required": True,
        },
    )
    stroke_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "StrokeMode",
            "type": "Element",
            "required": True,
        },
    )
    stroke_a: Optional[StrokeA] = field(
        default=None,
        metadata={
            "name": "StrokeA",
            "type": "Element",
            "required": True,
        },
    )
    compress_a: Optional[CompressA] = field(
        default=None,
        metadata={
            "name": "CompressA",
            "type": "Element",
            "required": True,
        },
    )
    compress_b: Optional[CompressB] = field(
        default=None,
        metadata={
            "name": "CompressB",
            "type": "Element",
            "required": True,
        },
    )
    solvent_composition: Optional[SolventComposition] = field(
        default=None,
        metadata={
            "name": "SolventComposition",
            "type": "Element",
            "required": True,
        },
    )
    low_pressure_limit: Optional[int] = field(
        default=None,
        metadata={
            "name": "LowPressureLimit",
            "type": "Element",
            "required": True,
        },
    )
    high_pressure_limit: Optional[int] = field(
        default=None,
        metadata={
            "name": "HighPressureLimit",
            "type": "Element",
            "required": True,
        },
    )
    maximum_flow_ramp: Optional[int] = field(
        default=None,
        metadata={
            "name": "MaximumFlowRamp",
            "type": "Element",
            "required": True,
        },
    )
    flow_ramp_down: Optional[int] = field(
        default=None,
        metadata={
            "name": "FlowRampDown",
            "type": "Element",
            "required": True,
        },
    )
    expected_mixer_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ExpectedMixerType",
            "type": "Element",
            "required": True,
        },
    )
