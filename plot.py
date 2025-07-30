

import argparse
import json
import statistics
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 18})


def runtime_anchors(runtime_results, anchor_points, output=None):
    data_points_x = []
    data_points_y = []
    for id in runtime_results.keys():
        data_points_x.append(anchor_points[id])
        data_points_y.append(statistics.median(runtime_results[id]))
    
    fig, ax = plt.subplots()
    plt.plot(data_points_x, data_points_y, 'o')
    ax.set_xlabel('#Anchors RT')
    ax.set_ylabel('Runtime [s]')
    plt.tight_layout()

    if output:
        plt.savefig(output)
    else:
        plt.show()
    


def anchors_HTp(anchor_points, hyperperiod_maxTp, output=None):
    data_points_x = []
    data_points_y = []
    for id in anchor_points.keys():
        data_points_x.append(hyperperiod_maxTp[id])
        data_points_y.append(anchor_points[id])
    
    fig, ax = plt.subplots()
    plt.plot(data_points_x, data_points_y, 'o')
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
    parser.add_argument("-o", "--outputs", help="Output file to save results.", nargs=2)

    args = parser.parse_args()

    # Load results
    runtime_results = dict()
    anchor_points = dict()
    hyperperiod_maxTp = dict()
    for filename in args.input:
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

    # Plot
    if args.outputs:
        outs = (args.outputs[0], args.outputs[1])
    else:
        outs = (None, None)
    
    runtime_anchors(runtime_results, anchor_points, outs[0])
    anchors_HTp(anchor_points, hyperperiod_maxTp, outs[1])
    

if __name__ == '__main__':
    main()