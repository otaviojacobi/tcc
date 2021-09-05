from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS

with open('easy.txt') as f:
    env_map = f.read()


sims = 100
cputc = 20

options = [
  # primitives, (0,0) is meaningless
  GridWorldOption((0, 0),  {'all'}, 0, 0),
  GridWorldOption((0, 0),  {'all'}, 1, 1),
  GridWorldOption((0, 0),  {'all'}, 2, 2),
  GridWorldOption((0, 0),  {'all'}, 3, 3),
]

env = GridWorld(env_map)
mcts = MCTS(env, options) 
while not env.finished():
    a = mcts.run(sims, cputc)
    env.step(a)
    mcts.set_new_head(a)

print(env.get_score())


