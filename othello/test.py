from othello_cython import Othello, move_to_action
from alpha_search import MCTS
from random import choices
from NeuralNet import NeuralNet

import time

env = Othello()
m = MCTS(env, NeuralNet())
counter = 0

start_time = time.time()

while True:

    possible_moves = env.legal_moves()
    if len(possible_moves) == 0:
        break

    s, pi, z = m.run(200, 1.0)


    distr = [pi[move_to_action(move)] for move in possible_moves]
    a = choices(possible_moves, distr)[0]
    env.play(a)

    m.set_new_head(a)

print('Total time is', time.time() - start_time)