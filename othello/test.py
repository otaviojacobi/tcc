from mcts_cython import MCTS as MCTSCython
from othello_cython import Othello as OthelloCython

from mcts import MCTS
from othello_numba import Othello


import time
from random import choice

start_time = time.time()

o = OthelloCython()
n = MCTSCython(o)

n.run(1000)

print('[CYTHON] Time for 100 simulation ', time.time() - start_time)

start_time = time.time()

o = Othello.new()
n = MCTS(o)

n.run(1000)

print('[NUMBA] Time for 100 simulation ', time.time() - start_time)