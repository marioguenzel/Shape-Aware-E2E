
import math
import json
import random
import os
import itertools
import time
import argparse


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
        self.anchorsDA = None  # Minimal anchor points in $overline I'_{DA}$
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

        # Lists of anchor points
        anchorsDA = list()
        anchorsRT = list()
        
        # Find anchor points over first hyperperiod
        assert self.hyperperiod/self.tasks[p].period == self.hyperperiod//self.tasks[p].period
        for jobidx in range(self.warmup[p],self.warmup[p]+self.hyperperiod//self.tasks[p].period):
            # Calculate partitioned job chain
            part = self._part(p, jobidx)
            partstart = self.tasks[0].re(part[0][0])
            partend = self.tasks[-1].we(part[-1][-1])

            # If there is already such a point, keep the highest one
            if len(anchorsDA) != 0 and anchorsDA[-1][0] == partend:
                anchorsDA[-1] = (partend, max(anchorsDA[-1][1], partend-partstart))
            else:  # Otherwise, we append
                anchorsDA.append((partend, partend-partstart))

            # Same for RT
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

        # == DA anchors ==
        def redundantDA(entry1,entry2):
            """Returns True if entry1 is redundant"""
            return entry2[1] - entry1[1] == entry2[0] - entry1[0]
        
        # Repeat first entry (First entry can potentially be non-redundant later on)
        anchorsDA.append(repeatentry(anchorsDA[0]))

        # Find anchor points in I
        anchorsDAfromI = []
        for idx in range(len(anchorsDA)-1):
            if not redundantDA(anchorsDA[idx], anchorsDA[idx+1]):
                anchorsDAfromI.append(anchorsDA[idx])
        anchorsDAfromI.append(repeatentry(anchorsDAfromI[0]))

        assert len(anchorsDAfromI)>1
        assert redundantDA(anchorsDAfromI[-2], anchorsDAfromI[-1]) is False

        # == Store anchors ==
        self.anchorsRT = anchorsRTfromI  # Careful: The anchor on the starttime might be artificial, i.e., not needed when describing later hyperperiods.
        self.anchorsDA = anchorsDAfromI


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

def analyze(chain: CEChain):

    # Start timer
    start_time = time.time()

    results = dict()
    if chain.anchorsRT is None or chain.anchorsDA is None:
        chain.calc_anchors()

    # print("Anchors RT: ", chain.anchorsRT)
    # print("Anchors DA: ", chain.anchorsDA)

    # Number of anchor points
    results['#AnchorsRT'] = len(chain.anchorsRT)-1
    results['#AnchorsDA'] = len(chain.anchorsDA)-1

    # Max RT and Max DA
    results['MaxRT'] = maximumRT(chain)
    results['MaxDA'] = maximumDA(chain)
    assert results['MaxRT'] == results['MaxDA']

    # Min RT and Min DA
    results['MinRT'] = minimumRT(chain)
    results['MinDA'] = minimumDA(chain)

    # Average
    results['AvRT'] = averageRT(chain)
    results['AvDA'] = averageDA(chain)

    # Throughput
    results['throughp'] = throughput(chain)

    # Longest Consecutive Exceedance


    end_time = time.time()
    results['analysis_time_sec'] = end_time - start_time

    
    return results

def maximumRT(chain: CEChain):
    '''Maximum Reaction Time (MRT/MaxRT)'''
    if chain.anchorsRT is None:
        chain.calc_anchors()
    return max([y for x,y in chain.anchorsRT])

def maximumDA(chain: CEChain):
    '''Maximum Data Age (MDA/MaxDA)'''
    if chain.anchorsDA is None:
        chain.calc_anchors()
    return max([y for x,y in chain.anchorsDA])

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

def minimumDA(chain: CEChain):
    '''Minimum Data Age (MinDA)'''
    if chain.anchorsDA is None:
        chain.calc_anchors()

    minDA = None
    for idx in range(len(chain.anchorsDA) - 1):
        prevX, prevY = chain.anchorsDA[idx]
        currentX, currentY = chain.anchorsDA[idx+1]

        da = currentY - (currentX - prevX)

        if minDA == None:
            minDA = da
        else:
            minDA = min(minDA, da)
    return minDA

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

def averageDA(chain: CEChain):
    '''Average Data Age (AvDA)'''
    if chain.anchorsDA is None:
        chain.calc_anchors()

    avDA = 0
    for idx in range(len(chain.anchorsDA)-1):
        prevX, prevY = chain.anchorsDA[idx]
        currentX, currentY = chain.anchorsDA[idx+1]

        yHat = currentY - (currentX - prevX)
        avDA = avDA + ((currentX - prevX) * (currentY + yHat))

    if chain.hyperperiod is None:
        chain.calc_hyperperiod()

    return avDA / (2 * chain.hyperperiod)

def throughput(chain: CEChain):
    '''Throughput'''
    if chain.anchorsDA is None:
        chain.calc_anchors()
    if chain.hyperperiod is None:
        chain.calc_hyperperiod()

    # Note: left anchor point is removed as described in the analysis (since first and last anchor point are exactly one hyperperiod apart)
    return (len(chain.anchorsDA) -1) / chain.hyperperiod

def longestExceedanceRT(chain: CEChain, bound):
    """Longest Consecutive Exceedance for Reaction Time (LE_{RT}) for a given bound."""
    
    # To be done
    # Make sure to return infty if length is full interval    
    return None

def longestExceedanceDA(chain: CEChain, bound):
    """Longest Consecutive Exceedance for Data Age (LE_{DA}) for a given bound."""
    
    # To be done
    # Make sure to return infty if length is full interval    
    return None


##########
# Main
##########


# if __name__ == '__main__':
#     # DEBUG 1
#     # tau1 = Task(0,50,50)
#     # tau2 = Task(0,120,120)
#     # chain = CEChain(tau1, tau2)
#     # chain.calc_anchors()

#     # print(chain.anchorsRT)
#     # print(chain.anchorsDA)
#     # print(chain.hyperperiod)
#     # print(chain.starttimes)

#     # # DEBUG 2
#     # chains = load_chains_from_jsonl("test/test.jsonl")
#     # for ch in chains:
#     #     res = analyze(ch)
#     #     print("ID:", ch.id, res)
#     #     if res['AvRT'] != res['AvDA']:
#     #         breakpoint()
        
#     #     if res['#AnchorsRT'] != res['#AnchorsDA']:
#     #         breakpoint()

    
#     ch = [c for c in load_chains_from_jsonl("test/test.jsonl") if c.id == 992][0]
#     res = analyze(ch)
#     print(ch.anchorsRT)
#     print(ch.anchorsDA)
#     print("ID:", ch.id, res)

#     # # DEBUG 3
#     # # Example chain from paper
#     # tau1 = Task(0,6,6)
#     # tau2 = Task(0,10,10)
#     # tau3 = Task(0,5,5)
#     # chain = CEChain(tau1, tau2, tau3)
#     # chain.calc_anchors()

#     # print(chain.anchorsRT)
#     # print(chain.anchorsDA)
#     # print(chain.hyperperiod)
#     # print(chain.starttimes)
#     # print(analyze(chain))
#     # print(analyze(chain))


def main():
    parser = argparse.ArgumentParser(description="Analyze CEChain(s) from JSON/JSONL files.")
    parser.add_argument("input", help="Input file (.json or .jsonl)")
    parser.add_argument("-o", "--output", help="Output file to save results (must match format of input file) (optional)")
    parser.add_argument("--format", choices=["json", "jsonl"], help="Force input format (optional)")
    parser.add_argument("--no-print", action="store_true", help="Do not print results to stdout")
    args = parser.parse_args()

    # Determine format
    input_ext = os.path.splitext(args.input)[1].lower()
    fmt = args.format or ("jsonl" if input_ext == ".jsonl" else "json")

    # Check output folder
    if args.output:
        ensure_filepath_exists(args.output)

    results = []
    if fmt == "json":
        # Load
        chain = load_chain_from_json(args.input)
        # Analyze
        res = analyze(chain)
        results.append({"ID": chain.id, "analysis": res})

        # Print
        if not args.no_print:
            print(json.dumps(res, indent=4))

        # Store
        if args.output:
            with open(args.output, "w") as f:
                json.dump(res, f, indent=4)
    
    else:
        # Load
        chains = load_chains_from_jsonl(args.input)
        # Analyze
        for chain in chains:
            res = analyze(chain)
            results.append({"ID": chain.id, "analysis": res})

            # Print
            if not args.no_print:
                print(json.dumps(res))
        
        if args.output:
            with open(args.output, "w") as f:
                for r in results:
                    f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    main()