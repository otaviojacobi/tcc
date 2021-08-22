from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS

with open('envmap.txt') as f:
    env_map = f.read()


sims=10
cputc=20

env = GridWorld(env_map)

print(env.get_oracle_score())

while not env.finished():
    mcts = MCTS(env)
    a = mcts.run(sims, cputc)
    env.play(a)

print(env.get_score())