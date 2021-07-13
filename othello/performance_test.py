from random import choice
import time
from othello_cython import Othello

import ray
ray.init(address='auto')

black_wins = 0
white_wins = 0
draw = 0

SIMS = 30000

def seq_simulation():
    o = Othello()
    while True:
        moves = o.legal_moves()

        if len(moves) == 0:
            break

        move = choice(moves)
        o.play(move)

    return o.score()

@ray.remote
def simulation():
    o = Othello()
    while True:
        moves = o.legal_moves()

        if len(moves) == 0:
            break

        move = choice(moves)
        o.play(move)

    return o.score()


start_time = time.time()
futures = [simulation.remote() for _ in range(SIMS)]
a = ray.get(futures) # [0, 1, 4, 9]
print("--- %s seconds ---" % (time.time() - start_time))


start_time = time.time()
a = [seq_simulation() for _ in range(SIMS)] # [0, 1, 4, 9]
print("--- %s seconds ---" % (time.time() - start_time))
#print(white_wins, black_wins, draw)
