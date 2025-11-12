

import argparse
import json
import statistics
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 18})

COLORS = ['#0173B2', '#DE8F05', '#D55E00', '#CA9161', '#56B4E9', '#F0E442', '#009E73', '#CC78BC']


def runtime_anchors(all_runtime_results, all_anchor_points, output=None):
    data = []
    counter = 0
    for runtime_results, anchor_points in zip(all_runtime_results, all_anchor_points):
        data.append([[],[],COLORS[counter]])
        for id in runtime_results.keys():
            data[-1][0].append(anchor_points[id])
            data[-1][1].append(statistics.median(runtime_results[id]))
        counter +=1
    
    fig, ax = plt.subplots()
    for dat in data:
        plt.plot(dat[0], dat[1], 'o', color=dat[2])
    ax.set_xlabel('#Anchors RT')
    ax.set_ylabel('Runtime [s]')
    plt.tight_layout()

    if output:
        plt.savefig(output)
    else:
        plt.show()
    


def anchors_HTp(all_anchor_points, all_hyperperiod_maxTp, output=None):

    data = []
    counter = 0

    for anchor_points, hyperperiod_maxTp in zip(all_anchor_points, all_hyperperiod_maxTp):
        data.append([[],[],COLORS[counter]])
        for id in anchor_points.keys():
            data[-1][0].append(hyperperiod_maxTp[id])
            data[-1][1].append(anchor_points[id])
        counter +=1
    
    fig, ax = plt.subplots()
    for dat in data:
        plt.plot(dat[0], dat[1], 'o', color=dat[2])
    ax.set_xlabel("$H(E)/max_p T_p$")
    ax.set_ylabel('#Anchors RT')
    plt.tight_layout()

    if output:
        plt.savefig(output)
    else:
        plt.show()
    

def main():

    parser = argparse.ArgumentParser(description="Plot evaluation results.")
    parser.add_argument("input", help="Results files (.jsonl)", nargs='+')
    parser.add_argument("-o", "--outputs", help="Output file to save results. OUTPUT1: Runtime - Anchors, OUTPUT2: Anchors - H(E)/max_p T_p.", nargs=2,metavar=('OUTPUT1', 'OUTPUT2'))
    parser.add_argument("-c", "--color-sep", type=int, help="Number of inputs after which the color changes.")

    args = parser.parse_args()

    if args.color_sep:
        assert args.color_sep >=1

    # Variables
    runtime_results = dict()
    anchor_points = dict()
    hyperperiod_maxTp = dict()

    all_runtime_results = []
    all_anchor_points = []
    all_hyperperiod_maxTp = []


    # Load results
    counter = 0
    for filename in args.input:
        if args.color_sep and counter >= args.color_sep:
            all_runtime_results.append(runtime_results)
            all_anchor_points.append(anchor_points)
            all_hyperperiod_maxTp.append(hyperperiod_maxTp)

            runtime_results = dict()
            anchor_points = dict()
            hyperperiod_maxTp = dict()

            counter = 0

        with open(filename, "r") as f:
            for line in f:
                res = json.loads(line.strip())
                assert "#AnchorsRT" in res, "Info in results file is missing. Run analysis with '--info' to obtain information for plotting"
                
                # Store runtime
                if res["ID"] in runtime_results:
                    runtime_results[res["ID"]].append(res["analysis_time_sec"])
                else:
                    runtime_results[res["ID"]] = [res["analysis_time_sec"]]
                
                # Store anchor points
                if res["ID"] in anchor_points:
                    assert anchor_points[res["ID"]] == res["#AnchorsRT"]
                else:
                    anchor_points[res["ID"]] = res["#AnchorsRT"]
                
                # Store hyperperiod_maxTp
                if res["ID"] in hyperperiod_maxTp:
                    assert hyperperiod_maxTp[res["ID"]] == res["H/Tp"] 
                else:
                    hyperperiod_maxTp[res["ID"]] = res["H/Tp"]
        
        counter += 1

    
    all_runtime_results.append(runtime_results)
    all_anchor_points.append(anchor_points)
    all_hyperperiod_maxTp.append(hyperperiod_maxTp)


    # Plot
    if args.outputs:
        outs = (args.outputs[0], args.outputs[1])
    else:
        outs = (None, None)
    
    runtime_anchors(all_runtime_results, all_anchor_points, outs[0])
    anchors_HTp(all_anchor_points, all_hyperperiod_maxTp, outs[1])
    

if __name__ == '__main__':
    main()