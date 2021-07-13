from random import choice
import time
from othello_cython import Othello

import ray
ray.init(local_mode=True)

print('heyy')

black_wins = 0
white_wins = 0
draw = 0

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

futures = [simulation() for _ in range(1000)]
#pprint(ray.get(futures)) # [0, 1, 4, 9]

print("--- %s seconds ---" % (time.time() - start_time))
#print(white_wins, black_wins, draw)
