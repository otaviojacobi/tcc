from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS

with open('easy.txt') as f:
    env_map = f.read()

env = GridWorld(env_map)

options = [
  # primitives, (0,0) is meaningless
  GridWorldOption((0, 0),  {'all'}, 0, 0),
  GridWorldOption((0, 0),  {'all'}, 1, 1),
  GridWorldOption((0, 0),  {'all'}, 2, 2),
  GridWorldOption((0, 0),  {'all'}, 3, 3),

  # composed
  GridWorldOption((2, 11),  {'all'}, 4),
  GridWorldOption((9, 4),   {'all'}, 5),
  GridWorldOption((11, 11), {'all'}, 6)
]

mcts = MCTS(env, options)
act = mcts.run(100, 20)

mcts.root.info(20)