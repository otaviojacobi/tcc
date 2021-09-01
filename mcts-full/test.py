from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
from time import sleep


with open('easy.txt') as f:
    env_map = f.read()

sims=10
cputc=20

env = GridWorld(env_map)
first_room_pos = [(i,j) for i in range(6) for j in range(8)]
second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

env.add_option(GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 5))

print(env.get_oracle_score())
while not env.finished():

    mcts = MCTS(env)
    o = mcts.run(100, cputc)
    #mcts.root.info(cputc)
    s, r, _ = env.play(o)

#print(r)

print(env.get_score())