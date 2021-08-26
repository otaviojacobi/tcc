from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS

with open('envmap.txt') as f:
    env_map = f.read()

sims=10
cputc=20

env = GridWorld(env_map)

env.add_option(GridWorldOption((5,46), {'all'}))
env.add_option(GridWorldOption((32,43), {'all'}))
env.add_option(GridWorldOption((30,10), {'all'}))

print(env.get_oracle_score())

while not env.finished():
    mcts = MCTS(env)
    a = mcts.run(sims, cputc)
    s, _, _ = env.play(a)
    print(s)

print(env.get_score())