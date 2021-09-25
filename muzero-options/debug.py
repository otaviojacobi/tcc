#from MuZeroParallel import MuZero as MuZeroP

from MuZero import MuZero

from GridWorldOption import GridWorldOption
from GridWorld import GridWorld

from mcts.MCTS import MCTS
import numpy as np
import matplotlib.pyplot as plt

from random import choice
from copy import deepcopy
import time

import pickle
import pandas as pd

from matplotlib.pyplot import figure
import itertools
from tqdm import tqdm


MAP_NAME = './maps/door.map'

options = [
      GridWorldOption((0, 0),  {'all'}, 0, 0),
      GridWorldOption((0, 0),  {'all'}, 1, 1),
      GridWorldOption((0, 0),  {'all'}, 2, 2),
      GridWorldOption((0, 0),  {'all'}, 3, 3)
]

with open(MAP_NAME) as f:
    the_map = f.read()

first_room_pos = [(i,j) for i in range(6) for j in range(8)]
second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

full_options = [
  # primitives, (0,0) is meaningless
  GridWorldOption((0, 0),   {'all'}, 0, 0),
  GridWorldOption((0, 0),   {'all'}, 1, 1),
  GridWorldOption((0, 0),   {'all'}, 2, 2),
  GridWorldOption((0, 0),   {'all'}, 3, 3),
  GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 4),
  GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)]), 5),
  GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)]), 6),
  GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)]), 7),
]    

env = GridWorld(the_map)

G_model = {}
for position in tqdm(env.possible_positions):
    for option in full_options:
        if option.is_valid(position):
            
            test_env = GridWorld(the_map)
            test_env.cur_x = position[0]
            test_env.cur_y = position[1]
            rewards = []
            while True:
                action, should_break = option.get_action(test_env)
                
                if action == -1:
                    break
                
                next_position, r, _ = test_env.step(action)
                rewards.append(r)
                
                if should_break:
                    break
                
            G_model[(position, option)] = (next_position, rewards)

SIMULATIONS = 40
SIM_FINISHS = 10000
GAMES = 2
ALPHA=0.01

env = GridWorld(the_map, SIM_FINISHS)
mu = MuZero(env, options)

mu.g.model_table = G_model

start = time.time()
returns, argmax_returns = mu.learn(GAMES, SIMULATIONS, alpha=ALPHA)

end = time.time()