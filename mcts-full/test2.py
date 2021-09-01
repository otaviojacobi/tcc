from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
from time import sleep


with open('easy.txt') as f:
    env_map = f.read()


sims=10
cputc=20

env = GridWorld(env_map)
env = GridWorld(env_map)
env.add_option(GridWorldOption((2,11), {'all'}, 5))
env.add_option(GridWorldOption((9,4), {'all'}, 6))
env.add_option(GridWorldOption((11,11), {'all'}, 7))

while not env.finished():

    print('\n')
    env.render()
    sleep(0.1)

    mcts = MCTS(env)
    opt = mcts.run(10, cputc)
    #mcts.root.info(cputc)
    s, _, _ = env.play(opt)

print('\n')
env.render()
sleep(0.1)

print(env.get_score())