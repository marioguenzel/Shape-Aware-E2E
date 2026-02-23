
import math
import json
import random
import os
import itertools
import sys
import time
import argparse

import signal


class TimeoutError(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutError



MKRange = (1,10)  # Range of k for (m,k) to be evaluated

##########
# Tasks and Cause-Effect Chains
##########

class Task:
    """A simple task."""
    def __init__(self, phase, period, deadline):
        self.phase = phase
        self.period = period
        self.deadline = deadline

    def re(self, idx: int):
        # Read-event of job idx.
        return self.phase + idx * self.period

    def we(self, idx: int):
        # Read-event of job idx.
        return self.phase + idx * self.period + self.deadline
    
    def let_re_geq(self,time):
        """Index of earliest job with read-event no earlier than 'time'."""
        return max(math.ceil((time - self.phase) / self.period), 0)
    
    def let_we_leq(self, time):
        """Index of latest job with write-event no later than 'time'. If this value becomes negative, there is no such job."""
        return math.floor((time - self.phase - self.deadline) / self.period)

class CEChain:
    """A Cause-Effect Chain."""
    def __init__(self, *tasks: Task, id: int = None):
        self.tasks = tasks
        self.id = id if id is not None else random.randint(1000, 9999)

        self.hyperperiod = None
        self.warmup = None
        self.starttimes = None
        self.anchorsRT = None  # Minimal anchor points in $overline I'_{RT}$

    def calc_hyperperiod(self):
        """Calculate and store hyperperiod parameter."""
        self.hyperperiod = math.lcm(*[tsk.period for tsk in self.tasks])
    
    def _immfw(self, taskidx, jobidx):
        # Calculate immediate forward job chain starting from taskidx and jobidx.
        jobchain = [jobidx,]
        for i in range(taskidx, len(self.tasks)-1):
            thistask = self.tasks[i]
            nexttask = self.tasks[i+1]
            # find next job and append to job chain
            jobidx = nexttask.let_re_geq(thistask.we(jobidx))
            jobchain.append(jobidx)
        assert len(jobchain) == len(self.tasks)-taskidx
        return jobchain

    def _immbw(self, taskidx, jobidx):
        # Calculate immediate backward job chain starting from taskidx and jobidx.
        jobchain = [jobidx]
        for i in range(taskidx, 0, -1):
            thistask = self.tasks[i]
            prevtask = self.tasks[i-1]
            # find previous job and prepend to job chain
            jobidx = prevtask.let_we_leq(thistask.re(jobidx))
            jobchain.insert(0, jobidx)
        assert len(jobchain) == taskidx + 1
        return jobchain
    
    def _part(self, taskidx, jobidx):
        # Calculate a partitioned job chain.
        return (self._immbw(taskidx,jobidx), self._immfw(taskidx,jobidx+1))

    def calc_warmup(self):
        # Calculate warmup values and the start times where RT and DA become well-defined.
        firstfw = self._immfw(0,0)
        firstbw = self._immbw(len(self.tasks) - 1, firstfw[-1])
        
        self.warmup = firstbw
        self.starttimes = (self.tasks[0].re(self.warmup[0]), self.tasks[-1].we(self.warmup[-1]))
    
    def calc_anchors(self, p=None):
        """Calculate anchor points during the interval $overline I'$."""
        if p is None:
            # Find index with maximal period
            p = max(range(len(self.tasks)), key=lambda i: self.tasks[i].period)
        # Check if warm up and hyperperiod is defined.
        if self.warmup is None:
            self.calc_warmup()
        if self.hyperperiod is None:
            self.calc_hyperperiod()

        # List of anchor points
        anchorsRT = list()
        
        # Find anchor points over first hyperperiod
        assert self.hyperperiod/self.tasks[p].period == self.hyperperiod//self.tasks[p].period
        for jobidx in range(self.warmup[p],self.warmup[p]+self.hyperperiod//self.tasks[p].period):
            # Calculate partitioned job chain
            part = self._part(p, jobidx)
            partstart = self.tasks[0].re(part[0][0])
            partend = self.tasks[-1].we(part[-1][-1])

            # If there is already such a point, keep the highest one
            if len(anchorsRT) != 0 and anchorsRT[-1][0] == partstart:
                anchorsRT[-1] = (partstart,max(anchorsRT[-1][1], partend-partstart))
            else:
                anchorsRT.append((partstart, partend-partstart))
        
        def repeatentry(entry):
            return (entry[0] + self.hyperperiod, entry[1])

        # == RT anchors ==
        def redundantRT(entry1,entry2):
            """Returns True if entry2 is redundant"""
            return entry1[1] - entry2[1] == entry2[0] - entry1[0]

        # Repeat first entry (First entry can potentially be non-redundant later on)
        anchorsRT.append(repeatentry(anchorsRT[0]))
        
        # Find anchor points in I 
        anchorsRTfromI = []
        for idx in range(len(anchorsRT) - 1):
            if not redundantRT(anchorsRT[idx], anchorsRT[idx+1]):
                anchorsRTfromI.append(anchorsRT[idx+1])
        anchorsRTfromI.append(repeatentry(anchorsRTfromI[0]))

        assert len(anchorsRTfromI)>1
        assert redundantRT(anchorsRTfromI[-2], anchorsRTfromI[-1]) is False

        # == Store anchors ==
        self.anchorsRT = anchorsRTfromI  # Careful: The anchor on the starttime might be artificial, i.e., not needed when describing later hyperperiods.


##########
# Data Handling
##########


def ensure_filepath_exists(filepath: str):
    """Check if a filepath exists and create it if it doesn't."""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def save_chain_as_json(chain: CEChain, filepath: str):
    """Save CEChain object as JSON. Just stores the chain without the computed features.
    
    Example usage:
    - save_chain_as_json(chain, "/path/to/output.json")
    """
    ensure_filepath_exists(filepath)

    chain_data = {
        "ID": chain.id,
        "tasks": [
            {"phase": t.phase, "period": t.period, "deadline": t.deadline}
            for t in chain.tasks
        ]
    }

    with open(filepath, "w") as f:
        json.dump(chain_data, f, indent=4)


def save_chains_as_jsonl(chains: list[CEChain], filepath: str):
    """Save a list of CEChain objects as JSONL, one chain per line.
    
    Example usage:
    - save_chain_as_jsonl(chain, "/path/to/output.jsonl")
    """
    ensure_filepath_exists(filepath)

    with open(filepath, "w") as f:
        for chain in chains:
            chain_data = {
                "ID": chain.id,
                "tasks": [
                    {"phase": t.phase, "period": t.period, "deadline": t.deadline}
                    for t in chain.tasks
                ]
            }
            f.write(json.dumps(chain_data) + "\n")


def load_chain_from_json(filepath: str) -> CEChain:
    """Load a CEChain object from a JSON file."""
    with open(filepath, "r") as f:
        chain_data = json.load(f)
    
    tasks = [Task(t["phase"], t["period"], t["deadline"]) for t in chain_data["tasks"]]
    return CEChain(*tasks, id=chain_data["ID"])


def load_chains_from_jsonl(filepath: str) -> list[CEChain]:
    """Load a list of CEChain objects from a JSONL file."""
    chains = []
    with open(filepath, "r") as f:
        for line in f:
            chain_data = json.loads(line.strip())
            tasks = [Task(t["phase"], t["period"], t["deadline"]) for t in chain_data["tasks"]]
            chains.append(CEChain(*tasks, id=chain_data["ID"]))
    return chains


##########
# Analysis
##########

def analyze(chain: CEChain, info=False, bound=None, relative_bound=None, timeout_sec=None):

    assert not (bound and relative_bound), "cannot specify bound and relative bound at the same time"

    try:
        if timeout_sec:
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_sec)

        # Start timer
        start_time = time.time()

        results = dict()

        if chain.hyperperiod is None:
            chain.calc_hyperperiod()

        if info:
            # hyperperiod
            results['H'] = chain.hyperperiod

            # hyperperiod/maxperiod
            results['H/Tp'] = chain.hyperperiod / max([tsk.period for tsk in chain.tasks])

        if chain.anchorsRT is None:
            chain.calc_anchors()

        # print("Anchors RT: ", chain.anchorsRT)

        if info:
            # Number of anchor points
            results['#AnchorsRT'] = len(chain.anchorsRT)-1

        # Max RT
        results['MaxRT'] = maximumRT(chain)
        results['MaxRedRT'] = results['MaxRT'] - chain.tasks[0].period

        results['Reac'] = reactive(chain)

        # Min RT
        results['MinRT'] = minimumRT(chain)

        # Average
        results['AvRT'] = averageRT(chain)

        # Throughput
        results['throughp'] = throughput(chain)

        if relative_bound:
            bound = relative_bound * results["MaxRT"] 
            # bound = relative_bound * (results["MaxRT"] - chain.tasks[0].period )

        if bound:
            results['mkRT'] = mkRT(chain, bound)

            results['LE-RT'] = longestExceedanceRT(chain, bound)


        end_time = time.time()
        results['analysis_time_sec'] = end_time - start_time

        signal.alarm(0)

    except TimeoutError as e:
        results['analysis_time_sec'] = timeout_sec
        signal.alarm(0)

    return results

def maximumRT(chain: CEChain):
    '''Maximum Reaction Time (MRT/MaxRT)'''
    if chain.anchorsRT is None:
        chain.calc_anchors()
    return max([y for x,y in chain.anchorsRT])

def minimumRT(chain: CEChain):
    '''Minimum Reaction Time (MinRT)'''
    if chain.anchorsRT is None:
        chain.calc_anchors()
    
    minRT = None
    for idx in range(len(chain.anchorsRT) - 1):
        currentX, currentY = chain.anchorsRT[idx]
        nextX, nextY = chain.anchorsRT[idx+1]

        rt = currentY - (nextX - currentX)

        if minRT == None:
            minRT = rt
        else:
            minRT = min(minRT, rt)
    return minRT

def reactive(chain: CEChain):
    '''Minimum Reaction Time (MinRT)'''
    if chain.anchorsRT is None:
        chain.calc_anchors()
    
    reac = None
    for idx in range(len(chain.anchorsRT) - 1):
        currentX, currentY = chain.anchorsRT[idx]
        nextX, nextY = chain.anchorsRT[idx+1]

        rt = currentY - (nextX - currentX)

        if reac == None:
            reac = rt
        else:
            reac = max(reac, rt)

    reac += chain.tasks[0].period
    return reac

def averageRT(chain: CEChain):
    '''Average Reaction Time (AvRT)'''
    if chain.anchorsRT is None:
        chain.calc_anchors()
    
    avRT = 0
    for idx in range(len(chain.anchorsRT)-1):
        currentX, currentY = chain.anchorsRT[idx]
        nextX, nextY = chain.anchorsRT[idx+1]

        yHat = currentY - (nextX - currentX)

        avRT = avRT + ((nextX - currentX) * (currentY + yHat))

    if chain.hyperperiod is None:
        chain.calc_hyperperiod()

    return avRT / (2 * chain.hyperperiod)

def throughput(chain: CEChain):
    '''Throughput''' 

    if chain.anchorsRT is None:
        chain.calc_anchors()
    if chain.hyperperiod is None:
        chain.calc_hyperperiod()

    # Note: right anchor point is removed as described in the analysis (since first and last anchor point are exactly one hyperperiod apart)
    return (len(chain.anchorsRT) -1) / chain.hyperperiod

def mkRT(chain: CEChain, bound):
    """Weakly hard chain-level (m,k) constraints for Reaction time. 
    Returns the (m,k) constraints with the smallest m which are satisfied for bound with k specified in MKRange."""
    if chain.anchorsRT is None:
        chain.calc_anchors()
    if chain.hyperperiod is None:
        chain.calc_hyperperiod()
    
    FP_list = []
    length = 0
    anchors = chain.anchorsRT
    T1 = chain.tasks[0].period
    hyperperiod = chain.hyperperiod

    for i in range(len(anchors) - 1):
        x_i, y_i = anchors[i]
        x_next, _ = anchors[i + 1]

        assert (x_next - x_i) // T1 == (x_next - x_i) / T1 # Make sure that anchors are actually integer multiples
        N_anc = (x_next - x_i) // T1
        N_fail = min(math.ceil((y_i - (bound + T1)) / T1), N_anc)
        N_fail = max(N_fail,0)  # corner case with very large bound
        FP_list.append((N_fail, 'F'))
        FP_list.append((N_anc - N_fail, 'P'))
        length += N_anc
    original_length = len(FP_list)

    i = 0
    while length < (hyperperiod / T1) + MKRange[1]:
        FP_list.append(FP_list[i])
        length += FP_list[i][0]
        i += 1

    # Construct results vector
    mk_results = [0 for k in range(MKRange[0],MKRange[1]+1)]
    for idx in range(original_length):
        if FP_list[idx][1] == 'F':
            # Start a new iteration
            for k in range(MKRange[0], MKRange[1] + 1):
                misses = 0
                total_count = 0
                j = idx
                while total_count < k:
                    nextNumber, nextFP = FP_list[j]
                    if nextNumber >= k - total_count:
                        nextNumber = k - total_count
                    total_count += nextNumber
                    if nextFP == 'F':
                        misses += nextNumber
                    j += 1
                
                mk_results[k - MKRange[0]] = max(mk_results[k - MKRange[0]], misses)

    return list(zip(mk_results,list(range(MKRange[0],MKRange[1]+1))))

def longestExceedanceRT(chain: CEChain, bound):
    """Longest Consecutive Exceedance for Reaction Time (LE_{RT}) for a given bound."""
    if chain.anchorsRT is None:
        chain.calc_anchors()
    if chain.hyperperiod is None:
        chain.calc_hyperperiod()

    assert chain.anchorsRT[0][0] + chain.hyperperiod == chain.anchorsRT[-1][0]

    # Determine exceedance intervals
    exceedance_intervals = []
    for idx in range(len(chain.anchorsRT)-1):
        currentX, currentY = chain.anchorsRT[idx]
        nextX, nextY = chain.anchorsRT[idx+1]

        if currentY > bound:
            exceedance_intervals.append((currentX, currentX + min(currentY - bound, nextX - currentX)))
    
    # Extend to two hyperperiods
    extended = exceedance_intervals[:]
    for start,finish in exceedance_intervals:
        extended.append((start + chain.hyperperiod, finish + chain.hyperperiod))    
    exceedance_intervals = extended
    
    # Merge exceedance intervals
    merged_exceedance_intervals = []

    if len(exceedance_intervals) <= 1:
        merged_exceedance_intervals = exceedance_intervals
    else:
        current_start, current_end = exceedance_intervals[0]
        for idx in range(1,len(exceedance_intervals)):
            next_start, next_end = exceedance_intervals[idx]

            if current_end == next_start:
                # merge interval
                current_end = next_end
            
            else:
                # append and start new interval
                merged_exceedance_intervals.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        
        # Add last interval after finishing loop
        merged_exceedance_intervals.append((current_start, current_end))

    
    # Calculate longest interval
    longest = max([0] + [end-start for start,end in merged_exceedance_intervals])
    if longest == 2* chain.hyperperiod:
        longest = math.inf
    
    return longest


##########
# Main
##########

def main():
    parser = argparse.ArgumentParser(description="Analyze CEChains from JSONL file.")
    parser.add_argument("input", help="Input file (.jsonl)")
    parser.add_argument("-o", "--output", help="Output file to save results (optional)")
    parser.add_argument("--no-print", action="store_true", help="Do not print results to stdout")
    parser.add_argument("-b", "--bound", type=float, help="If set, perform (m,k) and longest exceedance analysis with the given bound")
    parser.add_argument("-rb", "--relative-bound", type=float, help="If set, perform (m,k) and longest exceedance analysis with the given relative bound (relative_bound * MaxRT)")
    parser.add_argument("-i", "--info", action="store_true", help="Store additional information such as number of anchor points in the results vector.")
    parser.add_argument("-t", "--timeout", type=int, help="Set a timeout in seconds.")

    args = parser.parse_args()

    if args.bound is not None and args.relative_bound is not None:
        print("Error: You cannot specify both --bound and --relative-bound at the same time.")
        sys.exit(1)

    # Check output folder
    if args.output:
        ensure_filepath_exists(args.output)

    # Load
    chains = load_chains_from_jsonl(args.input)

    # Analyze
    results = []
    for chain in chains:
        res = dict()
        res["ID"] = chain.id
        res.update(analyze(chain, info=args.info, bound=args.bound, relative_bound=args.relative_bound, timeout_sec=args.timeout))
        results.append(res)

        # Print
        if not args.no_print:
            print(json.dumps(res))

    
    if args.output:
        with open(args.output, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    main()