import time

import matplotlib.pyplot as plt

from gridworld_cython import GridWorld
from mcts_cython import MCTS
import random

CPUTC = 200
#random.seed(42)

env = GridWorld(30, goalX=15, goalY=15)
total = 0

done = False
while not done:

#for _ in range(50):
    mcts = MCTS(env.copy())
    a = mcts.run(10, CPUTC)
    #print(a)

    #mcts.info(CPUTC)

    s, r, done = env.step(a)

    print(s)
    total += r

print(total)