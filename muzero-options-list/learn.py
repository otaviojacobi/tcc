from MuZero import MuZero
from GridWorldOption import GridWorldOption


from GridWorld import GridWorld

from mcts.MCTS import MCTS
import numpy as np
import matplotlib.pyplot as plt

from random import choice

import time

options = [
    GridWorldOption(0),
    GridWorldOption(1),
    GridWorldOption(2),
    GridWorldOption(3),
]

with open('./maps/brc000d.map') as f:
    the_map = f.read()
#print(the_map)
env = GridWorld(the_map, 150000)
mu = MuZero(env, options)


env.reset()
returns = mu.learn(200, 40)