import time

import matplotlib.pyplot as plt
import random

from gridworld_cython import GridWorld
from mcts_cython import MCTS

start_time = time.time()


SIM_RANGE = range(7, 25, 1)
SMOOTH = 20
CPUTC = 200

random.seed(42)

results_size = (len(list(SIM_RANGE)) + 1)
results = [0.0] * results_size
i = 0
for sims in SIM_RANGE:
    total = 0
    for smooth in range(SMOOTH):
        print(sims, smooth)
        env = GridWorld(30, goalX=15, goalY=15)
        done = False
        while not done:
            mcts = MCTS(env.copy())
            a = mcts.run(sims, CPUTC)
            #a=random.choice([0,1,2,3])
            s, r, done = env.step(a)

            total += r

    results[i] += total/SMOOTH
    i += 1


plt.plot(list(SIM_RANGE), results)
plt.savefig('result.png')