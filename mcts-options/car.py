from MCTS import MCTS
from MountainCarOption import MountainCarOption
from MountainCar import MountainCar
from random import choice
import time
from copy import deepcopy

options = [
    MountainCarOption(0),
    #MountainCarOption(1),
    MountainCarOption(2),

    MountainCarOption(0, 50),
    #MountainCarOption(1, 20),
    MountainCarOption(2, 50),

]

env = MountainCar()
mcts = MCTS(env, options)
#action= mcts.run(1000, 1.4)
#mcts.root.info(1.4)
# _, r, _ = env.step(action)
# render_env = deepcopy(env.env)

total = 0
steps = []
while not env.finished():
    #mcts.reset(env)
    mcts = MCTS(env, options)

    action= mcts.run(20, 1.4)
    _, r, _ = env.step(action)
    steps.append(action)
    total += r
    print(total)

print(total)

# for step in steps:
#     render_env.step(step)
#     render_env.render()
