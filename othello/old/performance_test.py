from random import choice
import time
import matplotlib.pyplot as plt

from othello import Othello as Othello
from othello_cython import Othello as OthelloCython
from othello_numba import Othello as OthelloNumba

def run_simulation(o):
    while True:
        moves = o.legal_moves()

        if len(moves) == 0:
            break

        move = choice(moves)
        o.play(move)

    return o.score()


def run_cython_simulations(sims):
    start_time = time.time()
    for _ in range(sims):
        run_simulation(OthelloCython())
    return time.time() - start_time

def run_numba_simulations(sims):
    start_time = time.time()
    for _ in range(sims):
        run_simulation(OthelloNumba.new())
    return time.time() - start_time

# Compile Numba
o = run_simulation(OthelloNumba.new())

SIMS_RANGE = (500, 800, 100)

total_native_times = []
total_cython_times = []
total_numba_times = []
for SIMS in range(*SIMS_RANGE):
    print(SIMS)
    total_cython_times.append(run_cython_simulations(SIMS))
    total_numba_times.append(run_numba_simulations(SIMS))

plt.plot(total_cython_times, label='cython')
plt.plot(total_numba_times, label='numba')

plt.legend()

plt.savefig('result.png')