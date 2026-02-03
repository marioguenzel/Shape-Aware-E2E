"""Methods used for comparison in the evaluation."""

import argparse
import itertools
from analysis import Task as OurTask
from analysis import CEChain as OurCEChain
from analysis import load_chains_from_jsonl

import math
import uuid

### Taken from E2E Evaluation framework ###
# https://github.com/tu-dortmund-ls12-rt/E2EEvaluation

# Class definitions

class Task:
    """A task."""
    features = {  # list of possible features and their values
        'release_pattern': ['sporadic', 'periodic'],
        'deadline_type': ['arbitrary', 'constrained', 'implicit'],
        'execution_behaviour': ['wcet', 'bcet', 'wc', 'bc', 'bcwc'],
        'communication_policy': ['implicit', 'explicit', 'LET'],
    }

    def __init__(self,
                 release_pattern,
                 deadline_type,
                 execution_behaviour,
                 communication_policy,
                 phase,
                 min_iat,
                 max_iat,
                 period,
                 bcet,
                 wcet,
                 deadline,
                 priority
                ):

        if release_pattern not in self.features['release_pattern']:
            raise ValueError(f'{release_pattern} is not a possible argument.')
        
        if deadline_type not in self.features['deadline_type']:
            raise ValueError(f'{deadline_type} is not a possible argument.')
        
        if execution_behaviour not in self.features['execution_behaviour']:
            raise ValueError(f'{execution_behaviour} is not a possible argument.')
        
        if communication_policy not in self.features['communication_policy']:
            raise ValueError(f'{communication_policy} is not a possible argument.')

        self.id = uuid.uuid4()  # necessary for multiprocessing
        self.release_pattern = release_pattern
        self.deadline_type = deadline_type
        self.execution_behaviour = execution_behaviour
        self.communication_policy = communication_policy
        self.phase = phase
        self.min_iat = min_iat
        self.max_iat = max_iat
        self.period = period
        self.bcet = bcet
        self.wcet = wcet
        self.deadline = deadline
        self.priority = priority
        self.jitter = 0         # TODO


    def print(self):
        """Quick print of all attributes for debugging."""
        print(self)
        print("")


    def utilization(self):
        """Task utilization."""
        return (self.wcet / self.min_iat)
    

    def copy(self):
        return Task(
            self.release_pattern,
            self.deadline_type,
            self.execution_behaviour,
            self.communication_policy,
            self.phase,
            self.min_iat,
            self.max_iat,
            self.period,
            self.bcet,
            self.wcet,
            self.deadline,
            self.priority
        )
    
class Job:

    def __init__(self, task, occurrence):
        self.task = task
        self.occurrence = occurrence

    def get_release(self):
        return self.task.period * self.occurrence
    
    def get_deadline(self):
        return self.get_release() + self.task.deadline
    
    def __str__(self):
        return f"({self.task}, {self.occurrence})"
    
class TaskSet:
    """A set of Task-Objects."""

    # Assumption: Task set ordered by priority
    # Lower index = Higher Priority

    def __init__(self, *args):
        """Input: Task-Objects"""
        self._lst = list(args)
        self.schedules = dict()     # needed for guenzel_23_inter
        self.id = uuid.uuid4()      # necessary for multiprocessing
        #for task in self._lst:
        #    task.priority = self._lst.index(task)

    def __len__(self):
        return self._lst.__len__()

    def __getitem__(self, item):
        return self._lst.__getitem__(item)

    def __setitem__(self, key, value):
        self._lst.__setitem__(key, value)

    def __delitem__(self, key):
        self._lst.__delitem__(key)

    def __iter__(self):
        yield from self._lst

    @property
    def lst(self):
        return self._lst

    @lst.setter
    def lst(self, new_lst):
        self._lst = new_lst

    def index(self, task):
        return self._lst.index(task)

    def append(self, task):
        self._lst.append(task)
        task.priority = self._lst.index(task)

    def prio(self, task):
        """Priority of a task"""
        return self._lst.index(task)

    def higher_prio(self, task1, task2):
        """task1 has higher prio than task2."""
        return self.prio(task1) < self.prio(task2)

    def utilization(self):
        return sum(task.utilization() for task in self)

    def communication(self):
        if all('implicit' == task.communication_policy for task in self):
            return 'implicit'
        elif all('LET' == task.communication_policy for task in self):
            return 'LET'
        else:
            return 'mixed'

    def check_feature(self, feature):
        assert feature in Task.features.keys()
        # First value
        val = getattr(self[0], feature)

        if all(val == getattr(task, feature) for task in self):
            return val
        else:
            return 'mixed'

    def print(self, length=True, utilization=False, communication=False, execution=False, release=False,
              deadline=False):
        printstr = ''
        printstr += self.__str__() + '\t'
        if length is True:
            printstr += f'length: {len(self)}, '
        if utilization is True:
            printstr += f'utilization: {self.utilization()}, '
        if communication is True:
            printstr += f"communication: {self.check_feature('comm')}, "
        if execution is True:
            printstr += f"execution: {self.check_feature('ex')}, "
        if release is True:
            printstr += f"release: {self.check_feature('rel')}, "
        if deadline is True:
            printstr += f"deadline: {self.check_feature('dl')}, "
        print(printstr)

    def print_tasks(self):
        for task in self:
            task.print()

    def compute_wcrts(self):
        """Compute wcrts by TDA."""
        self.wcrts = dict()
        for idx in range(len(self._lst)):
            self.wcrts[self._lst[idx]] = tda(self._lst[idx], self._lst[:idx])

    def hyperperiod(self):
        """Task set hyperperiod."""
        return math.lcm(*[task.period for task in self._lst])

    def max_phase(self):
        """Maximal phase of the task set."""
        return max([task.phase for task in self._lst])

    def sort_dm(self):
        """Sort by deadline."""
        self._lst.sort(key=lambda x: x.deadline)

    def rate_monotonic_scheduling(self):
        """change priorities of tasks according to RMS"""
        self._lst.sort(key=lambda x: x.period)
        for task in self._lst:
            task.priority = self._lst.index(task)

