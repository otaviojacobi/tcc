from MCTS import MCTS
from CartPoleOption import CartPoleOption
from CartPole import CartPole
from random import choice
import time
from copy import deepcopy

options = [CartPoleOption(0), CartPoleOption(1)]

env = CartPole()

render_env = deepcopy(env.env)

mcts = MCTS(env, options)
total = 0
while not env.finished():
    #mcts.reset(env)
    mcts = MCTS(env, options)

    action = mcts.run(20, 2)
    #mcts.info(2)
    #option = choice(options)
    _, r, _ = env.step(action)
    total += r
    
print(total)