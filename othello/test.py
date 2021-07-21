from othello_cython import Othello, move_to_action
from alpha_search import MCTS
from random import choices
from NeuralNet import NeuralNet
from ReplayMemory import ReplayMemory

import time


counter = 0
memory = ReplayMemory(50000)
start_time = time.time()

env = Othello()
m = MCTS(env, NeuralNet("cpu"))

while True:

    possible_moves = env.legal_moves()
    if len(possible_moves) == 0:
        break

    s, pi, z = m.run(100, 1.0)

    memory.push(s, pi, z)

    distr = [pi[move_to_action(move)] for move in possible_moves]
    move = choices(possible_moves, distr)[0]
    env.play(move)

    m.set_new_head(move)

print('Total time is', time.time() - start_time)