from othello_cython import Othello
import time
from random import choice


start_time = time.time_ns()
for _ in range(100000):
    o = Othello()
    while True:
        moves = o.legal_moves()

        if len(moves) == 0:
            break

        o.play(choice(moves))

end_time = time.time_ns()
print('Total time was', (end_time-start_time)/1000 )