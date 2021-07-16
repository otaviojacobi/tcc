from mcts_cython import MCTS
from othello_cython import Othello

import time
from random import choice
from tqdm import tqdm

start_time = time.time()

black_win = 0
white_win = 0
draw = 0
for _ in tqdm(range(100)):
    o = Othello()
    while True:

        moves = o.legal_moves()
        if len(moves) == 0:
            break

        #move = choice(moves)
        #o.play(move)
        m = MCTS(o)
        a = m.run(100)
        o.play(a)

        moves = o.legal_moves()
        if len(moves) == 0:
            break

        m = MCTS(o)
        a = m.run(50)
        o.play(a)

    score = o.score()
    if score > 0:
        black_win += 1
    elif score == 0:
        draw += 1
    else:
        white_win += 1

print('black', black_win)
print('white', white_win)
print('draw', draw)


