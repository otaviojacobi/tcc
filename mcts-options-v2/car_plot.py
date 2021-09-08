from MCTSLearn import MCTS
from MountainCarOption import MountainCarOption
from MountainCar import MountainCar
from random import choice
import time
from copy import deepcopy
import matplotlib.pyplot as plt
import ray

SIM_RANGE = list(range(10, 400, 10))
@ray.remote
def run_single_sim(sims, smooth, cputc):
    print(sims, smooth)

    options = [
        MountainCarOption(0),
        MountainCarOption(1),
        MountainCarOption(2),

        MountainCarOption(0, 20),
        #MountainCarOption(1, 20),
        MountainCarOption(2, 20),
    ]


    env = MountainCar()

    total = 0
    while not env.finished():
        #mcts.reset(env)
        mcts = MCTS(env, options)

        option, _ = mcts.learn(sims, 2)
        while True:
            action = option.get_action(env)

            if action == -1 or env.finished():
                break
            _, r, _ = env.step(action)

            total += r
    return total

@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)

features = [run_smoothed.remote(sims, 20, 2) for sims in SIM_RANGE]
out = ray.get(features)
print(out)
plt.plot(out)
plt.savefig('mcar.png')