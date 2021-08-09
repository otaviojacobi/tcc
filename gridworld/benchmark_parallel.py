import matplotlib.pyplot as plt
import ray

from gridworld_cython import GridWorld
from mcts_cython import MCTS

ray.init()

SIM_RANGE = [7,8,9,10,100,150,200,500,1000,5000]
SMOOTH = 50
CPUTC = 200


@ray.remote
def run_single_sim(sims, smooth, cputc):
    print(sims, smooth)
    env = GridWorld(30, goalX=15, goalY=15)
    done = False
    total = 0
    while not done:
        mcts = MCTS(env.copy())
        a = mcts.run(sims, cputc)
        _, r, done = env.step(a)

        total += r

    return total

@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)

features = [run_smoothed.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out = ray.get(features)

print(out)

plt.plot(out)

plt.savefig('result.png')