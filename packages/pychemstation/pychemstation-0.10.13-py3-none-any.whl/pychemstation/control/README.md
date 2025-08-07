# Examples of usecases

```python
from pychemstation.control import HPLCController

DEFAULT_METHOD_DIR = "C:\\ChemStation\\1\\Methods\\"
SEQUENCE_DIR = "C:\\USERS\\PUBLIC\\DOCUMENTS\\CHEMSTATION\\3\\Sequence"
DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
DATA_DIR_2 = "C:\\Users\\Public\\Documents\\ChemStation\\2\\Data"
DATA_DIR_3 = "C:\\Users\\Public\\Documents\\ChemStation\\3\\Data"

# Initialize HPLC Controller
hplc_controller = HPLCController(extra_data_dirs=[DATA_DIR_2, DATA_DIR_3],
                                 comm_dir=DEFAULT_COMMAND_PATH,
                                 method_dir=DEFAULT_METHOD_DIR,
                                 sequence_dir=SEQUENCE_DIR)

# Switching a method
hplc_controller.switch_method("General-Poroshell")

# Editing a method
from pychemstation.utils.method_types import *

new_method = MethodDetails(
    name="My_Method",
    params=HPLCMethodParams(
        organic_modifier=7,
        flow=0.44),
    timetable=[
        TimeTableEntry(
            start_time=0.10,
            organic_modifer=7,
            flow=0.34
        ),
        TimeTableEntry(
            start_time=1,
            organic_modifer=99,
            flow=0.55
        )
    ],
    stop_time=5,
    post_time=2
)
hplc_controller.edit_method(new_method)

# Run a method and get a report or data from last run method
hplc_controller.run_method(experiment_name="test_experiment")
chrom = hplc_controller.get_last_run_method_data()
channel_a_time = chrom.A.x
report = hplc_controller.get_last_run_method_report()
vial_location = report.vial_location

# switch the currently loaded sequence
hplc_controller.switch_sequence(sequence_name="hplc_testing")

# edit the sequence table
from pychemstation.utils.tray_types import *
from pychemstation.utils.sequence_types import *

seq_table = SequenceTable(
    name="hplc_testing",
    rows=[
        SequenceEntry(
            vial_location=FiftyFourVialPlate.from_str("P1-A1"),
            method="General-Poroshell",
            num_inj=3,
            inj_vol=4,
            sample_name="Control",
            sample_type=SampleType.CONTROL,
            inj_source=InjectionSource.MANUAL
        ),
        SequenceEntry(
            vial_location=VialBar.ONE,
            method="General-Poroshell",
            num_inj=1,
            inj_vol=1,
            sample_name="Sample",
            sample_type=SampleType.SAMPLE,
            inj_source=InjectionSource.AS_METHOD
        ),
        SequenceEntry(
            vial_location=FiftyFourVialPlate.from_str("P2-B4"),
            method="General-Poroshell",
            num_inj=3,
            inj_vol=4,
            sample_name="Blank",
            sample_type=SampleType.BLANK,
            inj_source=InjectionSource.HIP_ALS
        ),
    ]
)
hplc_controller.edit_sequence(seq_table)

# Run a sequence and get data or report from last run sequence
hplc_controller.run_sequence()
chroms = hplc_controller.get_last_run_sequence_data(read_uv=True)
row_1_channel_A_abs = chroms[0][210].y
report = hplc_controller.get_last_run_sequence_reports()
vial_location_row_1 = report[0].vial_location
```