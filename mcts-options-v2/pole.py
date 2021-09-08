from MCTSLearn import MCTS
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

    option, _ = mcts.learn(10, 2)
    #mcts.info(2)
    #option = choice(options)
    option.executed = False
    while True:
        action = option.get_action(env)

        if action == -1 or env.finished():
            break
        _, r, _ = env.step(action)

        render_env.step(action)

        render_env.render()
        #time.sleep(0.1)
        total += r
    option.executed = False
    
print(total)