# Shape-Aware-E2E

Shape-Aware Analysis of End-to-End Latency under Logical Execution Time (LET) paradigm.

This repository has been used to evaluate the paper "Shape-Aware Analysis of End-to-End Latency Under LET" published at RTAS 2026.

```
@inproceedings{2026/RTAS/GuenzelBC,
  author       = {Mario G{\"{u}}nzel and Matthias Becker and Daniel Casini},
  title        = {Shape-Aware Analysis of End-to-End Latency Under LET},
  booktitle    = {{RTAS}},
  publisher    = {{IEEE}},
  year         = {2026}
}
```

To reproduce the evaluation results of the paper, first follow the section [Installation](#installation) and then use the automatic evaluation script as described in section [Reproducing Evaluation Results](#reproducing-evaluation-results).
The artifact has been developed for MacOS and Linux.

The general usage of this repository (e.g., to analyze own cause-effect chains) is described in the section [General Usage](#general-usage).

## Table of Contents
- [Shape-Aware-E2E](#shape-aware-e2e)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Installation](#installation)
    - [Step 1: Cloning the repository](#step-1-cloning-the-repository)
    - [Step 2: Create a Virtual Environment](#step-2-create-a-virtual-environment)
    - [Step 3: Install Requirements](#step-3-install-requirements)
  - [Reproducing Evaluation Results](#reproducing-evaluation-results)
    - [Step 1: Make sure the installation was successful](#step-1-make-sure-the-installation-was-successful)
    - [Step 2: Start the virtual environment](#step-2-start-the-virtual-environment)
    - [Step 3: Run the automatic evaluation script](#step-3-run-the-automatic-evaluation-script)
  - [General Usage](#general-usage)
    - [Quick Guide](#quick-guide)
    - [Generating Cause-Effect Chains](#generating-cause-effect-chains)
    - [Analyzing Cause-Effect Chains](#analyzing-cause-effect-chains)
    - [Further Components](#further-components)
    - [Metrics](#metrics)
    - [Use Cases](#use-cases)
  - [Acknowledgment](#acknowledgment)



## About

This project allows the analysis of multiple [metrics](#metrics) regarding the end-to-end latency of cause-effect chains. 
Tasks are assumed to communicate using the Logical Execution Time (LET) paradigm, i.e., the read and write operations occur periodically with given offsets (i.e., at release and at deadline).
The project is composed of the following files:

    Shape-Aware-E2E/
    │
    ├── README.md                       # Project documentation
    ├── requirements.txt                # Python dependencies
    ├── LICENSE                         # License file
    │
    ├── generate.py                     # Synthetic cause-effect chain generator
    ├── analysis.py                     # Analysis tool
    │
    ├── chains/                         # Pre-implemented cause-effect chains
    │   ├── case_studies.jsonl              # Case studies
    │   └── paper_running_example.jsonl     # Running example used in the paper
    │
    ├── compare_methods.py              # Literature analyses for comparison
    ├── plot.py                         # Plotting of relation between runtime and anchor points
    ├── plot_runtimecomparison.py       # Plotting of runtime comparison with literature results
    ├── make_table.py                   # Script to generate a latex table for the case-study results
    └── automatic_eval.sh               # Script to automate the evaluation from the paper


## Installation

This implementation is tested with [Python3.12](https://www.python.org/downloads/release/python-3123/). However, other versions of Python3 should be supported as well. 
Make sure, a suitable version of Python3 is installed, e.g., by typing the following:
```
python3.12 --version
```
When Python3 is installed, follow the instructions:

### Step 1: Cloning the repository

First, download the repository.
Alternatively, the repository can be cloned using: 
```
git clone https://github.com/marioguenzel/Shape-Aware-E2E.git
```
This creates a folder `Shape-Aware-E2E'. 
It can be entered using 
```
cd Shape-Aware-E2E
```

### Step 2: Create a Virtual Environment

To create a virtual environment (and avoid installing packages in your system Python3), use:
```
python3.12 -m venv venv
```
This creates a folder with the name ```venv```.
The virtual environment can be activated using
```
source venv/bin/activate
```
If you use ```which python3``` it should now show you the path of python in the virtual environment.

**Note:**<br>
The virtual environment has to be entered using ```source venv/bin/activate``` every time a new terminal window is started and the shape-aware analysis framework is to be used. 
The virtual environment can be deactivated manually using ```deactivate```.

### Step 3: Install Requirements

The python requirements can be installed using:
```
pip install -r requirements.txt
```

You are now ready to use the shape-aware analysis framework!


## Reproducing Evaluation Results

The generation of test data, analysis and the generation of plots that are displayed in the paper is fully automated using the script ```automatic_eval.sh```.
It creates a new folder ```AutomaticEval/``` containing all the relevant files. 

### Step 1: Make sure the installation was successful

Before reproducing the results, section [Installation](#installation) should be completed.
When running the command `ls`, you should be able to see the files of this repository (such as this `README.md`) as well as the folder `venv` which has been created during the installation process.

### Step 2: Start the virtual environment

Run the command 
```
source venv/bin/activate
```
to activate the virtual environment. 
To check whether that was successful, when running `which python3`, it should display `<your-path>/venv/bin/python3`.

**Note:**<br>
It is important that the command `python3` works correctly, because this command is utilized in `automatic_eval.sh`.

### Step 3: Run the automatic evaluation script

To run the evaluation script, simply use:
```
bash automatic_eval.sh
```
Please note that this command will use 50 cores in parallel and run for multiple hours.
If your hardware is not powerful enough or just a **quick test of reproducibility** is required, the command
```
bash automatic_eval.sh 0
```
can be used. This will start a simplified version of the experiment. 
The configuration for running the experiment can be changed by modifying the first few lines of `automatic_eval.sh`:
```
NUM_ITERATIONS=50  # number of runs for the time measurements of the synthetic evaluation
TASKSETS_PER_CONFIG=1000  # number of tasksets per configuration for the runtime evaluation
PARALLELIZE=true  # Parallelize the iterations
```

By running the script a new folder `AutomaticEval` will be created, which contains:
- `CaseStudies`: The results from the case studies (cf. Section VIII.A).
- `RuntimeComparison`: The generated chains and results for the runtime comparison with enumeration-based analysis methods (cf. Section VIII.B).
- `Relation`: The generated chains and results for the evaluation of the relation between rutime and anchor points (cf. Section VIII.C).
- `paperdata`: Files, table and stats that have been reported in the paper.

The contents of the paper correspond to the following files:

| Paper Content | File |
|---|---|
| Table II | `paperdata/case_studies.tex` |
| Figure 3.a | `paperdata/runtime_comparison_waters_05.png` |
| Figure 3.b | `paperdata/runtime_comparison_waters_20.png` |
| Figure 3.c | `paperdata/runtime_comparison_waters_50.png` |
| Figure 4.a | `paperdata/runtime_comparison_uni_05.png` |
| Figure 4.b | `paperdata/runtime_comparison_uni_20.png` |
| Figure 4.c | `paperdata/runtime_comparison_uni_50.png` |
| Figure 5.a | `paperdata/UNI_runtime.png` |
| Figure 5.b | `paperdata/UNI_anchors.png` |




## General Usage

This section describes the general usage of the shape-aware analysis framework. 
It is structured as follows:
- [Quick Guide](#quick-guide): A quick description how to run shape-aware analysis on your own cause-effect chains.
- [Generating Cause-Effect Chains](#generating-cause-effect-chains): Description of how to generate synthetic cause-effect chains.
- [Analyzing Cause-Effect Chains](#analyzing-cause-effect-chains): Explains the analysis of given cause-effect chains.
- [Further Components](#further-components): Details the usage of further components.
- [Metrics](#metrics): Overview of the metrics that can be analyzed with this repository.
- [Use Cases](#use-cases): Overview of the use cases that are aggregated in the file `chains/case_studies.jsonl`.


### Quick Guide

To use the framework on your own cause-effect chains, just follow the steps:
1. Clone the repository
2. Install Python3 and the dependencies in ```requirements.txt```
3. Add a file with your cause-effect chains in ```.jsonl``` format. (You can take the file ```chains/case_studies.jsonl``` as template.)
4. Use ```python3 analysis.py your/file/name.jsonl```

More detailed instruction can be found in the sections [Installation](#installation) and [Full Guide](#full-guide). 


### Generating Cause-Effect Chains

Cause-effect chains are stored in json-line (```.jsonl```) files, where each line represents one cause-effect chain or one result in json format. 
Examples of how these ```.jsonl``` files look like can be found in the folder ```chains/```.
The generation of synthetic cause-effect chains is implemented in ```generate.py```, creating ```.jsonl``` files using two benchmarks (WATERS and UNIFORM).
The cause-effect chain generator can be started using ```python3 generate.py```:
```
usage: generate.py [-h] [--bench {WATERS,UNI}] [--tasks TASKS] [--sets SETS] [--startid STARTID] [--maxH MAXH] [--maxHTp MAXHTP] filename

Generate CE chains with specified benchmark and parameters.

positional arguments:
  filename              Output filename (e.g., 'chains/tests.jsonl')

options:
  -h, --help            show this help message and exit
  --bench {WATERS,UNI}  Benchmark type: WATERS or UNI (default: WATERS)
  --tasks TASKS         Number of tasks per chain (default: 5)
  --sets SETS           Number of chains to generate (default:10)
  --startid STARTID     ID of the first chain.
  --maxH MAXH           Maximal allowed value of Hyperperiod. (For generator UNIFORM only.)
  --maxHTp MAXHTP       Maximal allowed value of Hyperperiod / maximal period. (For generator UNIFORM only.)
```

It generates cause-effect chains and stores them in the filename as `.jsonl` files. 
The number of tasks per cause-effect chain can be set with the `--tasks` parameter, and the total number of cause-effect chains can be set with the `--sets` parameter.
Each cause-effect chain gets a parameter `ID` (counted upwards), and the first ID can be set with the `--startid` parameter. 
Two different benchmarks can be chosen with the `--bench` parameter:
- `WATERS`: Each task period $T_i$ is drawn according to the distribution in Table III of the benchmark [1] from WATERS 2015. Please note that the probabilities only sum up to $85\%$ because $15\%$ are reserved for angle-synchronous tasks which we do not consider. Therefore, in the generation all values are divided by $0.85$. Deadlines are chosen implicit and phases are drawn uniformly at random from the set $\{0,1, ..., T_i\}$.
- `UNI`: Each task period $T_i$ is drawn uniformly at random from the set $\{10,20, ..., 200\}$. Again, deadlines are chosen implicit and phases are drawn uniformly at random from the set $\{0,1, ..., T_i\}$.

[1] S. Kramer, D. Ziegenbein, and A. Hamann. Real world automotive benchmarks for free. In International Workshop on Analysis Tools and Methodologies for Embedded and Real-time Systems (WATERS), 2015.

To control the runtime of the experiments, the parameters `--maxH` or `--maxHTp` can be used to limit the hyperperiod or the value of hyperperiod divided by the maximal period, respectively. If a generated cause-effect chain exceeds the specified value, the cause-effect chain is removed and a new cause-effect chain is generated until a suitable cause-effect chain is found.

**Example:**<br>
To generate $20$ cause-effect chains with UNI benchmark and store them in ```tutorial/cause_effect.jsonl```, use the following command:
```
python3 generate.py --bench UNI --sets 20 tutorial/cause_effect.jsonl
```

### Analyzing Cause-Effect Chains

Given that (one or multiple) cause-effect chains are stored in a `.jsonl` file, `analysis.py` can be utilized to analyze them using the shape-aware analysis framework.
The analysis for a file `<my-chains>.jsonl` can be started using `python3 analysis.py <my-chains>.jsonl`:
```
usage: analysis.py [-h] [-o OUTPUT] [--no-print] [-b BOUND] [-rb RELATIVE_BOUND] [-i] [-t TIMEOUT] input

Analyze CEChains from JSONL file.

positional arguments:
  input                 Input file (.jsonl)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file to save results (optional)
  --no-print            Do not print results to stdout
  -b BOUND, --bound BOUND
                        If set, perform (m,k) and longest exceedance analysis with the given bound
  -rb RELATIVE_BOUND, --relative-bound RELATIVE_BOUND
                        If set, perform (m,k) and longest exceedance analysis with the given relative bound (relative_bound * MaxRT)
  -i, --info            Store additional information such as number of anchor points in the results vector.
  -t TIMEOUT, --timeout TIMEOUT
                        Set a timeout in seconds.
```

The analysis takes an input file, determines the metrics described in the section on [Metrics](#metrics) and prints them to the console. 
Optionally, the results can also be stored to an output file specified with the `--output` parameter.
There are options `--no-print` to avoid the console out put (especially useful for large datasets) and `--info` to store additional information, which are useful for generating the plots in the next step. 
Furthermore, to give soft real-time guarantees such as (m,k) and longest exceedance, a bound has to be specified. 
This can be done either using a static bound `--bound` or a relative bound `--relative-bound`.
A timeout for the analysis (in seconds) can be set using `--timeout`.

**Example:**<br>
The case studies stored in `chains/case_studies.jsonl` can be evaluated using:
```
python3 analysis.py chains/case_studies.jsonl
```
We can see the different metrics and analysis time printed to the console.
Furthermore, if the file `tutorial/cause_effect.jsonl` has been created in the previous step, we can prepare the results for the plotting in the subsequent step. 
For that, we need to add additional information, calculate the soft metrics and store the outputs:
```
python3 analysis.py --info --relative-bound 1.0 --output tutorial/results.jsonl tutorial/cause_effect.jsonl
```
We can see that a new file `tutorial/results.jsonl` has been created storing the analysis results.


### Further Components

Multiple other python components are used, mainly to achieve the plots presented in the paper. The components are listed below. 
In general, using the `-h` option shows an instruction how to utilize the corresponding component. 
Furthermore, a peak into the `automatic_eval.sh`-file can demonstrate how components can be utilized correctly. 

- `plot.py`: The script takes multiple input files (in case multiple runtime measurements have been done), and plots the median result. It generates two output files, specified by the `--outputs` parameter, to show the relation between anchor points and runtime. With the results `tutorial/results.jsonl` exemplary generated in the previous steps, we can create plots using:
`python3 plot.py -o tutorial/plot1.png tutorial/plot2.png tutorial/results.jsonl`
This generates two plots `tutorial/plot1.png` `tutorial/plot2.png` similar to those displayed in the paper. 
- `compare_methods.py`: Analyzes cause-effect chains using literature results. Input and output file have to be specified, and a timeout can optionally be set using the `--timeout` parameter.
- `plot_runtimecomparison.py`: Plots a runtime comparison similar to the plots presented in the paper. It allows specifying multiple inputs using `-i <method-name> <keyword-in-inputfile> <inputfile1>.jsonl [<inputfile2>.jsonl ...]`. Inside the inputfiles, the runtime is stored under the keyword `<keyword-in-inputfile>`. When multiple inputfiles are specified, the median runtime among all inputfiles is taken. Multiple methods can be specified by using the `-i` parameter multiple times.

**Note**<br>
The component `make_table.py` is only used to generate the table presented in the paper and is not meant to be applied for a general analysis usage. (Hence, it does not have a `-h` parameter for example.)

### Metrics

Using our shape-aware analysis, the following metrics can be analyzed:

| Paper | Metric | Keyword | Short Description | Note |
|-|-|-|-|-|
| Section VI.B | Maximum reaction time | `MaxRT` | Type of maximum end-to-end latency | -- |
| Section VI.B | Maximum reduced reaction time | `MaxRedRT` | Type of maximum end-to-end latency | -- |
| Section VI.B | Reactive time | `Reac` | Type of maximum end-to-end latency | -- |
| Section VI.B | Minimum reaction time | `MinRT` | Type of minimum end-to-end latency | -- |
| Section VI.C | Average latency | `AvRT` | The average reaction time over one hyperperiod assuming uniform distribution. | -- |
| Section VI.D | Throughput | `throughp` | Rate of data samples that are processed without being overwritten. | -- |
| Section VI.E | Weakly-hard (m,k) | `mkRT` | (m,k) constraints that are fulfilled for reaction time. | A bound for comparison has to be specified. |
| Section VI.F | Longest consecutive exceedance | `LE-RT` | Longest interval that the reaction time exceeds a specified bound. | A bound for comparison has to be specified. |


### Use Cases

The following use-cases are listed in `chain/case_studies.jsonl`:

| Paper | Description | IDs |
|-|-|-|
| Hamann et al., "WATERS industrial challenge", WATERS 2017.<br> https://www.ecrts.org/forum/download/WATERS2017_Industrial_Challenge_Bosch.pdf | The two chains with periodic tasks. | WATERS16/17 EffectChain1; WATERS16/17 EffectChain2 |
| Rehm et al., "Performance modeling of heterogeneous HW platforms", Microprocessors and Microsystems 2021.<br> https://dl.acm.org/doi/abs/10.1016/j.micpro.2021.104336 | Six chains from the WATERS 2019 Challenge prototype of a next-generation advanced driving assistance system by Bosch. (More detailed description in the paper.) | WATERS2019, LG->LOC->EKF->Planner->DASM; WATERS2019, CAN->LOC->EKF->Planner->DASM; WATERS2019, CAN->EKF->Planner->DASM; WATERS2019, SFM->Planner->DASM; WATERS2019, LaneDet->Planner->DASM; WATERS2019, Detection->Planner->DASM |
| PerceptIn, "RTSS 2021 industry challenge", RTSS 2021<br> https://2021.rtss.org/wp-content/uploads/2021/06/RTSS2021-Industry-Challenge-v2.pdf | The five chains from the autonomous driving system. | RTSS 2021 - 1 - mmWaveRadar; RTSS 2021 - 2 - camera; RTSS 2021 - 3 - Lidar(long); RTSS 2021 - 4 - Lidar(short); RTSS 2021 - 5 - GNSS/IMU |
| Bellassai et al., "AP-LET: Enabling deterministic pub/sub communication in autosar adaptive", Journal of Systems Architecture 2025.<br> https://dl.acm.org/doi/abs/10.1016/j.sysarc.2025.103390 | The chain of the AUTOSAR Adaptive Platform brake assistant Demonstrator application. | AUTOSAR-Adaptive Brake Assistant |
| Becker and Casini, "The material framework: Modeling and automatic code generation of edge real-time applications under the qnx rtos", Journal of Systems Architecture 2024.<br> https://dl.acm.org/doi/abs/10.1016/j.sysarc.2024.103219 | The chain from the Brake-By-Wire application of a Swedish automotive Original Equipment Manufacturer (OEM). | Brake-By-Wire JSA 2024 |
| Gemlau et al., "System-level logical execution time: Augmenting the logical execution time paradigm for distributed real-time automotive software", ACM Trans. Cyber-Phys. Syst. 2021.<br> https://dl.acm.org/doi/abs/10.1145/3381847 | A powertrain application. | Gemlau TCPS 2021 Fig. 7a, upper path; Gemlau TCPS 2021 Fig. 7a, lower path |
| Iyenghar et al., "Automated end-to-end timing analysis of autosar-based causal event chains", ENASE 2020.<br> https://www.scitepress.org/Papers/2020/95129/95129.pdf | An Autonomous Emergency Braking System case study. | Iyenghar ENASE 2020, Figure 7 |
| Frey, "Case Study: Engine Control Application. Technical report", University Ulm 2010.<br> http://www.uni-ulm.de/fileadmin/website_uni_ulm/iui/Ulmer_Informatik_Berichte/2010/UIB-2010-03.pdf | Four chains from the engine control application case study. | Frey 2010: Tech. report, Fig. 10 1st path from top; Frey 2010: Tech. report, Fig. 10 2nd path from top; Frey 2010: Tech. report, Fig. 10 3rd path from top, angleSync with 10ms period; Frey 2010: Tech. report, Fig. 10 4rd path from top, angleSync with 10ms period |
| Pagetti et al., "The ROSACE case study: From simulink specification to multi/many-core execution", RTAS 2014.<br> https://ieeexplore.ieee.org/abstract/document/6926012 | The two chains of the ROSACE avionics case study of a flight controller. | ROSACE - 1 - h_filter->altitude_hold->Vz_control; ROSACE - 2 - x_filter->x_control |

## Acknowledgment

This result is part of a project (PropRT) that has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme (grant agreement No. 865170).
This work has been funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) -- Project No. 569077889 (PEACH).
This work was partially funded by the Swedish Research Council (VR) under the project nr. 2023-04773 and by Sweden's Innovation Agency via the NFFP8 project 2024-01267: PARTI.
This work has been partially supported by the project SERICS (PE00000014) under the MUR National Recovery and Resilience Plan funded by the European Union -- NextGenerationEU.