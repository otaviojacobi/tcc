import torch
import time
from random import choices

from alpha_search import MCTS
from othello_cython import Othello, move_to_action
from model import AlphaNet
from ReplayMemory import ReplayMemory

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

nn = AlphaNet().to(device)


TEMPERATURE = 1.0
TOTAL_SIMULATIONS = 5
MEMORY_SIZE = 50000

memory = ReplayMemory(MEMORY_SIZE)

for sim in range(TOTAL_SIMULATIONS):

  env = Othello()
  m = MCTS(env, nn)
  game_over = False
  counter = 0
  while True:

    start_time = time.time()
    possible_moves = env.legal_moves()
    if len(possible_moves) == 0:
      break

    s, pi, z = m.run(200, TEMPERATURE)

    memory.push(s, pi, z)

    distr = [pi[move_to_action(move)] for move in possible_moves]
    a = choices(possible_moves, distr)[0]
    env.play(a)

    m.set_new_head(a)

    counter += 1
    if counter > 10:
      TEMPERATURE = 0.01

    print('Total time for 200 sims is: %d', time.time() - start_time)





print(pi)
print(z)