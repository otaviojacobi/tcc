from MCTSLearn import MCTS
from MountainCarOption import MountainCarOption
from MountainCar import MountainCar
from random import choice
import time
from copy import deepcopy

options = [
    MountainCarOption(0),
    MountainCarOption(1),
    MountainCarOption(2),

    MountainCarOption(0, 20),
    #MountainCarOption(1, 20),
    MountainCarOption(2, 20),

]

env = MountainCar()

render_env = deepcopy(env.env)

total = 0
option_order = []
while not env.finished():
    #mcts.reset(env)
    mcts = MCTS(env, options)

    option, _ = mcts.learn(20, 2)
    #mcts.info(2)
    #option = choice(options)
    option.executed = False
    print(option.opt_id, option.counter)

    option_order.append(option)
    while True:
        action = option.get_action(env)

        if action == -1 or env.finished():
            break
        _, r, _ = env.step(action)

        total += r
    print(total)
    option.executed = False

print(total)

for option in option_order:
    done = False
    while True:
        action = option.get_action(None)

        if action == -1:
            break
        _, _, done, _ = render_env.step(action)
        render_env.render()

        if done:
            print('terminei')
            break
