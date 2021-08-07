from random import choice
import time

import matplotlib.pyplot as plt

from gridworld_cython import GridWorld
from mcts_cython import MCTS

possible_actions = [0, 1, 2, 3]
start_time = time.time()


results = [0.0] * 9
SMOOTH = 10
for smooth in range(SMOOTH):
    i = 0
    for sims in range(10, 100, 10):
        print(smooth, sims)
        env = GridWorld(20, 10, 10)
        total = 0

        while len(env.legal_moves()) != 0:

            mcts = MCTS(env.copy())
            a = mcts.run(sims)
            s, r, _ = env.step(a)
            
            total += r

        results[i] += total

        i+= 1
        i = i % 9

for k in range(9):
    results[k] /= SMOOTH

plt.plot(results)
plt.savefig('result.png')