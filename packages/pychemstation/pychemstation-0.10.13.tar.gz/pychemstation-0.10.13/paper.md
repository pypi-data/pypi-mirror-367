---
title: 'pychemstation: A Python package for automated control of Chemstation using MACROs'
tags:
  - Python
  - Self Driving Labs
  - SDL
  - HPLC
  - Automation
authors:
  - name: Lucy Hao
    email: lucyhao@chem.ubc.ca
    orcid: 0000-0003-0296-3591
    affiliation: 1
  - name: Maria Politi
    email: politim@chem.ubc.ca
    orcid: 0000-0002-5815-3371
    affiliation: "1, 3"
  - name: Jason Hein
    email: jhein@chem.ubc.ca
    orcid: 0000-0002-4345-3005
    affiliation: "1, 2, 3, 4"
affiliations:
  - name: Department of Chemistry, The University of British Columbia, Vancouver, Canada
    index: 1
  - name: Department of Chemistry, University of Bergen, Norway
    index: 2
  - name: Acceleration Consortium, University of Toronto, Toronto, ON, Canada
    index: 3
  - name: Telescope Innovations Corp., Vancouver, BC, Canada
    index: 4
date: 17 April 2025
bibliography: paper.bib
---

# Summary

`pychemstation` is a Python package that automates the use of high-performance liquid chromatography (HPLC) machines using
Chemstation [@ChromatographyMethodDevelopment]. Python enables easy adoption by chemists and integrates smoothly with
existing data analysis and robotics packages used in developing automated chemical workflows. The `pychemstation` API
provides users with a simple class-based interface to automate common operations such as running analytical methods and
sequences, modifying methods and sequences, and extracting chromatograms after runs. `pychemstation` provides this functionality by generating MACROs (a command
protocol developed by Agilent) which are sent to ChemStation for execution. With HPLC being one of the most widely
used analytical methods in research and industry, `pychemstation` opens the doors to using this powerful analytical technique in automated chemical workflows.

# Statement of need

Chemists run hundreds of analytical measurements to gain insight into chemical reactions. 
This amounts to hours of manual labour to interact with graphical user interfaces (GUIs) to modify analytical methods,
run the methods, and then extract data to gain scientific insight. Tasks such as these are amenable to automation, leading to a broader research
goal to automate experiments through self-driving labs (SDLs) [@robertsAutomatingStochasticAntibody2025; @DynamicSamplingAutonomous].
SDLs are robotic platforms that autonomously plan and execute hundreds of chemical reactions. Building an SDL requires
every step a chemist would do by hand to be automated, one of them being the running of analytical equipment such as HPLC. 
Building autonomous chemical requires the development of robust software tools that enable control and communication with analytical hardware.

`pychemstation` was designed to be used by chemists to control Agilent-specific HPLC machines in their day-to-day
operations or in developing SDLs. The development of `pychemstation` stemmed from the desire for a 
robust strategy to interact with Chemstation, moving away from the fragile and cumbersome development of the “mouse and
keyboard” interaction strategy with the GUI. Development began from the augmentation of an existing Python codebase for
sending MACROs to Chemstation, with addition more MACROs through trial-and-error and previous published work 
[@CroningpAnalyticallabware2025; @dixonOperatorfreeHPLCAutomated2024a; @BourneGroupHPLCMethodOptimisationGUIHPLCl; @schneiderMacroProgrammingGuide].
`pychemstation` has already been used in several of the Hein group's projects, including SDLs for kinetics,
liquid-liquid extraction and development of a Python based tool for autonomous data-driven HPLC method
development [@AccelerationConsortium; @HeinGroupHplcmethodoptimization2025]. Built with robustness and ease-of-use in
mind, `pychemstation` frees the chemist from repetitive tasks and gives SDL developers the ability to seamlessly interact with
HPLC machines through an API, enhancing productivity and enabling more efficient software integration.

# Description

`pychemstation` controls the operation of Chemstation through a set of `Controller` classes which generate MACROs based
on Python dataclasses. A schematic describing the package architecture is shown below in figure 1.

![A class architecture diagram for `pychemstation`. The
`CommunicationController` handles all communication between a user's Python program and a Chemstation instance. All other controllers extend an abstract
`ABCTableController` which provides table loading and editing functionality all controllers require. The
`RunController` is another abstract class including more functionality related to editing and triggering a run/runs.
`RunController` also provides a polling functionality to let the user know when a run is complete, and returns the file paths containing the data from the run. The
`DeviceController` load and edit details about hardware.](imgs/control.png)

MACROs enabling functionality beyond method editing were discovered using a MACRO editor and Chemstation's built in
MACRO help [@schneiderMacroProgrammingGuide; @ChromatographyMethodDevelopment].
Python tests were written to ensure proper functionality of all the methods available in the `HPLCController` class that
most users interact with, shown in figure 2. These tests include both unit (testing the individual controller
classes) and integration tests (such as editing of methods and running them immediately after with retrieval of run
data). Tests were run on two different HPLC machines in the Hein group.

![All methods available for use in the `HPLCController` class](imgs/hplc.png)

The `HPLCController` class contains a series of subclasses of `RunController` and `DeviceController`. 
`RunController` subclasses, `MethodController` and `SequenceController`, generate MACROs related to runs, 
such as triggering runs and returning data. The `DeviceController` subclasses are a new edition, allowing users to load 
details about the injector, diode array detector, column/thermostat and pumps. The subclasses extending 
`DeviceController` are in active development.

The `RunController` subclasses provide `pychemstation`'s main functionality. The `MethodController` triggers method runs for one sample, while the `SequenceController` can trigger a runf o
After a run is triggered, the `RunController` can either block until the HPLC is done the run or immediately return. If the user
chooses to return before the HPLC is done a run, they choose to check how much time is remaining for the run. After the
run, the `RunController` returns all the necessary file paths for further data processing. The UV chromatogram is returned per active channel, or for the entire
scanned spectrum. There is limited data processing functionality for the auto-generated report in the `ReportProcessor`
classes, thus other Python libraries are recommended for more in depth processing.

The `MethodController` edits the pump timetable while the `SequenceController` edits the sequence table. An example is
shown below. Various combinations of parameters and editing scenarios were tested to ensure the generated MACROs could
handle different types of parameter updates.

![An example of a Method pump timetable](imgs/method%20timetable.png)
![An example of a Sequence table](imgs/img.png)

A summary of available methods and functionality are shown in the tables below.

| Run Controller | Features                                                                                                   |
|----------------|------------------------------------------------------------------------------------------------------------|
| Sequence       | Switch, Load sequence details, Edit sequence table entries, Run sequence, Retrieve sequence run data files |
| Method         | Switch, Load method timetable, Edit method timetable, Run method, Retrieve method run data files           |

| Device Controller    | Features                                                                            |
|----------------------|-------------------------------------------------------------------------------------|
| Pump                 | Edit parameters (flow, pressure, organic modifier), solvent and waste bottle status |
| Diode Array Detector | Read and set active wavelengths                                                     |
| Injector             | Change injection volume                                                             |
| Columns              | Read active column, edit active column                                              |

Thus, `pychemstation` provides both high-level and low-level control of an HPLC machine that uses Agilent's Chemstation
software. More information and use case examples can be found in
the [documentation](https://pychemstation-e5a086.gitlab.io/pychemstation.html).

# Acknowledgements

We acknowledge contributions from Wesley McNutt, Matthew Reish and Clark Zhang and funding support from AC, NSERC,
Canada
NRC,
CFFI (?).

# References