def tda(task, hp_tasks):
    """Implementation of TDA to calculate worst-case response time.
    Source:
    https://github.com/kuanhsunchen/MissRateSimulator/blob/master/TDA.py
    """
    c = task.wcet  # WCET
    r = c  # WCRT
    while True:
        i = 0  # interference
        for itask in hp_tasks:
            i = i + _workload(itask.min_iat, itask.wcet, r)
        if r < i + c:
            r = i + c
        else:
            return r


def _workload(period, wcet, time):
    """Workload function for TDA.
    Help function for tda().
    """
    return wcet * math.ceil(float(time) / period)


class CEChain(TaskSet):
    """A cause-effect chain."""

    def __init__(self, *args, base_ts=None):
        self.base_ts = base_ts  # base task set (needed for some analyses)
        super().__init__(*args)

    def length(self):
        """returns the length of the cec"""

        return len(self._lst)
    
    def contains(self, task):
        """checks if the given task is in the cec"""

        return self._lst.count(task) > 0
    
    def id_list(self):
        """returns the list of task ids in the cec"""

        ids = []
        for task in self._lst:
            ids.append(int(task.id))
        return ids

class JobChain(list):
    """A chain of jobs."""

    def __init__(self, *jobs):
        """Create a job chain with jobs *jobs."""
        super().__init__(jobs)

    def __str__(self, no_braces=False):
        return "[ " + " -> ".join([str(j) for j in self]) + " ]"


class PartitionedJobChain:
    """A partitioned job chain."""

    def __init__(self, chain, fw, bw):
        self.bw = bw
        self.fw = fw
        self.complete = self.bw[0].occurrence >= 0  # complete iff bw chain complete
        self.base_ce_chain = chain

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return "[ " + " / ".join(entries) + " ]"

# Analyses

def hamann17(chain):
    """https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECRTS.2017.10"""
    latency = 0
    for task in chain:
        latency += task.max_iat + task.deadline
    return latency


def _release_after(time, task):
    """Next release of task at or after 'time' for periodic tasks."""
    return task.phase + math.ceil((time - task.phase) / task.period) * task.period

def _release(m, task):
    """Time of the m-th job release of a periodic task.
    (First job is at m=1.)"""
    return task.phase + (m - 1) * task.period

def LET_per(chain):
    """https://dl.acm.org/doi/10.1145/3575757.3593640"""
    """Upper bound for periodic tasks under LET.
    - LET
    - periodic
    """
    # Compute chain hyperperiod and phase:
    hyper = chain.hyperperiod()
    max_phase = chain.max_phase()
    # WCRT_max = max(chain.base_ts.wcrts[task] for task in chain)
    WCRT_max = max([tsk.deadline for tsk in chain])

    lengths = []

    for mvar in itertools.count(start=1):
        # Principle 1 and chain definition
        zvar = _release(mvar, chain[0])
        relvar = _release(mvar + 1, chain[0])

        # check conditions
        if relvar + chain.base_ts.wcrts[chain[0]] < max_phase:
            continue
        if zvar > max_phase + hyper + WCRT_max:
            break

        for this_task, next_task in zip(chain[:-1], chain[1:]):
            # Principle 2 (Compute release of next job in the job chain)
            compare_value = relvar + this_task.deadline
            relvar = _release_after(compare_value, next_task)

        # Principle 3
        zprimevar = relvar + chain[-1].deadline

        lengths.append(zprimevar - zvar)

    return max(lengths)

# TODO: Partitioned job chains

# TODO: Approach Suggested by the shepherd

# Main

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Analyze CEChains from JSONL file.")
    parser.add_argument("input", help="Input file (.jsonl)")
    parser.add_argument("-o", "--output", help="Output file to save results (optional)")
    args = parser.parse_args()

    # Load
    chains = load_chains_from_jsonl(args.input)

    # Translate chains to the object type from the sota
    translated_chains = []
    for ch in chains:
        new_task_list = []
        for tsk in ch.tasks:
            new_task_list.append(Task(
                'periodic', 
                'arbitrary', 
                'wcet',
                'LET', 
                phase=tsk.phase, 
                min_iat=tsk.period,
                max_iat=tsk.period,
                period=tsk.period,
                bcet=None,
                wcet=None,
                deadline=tsk.deadline, 
                priority=None
                ))
        translated_chains.append(CEChain(*new_task_list))
    
    breakpoint()

