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

env = Othello()
m = MCTS(env, nn)

possible_moves = env.legal_moves()
s, pi, z = m.run(100, TEMPERATURE)


distr = [pi[move_to_action(move)] for move in possible_moves]
a = choices(possible_moves, distr)[0]
env.play(a)

m.set_new_head(a)
