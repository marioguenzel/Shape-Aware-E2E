import math
from scipy import stats
from analysis import save_chains_as_jsonl, CEChain, Task
import random
import argparse

def gen_periods_WATERS(number: int):
    """Generate a task periods with the WATERS distribution."""

    periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
    period_pdf=[0.03 / 0.85, 0.02 / 0.85, 0.02 / 0.85, 0.25 / 0.85, 0.25 / 0.85, 0.03 / 0.85, 0.2 / 0.85, 0.01 / 0.85, 0.04 / 0.85]

    dist = stats.rv_discrete(name='periods',
                             values=(periods, period_pdf))
    task_set_periods = dist.rvs(size=number)  # list all periods

    return list(map(int, task_set_periods))


def generateSynchronousImplicitWATERS(number_tasks, number_chains, filename, startid=0):
    """Generate cause-effect chains using the WATERS periods, with random phase and implicit deadlines."""
    
    # Generate CE chains
    chains = []
    for idx in range(number_chains):
        periods = gen_periods_WATERS(number_tasks)
        chains.append(CEChain(*[Task(random.randint(0,per), per, per) for per in periods], id=startid+idx))
    
    # Store CE chains
    save_chains_as_jsonl(chains, filename)


def gen_periods_uniform(number: int, periods: list):
    """Draw periods uniformly from a given set of periods."""
    return random.choices(periods, k=number)

def generateUniform(number_tasks, number_chains, filename, startid=0, maxHTp=None):
    """Generate cause-effect chains with uniform periods, random phase and implicit deadlines.
    Current period range: 10, 20, 30, ..., 200
    """
    chains = []
    periods_list = list(range(10, 201, 10))
    for idx in range(number_chains):
        while True:
            periods = gen_periods_uniform(number_tasks, periods_list)
            if maxHTp is None or math.lcm(*periods)/max(*periods) <= maxHTp:
                break
        chains.append(CEChain(*[Task(random.randint(0,per), per, per) for per in periods], id=startid+idx))
    save_chains_as_jsonl(chains, filename)
    

if __name__ == "__main__":
    # Generate 10 test CE chains with 5 tasks each using WATERS periods
    # generateSynchronousImplicitWATERS(10,1000,"test/test.jsonl") 
    # generateUniform(5,1000,"test/test.jsonl") 

    parser = argparse.ArgumentParser(description="Generate CE chains with specified benchmark and parameters.")
    parser.add_argument("--bench", choices=["WATERS", "UNI"], default="WATERS", help="Benchmark type: WATERS or UNI (default: WATERS)")
    parser.add_argument("--tasks", type=int, default=5, help="Number of tasks per chain (default: 5)")
    parser.add_argument("--sets", type=int, default=10, help="Number of chains to generate (default:10)")
    parser.add_argument("--startid", type=int, default=0, help="ID of the first chain.")
    parser.add_argument("--maxHTp", type=int, default=None, help="Maximal allowed value of Hyperperiod / maximal period.")
    parser.add_argument("filename", type=str, help="Output filename (e.g., 'chains/tests.jsonl')")

    args = parser.parse_args()

    if args.bench == "WATERS":
        generateSynchronousImplicitWATERS(args.tasks, args.sets, args.filename, startid=args.startid)
    elif args.bench == "UNI":
        generateUniform(args.tasks, args.sets, args.filename, startid=args.startid,maxHTp=args.maxHTp)
