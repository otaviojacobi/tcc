from gridworld import GridWorld, GridWorldOption
from random import choice
from mcts_options import MCTS

CPUTC = 200
search_map = '''.....*.....
.X...*.....
...........
.....*.....
**.*****.**
.....*.....
.....*.....
........G..
.....*.....
.....*.....
'''
env = GridWorld(search_map)
env.add_options([GridWorldOption((7,3), env.get_valid_positions().copy())])

done = False
total = 0
while not done:
    mcts = MCTS(env.copy())
    a = mcts.run(10, 200)

    _, r, done = env.step(a)

    total += r



print(total)