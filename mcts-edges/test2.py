from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
from time import sleep


with open('easy.txt') as f:
    env_map = f.read()


sims=10
cputc=20

env = GridWorld(env_map)
# env.render()
# env.add_option(GridWorldOption((2,11), {'all'}))
# env.add_option(GridWorldOption((9,4), {'all'}))
# env.add_option(GridWorldOption((11,11), {'all'}))

#print(env.get_oracle_score())
# first_room_pos = [(i,j) for i in range(6) for j in range(8)]
# second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
# third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
# fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

# env.add_option(GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)])))
# env.add_option(GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)])))
# env.add_option(GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)])))
# env.add_option(GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)])))

while not env.finished():

    mcts = MCTS(env)
    a = mcts.run(50, cputc)
    #mcts.root.info(cputc)
    s, _, _ = env.play(a)
    print('\n')
    env.render()
    sleep(0.1)
#print(s)

print(env.get_score())