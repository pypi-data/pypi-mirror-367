# pychemstation: A Python package for automated control of Chemstation using MACROs

![PyPI - Downloads](https://img.shields.io/pypi/dm/pychemstation)

[![PyPI Latest Release](https://img.shields.io/pypi/v/pychemstation.svg)](https://pypi.org/project/pychemstation/)

> **_NOTE:_** If you are running Python **3.8**, use versions 0.**8**.x. If you are running Python **3.9** use versions 0.**9**.x.
> If you are running Python **>=3.10**, use version 0.**10**.x. Older versions of pychemstation are not the most feature-rich and bug-free. Please consider upgrading to using Python 3.10!

Unofficial Python package to control Agilent Chemstation; we are not affiliated with Agilent.
Check out the [docs](https://pychemstation-e5a086.gitlab.io/pychemstation.html) for usage instructions. This project is under
active development, and breaking changes may occur at any moment.

## Getting started

Before running this library, these are the steps you need to complete.

### Add python package

```bash
pip install pychemstation
```

### Add required MACRO script

1. Open ChemStation
2. Run this in the ChemStation command line: ``Print _AutoPath$``. Go to this path in your file navigator, as this is
   where you will put your
   MACRO file(s).
3. Download the [
   `hplc_talk.mac`](https://gitlab.com/heingroup/device-api/pychemstation/-/blob/main/tests/hplc_talk.mac).
    - On line 69, change the path name up to `\cmd` and `\reply`. For instance, you should have:
      `MonitorFile "[my path]\cmd", "[my path]\reply"`
    - and then add this file to the folder from the previous step.
4. To have these MACRO files be read by ChemStation, you must either:
    - Open ChemStation and run:

```MACRO
macro hplc_talk.mac
HPLCTalk_Run
```

- OR add the above lines to a MACRO file named: `user.mac`, and then put `user.mac` in the same folder from step 3.
    - ChemStation will automatically load these MACRO files for you. However, sometimes this does not work, and if it
      does not, you will have to run the lines in the `user.mac` manually.

## Example Usage

```python
import time
from pychemstation.control import HPLCController
from pychemstation.utils.method_types import *
import pandas as pd

DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
CUSTOM_DATA_DIR = "C:\\Users\\Public\\Documents\\ChemStation\\2\\Data\\MyData"

# Initialize HPLC Controller
hplc_controller = HPLCController(extra_data_dirs=[CUSTOM_DATA_DIR],
                                 comm_dir=DEFAULT_COMMAND_PATH)

# Switching a method
hplc_controller.switch_method("General-Poroshell")

# Editing a method
new_method = MethodDetails(
    name="General-Poroshell",
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
            start_time=4,
            organic_modifer=99,
            flow=0.55
        )
    ],
    stop_time=5,
    post_time=2
)
hplc_controller.edit_method(new_method)

# Run a method and get a report or data from last run method
hplc_controller.run_method(experiment_name="test_experiment", stall_while_running=False)
time_left, done = hplc_controller.check_method_complete()
while not done:
    print(time_left)
    time.sleep(time_left/2)
    time_left, done = hplc_controller.check_method_complete()
    
# Save the path the HPLC data for later!  
file_path = hplc_controller.get_last_run_method_file_path()

# Make sure CSV reports are being generated in the post-run MACRO!
report = hplc_controller.get_last_run_method_report()
vial_location = report.vial_location

# Save, analyze or plot the data!
chrom = hplc_controller.get_last_run_method_data()
chromatogram_data = pd.DataFrame.from_dict({"x": chrom.A.x, "y": chrom.A.y})
chromatogram_data.to_csv("Run 10.csv", index=False) 
```

## Adding your own MACROs

If you wish to add your own MACRO functions, then all you need to do is write you MACRO (using Agilent's) MACRO guide,
put the file in the `user.mac` file and then list the function you want to use.

## Developing

If you would like to contribute to this project, check out
our [GitLab](https://gitlab.com/heingroup/device-api/pychemstation)!

## Authors and Acknowledgements

Lucy Hao, Maria Politi

- Adapted from [**AnalyticalLabware**](https://github.com/croningp/analyticallabware), created by members in the Cronin
  Group. Copyright © Cronin Group, used under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.
- Adapted from the [MACROS](https://github.com/Bourne-Group/HPLCMethodOptimisationGUI) used in [**Operator-free HPLC
  automated method development guided by Bayesian optimization**](https://pubs.rsc.org/en/content/articlelanding/2024/dd/d4dd00062e),
  created by members in the Bourne Group. Copyright © Bourne Group, used under
  the [MIT](https://opensource.org/license/mit) license.