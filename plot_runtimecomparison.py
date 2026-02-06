

import argparse
import json
import statistics
from typing import List
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

plt.rcParams.update({'font.size': 18})

COLORS = ['#0173B2', '#DE8F05', '#D55E00', '#CA9161', '#56B4E9', '#F0E442', '#009E73', '#CC78BC']


def plot(data: List[List[float]], xticks=None, output=None, title='', yticks=None, ylimits=None, yscale='linear', yaxis_label=""):
    """Create a boxplot which displays given data (e.g., runtime of multiple methods)."""

    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.boxplot(data,
               boxprops=dict(linewidth=4, color='blue'),
               medianprops=dict(linewidth=4, color='red'),
               whiskerprops=dict(linewidth=4, color='black'),
               capprops=dict(linewidth=4),
               whis=[0, 100])

    if xticks is not None:
        plt.xticks(list(range(1, len(xticks) + 1)), xticks)
    else:
        plt.xticks([])

    if yticks is not None:
        plt.yticks(yticks)
    if ylimits is not None:
        ax.set_ylim(ylimits)

    plt.yscale(yscale)

    ax.tick_params(axis='x', rotation=0, labelsize=20)
    ax.tick_params(axis='y', rotation=0, labelsize=20)

    ax.set_ylabel(yaxis_label, fontsize=20)

    plt.grid(True, color='lightgray', which='both', axis='y', linestyle='-')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)

    plt.tight_layout()  # improve margins for example for yaxis_label

    if output:
        fig.savefig(output)
    else:
        plt.show()


def main():

    # == Argparse ==
    parser = argparse.ArgumentParser(description="Boxplot to compare runtime.")
    parser.add_argument('-i','--input',action='append',nargs='+',
    metavar=('ARG'),help='(Arguments: Methodname runtime-keyword resultfile [resultfile ...]) First argument needs to be the method name to be specified (later shown as boxplotlabel). Second argument is the keyword used in the result files to specify the corresponding runtime. Third (and following) arguments are the input files as .jsonl. If multiple result files are given, then the median runtime is displayed. Example: -i OurMethod OurRuntimeKeyword results1.jsonl results2.jsonl')
    parser.add_argument("-o", "--output", help="Output file to save boxplot.", nargs=1, metavar=('outputfile.png'))

    args = parser.parse_args()

    # == Load input ==
    if args.input is None:
        print("No input specified. (Check help with '-h' for explanation how to load input.)")
        return None
    
    data = []
    names = []
    for entry in args.input:
        name = entry[0]
        keyword = entry[1]
        filenames = entry[2:]

        # Read first file to determine number of lines
        per_line = []
        with open(filenames[0], "r") as f:
            for line in f:
                res = json.loads(line)
                per_line.append([res[keyword]])

        # Process remaining files
        for filename in filenames[1:]:
            with open(filename, "r") as f:
                for i, line in enumerate(f):
                    res = json.loads(line)
                    per_line[i].append(res[keyword])

        # Median across files for each line
        this_data = [statistics.median(values) for values in per_line]

        # Store values
        data.append(this_data)
        names.append(name)
    
    # == Plot data ==
    out = args.output[0] if args.output else None
    plot(data, xticks=names, output=out)
    

if __name__ == '__main__':
    main()