


import json
import random
import numpy as np
from scipy import stats
from collections import Counter
from analysis import ensure_filepath_exists

def gen_periods_WATERS(number: int):
    """Main function to generate a task set with the WATERS benchmark.
    Output: taskset

    Variables:
    number: 
    """

    periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
    period_pdf=[0.03 / 0.85, 0.02 / 0.85, 0.02 / 0.85, 0.25 / 0.85, 0.25 / 0.85, 0.03 / 0.85, 0.2 / 0.85, 0.01 / 0.85, 0.04 / 0.85]

    dist = stats.rv_discrete(name='periods',
                             values=(periods, period_pdf))
    task_set_periods = dist.rvs(size=number)  # list all periods

    return list(map(int, task_set_periods))


def generateSynchronousImplicitWATERS(number_tasks, number_chains, filename):
    """Generate cause-effect chains using the WATERS periods, with phase=0 and implicit deadlines."""

    # Make sure filepath exists
    ensure_filepath_exists(filename)
    
    # Generate CE chains
    periods_for_chains = []
    for _ in range(number_chains):
        periods_for_chains.append(gen_periods_WATERS(number_tasks))
    
    # Store CE chains
    with open(filename, "w") as f:
        for ceid, periods in enumerate(periods_for_chains):
            chain_data = {
                "ID": ceid,
                "tasks": [
                    {"phase": 0, "period": per, "deadline": per}
                    for per in periods
                ]
            }
            f.write(json.dumps(chain_data) + "\n")


if __name__ == "__main__":
    # Generate two test CE chains with 5 tasks each using WATERS periods
    generateSynchronousImplicitWATERS(5,2,"test/test.jsonl") 
