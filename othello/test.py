from mcts_cython import MCTS
from othello_cython import Othello

import time
from random import choice

start_time = time.time()

o = Othello()
while True:


    moves = o.legal_moves()
    if len(moves) == 0:
        break

    move = choice(moves)
    o.play(move)

    moves = o.legal_moves()
    if len(moves) == 0:
        break

    m = MCTS(o)
    a = m.run(1000)
    o.play(a)

    #o.render()

print(o.score())


print('[CYTHON] Time for 100 simulation ', time.time() - start_time)
