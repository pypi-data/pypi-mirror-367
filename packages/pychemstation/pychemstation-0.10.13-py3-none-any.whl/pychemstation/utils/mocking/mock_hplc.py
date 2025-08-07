from ..macro import HPLCAvailStatus, Status
from ..method_types import MethodDetails, HPLCMethodParams, TimeTableEntry
from ..sequence_types import SequenceTable, SequenceEntry, InjectionSource
from ..tray_types import FiftyFourVialPlate


class MockHPLC:
    def __init__(self):
        self.current_method: MethodDetails = MethodDetails(
            name="General-Poroshell",
            params=HPLCMethodParams(organic_modifier=5, flow=0.65),
            timetable=[TimeTableEntry(start_time=3, organic_modifer=99, flow=0.65)],
            stop_time=5,
            post_time=2,
        )
        self.current_sequence: SequenceTable = SequenceTable(
            name="hplc_testing",
            rows=[
                SequenceEntry(
                    vial_location=FiftyFourVialPlate.from_str("P1-A2"),
                    sample_name="sample1",
                    data_file="sample1",
                    method="General-Poroshell",
                    num_inj=1,
                    inj_vol=1,
                    inj_source=InjectionSource.HIP_ALS,
                )
            ],
        )
        self.current_status: Status = HPLCAvailStatus.STANDBY
