from scipy import stats
from analysis import save_chains_as_jsonl, CEChain, Task

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
    
    # Generate CE chains
    chains = []
    for idx in range(number_chains):
        periods = gen_periods_WATERS(number_tasks)
        chains.append(CEChain(*[Task(0, per, per) for per in periods], id=idx))
    
    # Store CE chains
    save_chains_as_jsonl(chains, filename)


if __name__ == "__main__":
    # Generate 10 test CE chains with 5 tasks each using WATERS periods
    generateSynchronousImplicitWATERS(10,10,"test/test.jsonl") 
