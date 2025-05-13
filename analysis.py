
import math
import json
import random
import os


class Task:
    """A simple task"""
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
        self.anchorsDA = None
        self.anchorsRT = None

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
        """Calculate anchor points over one hyperperiod"""
        if p is None:
            # Find index with maximal period
            p = max(range(len(self.tasks)), key=lambda i: self.tasks[i].period)
        # Check if warm up and hyperperiod is defined.
        if self.warmup is None:
            self.calc_warmup()
        if self.hyperperiod is None:
            self.calc_hyperperiod()

        # For each partitioned jobchains within a hyperperiod set an anchor
        anchorsDA = list()
        anchorsRT = list()

        assert self.hyperperiod/self.tasks[p].period == self.hyperperiod//self.tasks[p].period
        for jobidx in range(self.warmup[p],self.warmup[p]+self.hyperperiod//self.tasks[p].period + 1):
            # Cal partitioned job chain
            part = self._part(p, jobidx)
            partstart = self.tasks[0].re(part[0][0])
            partend = self.tasks[-1].we(part[-1][-1])
            anchorsDA.append((partend, partend-partstart))
            anchorsRT.append((partstart, partend-partstart))
        
        # TODO: Remove redundant anchors!

        # Store anchors
        self.anchorsRT = anchorsRT  # Careful: The anchor on the starttime might be artificial, i.e., not needed when describing later hyperperiods.
        self.anchorsDA = anchorsDA
    
    def get_anchorsDA(self,fromtime, totime, leftborder=True,rightborder=True, artificialborder=False):
        """Return all anchors within a given interval."""
        # artificialborders adds an anchor on the RIGHT border such that the DA is fully defined inside the interval [fromtime, totime]
        # leftborder and rightborder describe whether potential anchor points that lie right on the border of the interval should be included or not.
        # TODO
        pass
    
    def get_anchorsRT(self,fromtime, totime, leftborder=True,rightborder=True, artificialborder=False):
        # artificialborders adds an anchor on the LEFT border such that the RT is fully defined inside the interval [fromtime, totime]
        # TODO
        pass

    def _check_RT_anchor_artificial(self):
        # The anchor at starttime is artitifical iff there is no anchor on starttime+hyperperiod
        if self.starttimes[0] + self.hyperperiod in [x for x,y in self.anchorsRT]:
            return False
        else: 
            return True


def analyze(chain: CEChain):
    results = dict()
    if chain.anchorsRT is None or chain.anchorsDA is None:
        chain.calc_anchors()
    
    # Max RT and Max DA
    results['MaxRT'] = max([y for x,y in chain.anchorsRT])
    results['MaxDA'] = max([y for x,y in chain.anchorsDA])

    # Min RT and Min DA
    
    # Average

    # Longest Consecutive Exceedance

    # Throughput

    return results




# === DATA HANDLING ===

def ensure_filepath_exists(filepath: str):
    """Check if a filepath exists and create it if it doesn't."""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def save_chain_as_json(chain: CEChain, filepath: str):
    """Save CEChain object as JSON. Just stores the chain without the computed features."""
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
    """Save a list of CEChain objects as JSONL, one chain per line."""

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

# Example usage:
# save_chain_as_json(chain, "/path/to/output.json")


if __name__ == '__main__':
    # DEBUG
    tau1 = Task(0,50,50)
    tau2 = Task(0,120,120)
    chain = CEChain(tau1, tau2)
    chain.calc_anchors()

    print(chain.anchorsRT)
    print(chain.anchorsDA)
    print(chain.hyperperiod)
    print(chain.starttimes)
    print(chain._check_RT_anchor_artificial())

    breakpoint()
