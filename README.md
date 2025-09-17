# Shape-Aware-E2E

Shape-Aware Analysis of End-to-End Latency under Logical Execution Time (LET) paradigm.


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
    ├── generate.py                     # Cause-effect chain generator
    ├── analysis.py                     # Analysis tool
    ├── plot.py                         # Plotting of runtime results
    │
    ├── chains/                         # Pre-implemented cause-effect chains
    │   ├── case_studies.jsonl              # Case studies
    │   └── paper_running_example.jsonl     # Running example used in the paper
    │
    └── automatic_eval.sh               # Script to automate the evaluation from the paper


## Quick Guide

To use the framework on your own cause-effect chains, just follow the steps:
1. Clone the repository
2. Install Python3 and the dependencies in ```requirements.txt```
3. Add a file with your cause-effect chains in ```.jsonl``` format. (You can take the file ```chains/case_studies.jsonl``` as template.)
4. Use ```python3 analysis.py your/file/name.jsonl```

More detailed instruction on [Installation](#installation) and [Usage](#usage) can be found below. 


## Installation

This implementation is tested with [Python3.12](https://www.python.org/downloads/release/python-3123/). However, other versions of Python3 should be supported as well. 
Make sure, a suitable version of Python3 is installed, e.g., by typing one of the following:
```
python3.12 --version
python3 --version
python --version
```
When Python3 is installed, follow the instructions:

### Step 1: Cloning the repository

This repository can be cloned using: 
```
git clone https://github.com/marioguenzel/Shape-Aware-E2E.git
```
This creates a folder Shape-Aware-E2E. It can be entered using 
```
cd Shape-Aware-E2E
```

### Step 2: Create a Virtual Environment (Optional)

To create a virtual environment (and avoid installing packages in your system Python3), use:
```
python3.12 -m venv venv
```
This creates a folder with the name ```venv```.
The virtual environment can be activated using
```
source venv/bin/activate
```
If you use ```which python3.12``` it should now show you the path of python in the virtual environment.

**Note:**<br>
The virtual environment has to be entered using ```source venv/bin/activate``` every time a new terminal window is started and the shape-aware analysis framework is to be used. 
The virtual environment can be deactivated manually using ```deactivate```.

### Step 3: Install Requirements

The python requirements can be installed using:
```
pip install -r requirements.txt
```

You are now ready to use the shape-aware analysis framework!


## Usage

The shape-aware analysis framework consists of three parts, discussed below. 
When during the installation process a virtual environment is created, first use ```source venv/bin/activate``` to enter the environment. 

This framework uses json-line (```.jsonl```) files, where each line represents one cause-effect chain or one result in json format. 
Examples of how these ```.jsonl``` files look like can be found in the folder ```chains/```.

The framework has three parts:
- The first is a cause-effect chain generator (```generate.py```) which creates ```.jsonl``` files using two benchmarks.
- The second is the shape-aware analyzer (```analysis.py```) which takes the cause-effect chain ```.jsonl``` files as input and prints the results. The results can optionally also be stored as ```.jsonl``` files. 
- The third is a plot generator (```plot.py```) which takes the ```.jsonl``` result files from the shape-aware anlyzer and generates plots which are shown in the paper. 

### Cause-effect chain generator

The cause-effect chain generator can be started using ```python3.12 generate.py```. 

```
usage: generate.py [-h] [--bench {WATERS,UNI}] [--tasks TASKS] [--sets SETS] [--startid STARTID] [--maxHTp MAXHTP] filename

Generate CE chains with specified benchmark and parameters.

positional arguments:
  filename              Output filename (e.g., 'chains/tests.jsonl')

options:
  -h, --help            show this help message and exit
  --bench {WATERS,UNI}  Benchmark type: WATERS or UNI (default: WATERS)
  --tasks TASKS         Number of tasks per chain (default: 5)
  --sets SETS           Number of chains to generate (default:10)
  --startid STARTID     ID of the first chain.
  --maxHTp MAXHTP       Maximal allowed value of Hyperperiod / maximal period.
```

It generates cause-effect chains and stores them in the filename as ```.jsonl``` files. 
The number of tasks per cause-effect chain can be set with the ```--tasks``` parameter, and the total number of cause-effect chains can be set with the ```--sets``` parameter.
Each cause-effect chain gets a parameter ```ID``` (counted upwards), and the first ID can be set with the ```--startid``` parameter. 
Two different benchmarks can be chosen with the ```--bench``` parameter:
- ```WATERS```: Each task period $T_i$ is drawn according to the distribution in Table III of the benchmark [1] from WATERS 2015. Please note that the probabilities only sum up to $85\%$ because $15\%$ are reserved for angle-synchronous tasks which we do not consider. Therefore, in the generation all values are divided by $0.85$. Deadlines are chosen implicit and phases are drawn uniformly at random from the set $\{0,1, ..., T_i\}$.
- ```UNI```: Each task period $T_i$ is drawn uniformly at random from the set $\{10,20, ..., 200\}$. Again, deadlines are chosen implicit and phases are drawn uniformly at random from the set $\{0,1, ..., T_i\}$.

[1] S. Kramer, D. Ziegenbein, and A. Hamann. Real world automotive benchmarks for free. In International Workshop on Analysis Tools and Methodologies for Embedded and Real-time Systems (WATERS), 2015.

To control the runtime of the experiments, a parameter ```--maxHTp``` can control the value of hyperperiod divided by the maximal period. If the value of a generated cause-effect chain exceeds the set value, the cause-effect chain is removed and a new cause-effect chain is generated until a suitable cause-effect chain is found.

**Example:**<br>
To generate $20$ cause-effect chains with UNI benchmark and store them in ```tutorial/cause_effect.jsonl```, use the following command:
```
python3.12 generate.py --bench UNI --sets 20 tutorial/cause_effect.jsonl
```




### Analysis

The analysis for given cause-effect chains can be started using ```python3.12 analysis.py```.

```
usage: analysis.py [-h] [-o OUTPUT] [--no-print] [-b BOUND] [-rb RELATIVE_BOUND] [-i] input

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
                        If set, perform (m,k) and longest exceedance analysis with the given relative bound (relative_bound * AvRT)
  -i, --info            Store additional information such as number of anchor points in the results vector.
```

The analysis takes an input file, determines the metrics described in the section on [Metrics](#metrics) and prints them to the console. 
Optionally, the results can also be stored to an output file specified with the ```--output``` parameter.
There are options ```--no-print``` to avoid the console out put (especially useful for large datasets) and ```--info``` to store additional information, which are useful for generating the plots in the next step. 
Furthermore, to soft real-time guarantees such as (m,k) and longest exceedance, a bound has to be specified. 
This can be done either using a static bound ```--bound``` or a relative bound ```--relative-bound```.

**Example:**<br>
The case studies stored in ```chains/case_studies.jsonl``` can be evaluated using:
```
python3.12 analysis.py chains/case_studies.jsonl
```
We can see the different metrics and analysis time printed to the console.
Furthermore, if the file ```tutorial/cause_effect.jsonl``` has been created in the previous step, we can prepare the results for the plotting in the subsequent step. 
For that, we need to add additional information, calculate the soft metrics and store the outputs:
```
python3.12 analysis.py --info --relative-bound 1.0 --output tutorial/results.jsonl tutorial/cause_effect.jsonl
```
We can see that a new file ```tutorial/results.jsonl``` has been created storing the analysis results.
Feel free to manually or automatically add your own cause-effect chains and apply our analysis!


### Plot generation

The runtime plots can be generated using ```python3.12 plot.py```
```
usage: plot.py [-h] [-o OUTPUTS OUTPUTS] input [input ...]

Plot evaluation results.

positional arguments:
  input                 Results files (.jsonl)

options:
  -h, --help            show this help message and exit
  -o OUTPUTS OUTPUTS, --outputs OUTPUTS OUTPUTS
                        Output file to save results.
```

The script takes multiple input files (in case multiple runtime measurements have been done), and plots the median result. 
It generates two output files, specified by the ```--outputs``` parameter.

**Example:**<br>
With the results ```tutorial/results.jsonl``` exemplary generated in the previous step, we can create plots using:
```
python3.12 plot.py -o tutorial/plot1.png tutorial/plot2.png tutorial/results.jsonl
```
This generates two plots ```tutorial/plot1.png``` ```tutorial/plot2.png``` similar to those displayed in the paper. 


## Metrics

- TODO: Write a list of all the metrics plus a short explanation

## Use Cases

- TODO: Make a list of all the use cases. Each of them is one entry in chain/case_studies.jsonl (easily identifiable with the ID field)


## Evaluation of the corresponding paper

The generation of test data, analysis and the generation of plots that are displayed in the paper is fully automated using the script ```automatic_eval.sh```.
It creates a new folder ```paperdata/``` containing all the relevant files. 


- TODO: Create automatic_eval.sh