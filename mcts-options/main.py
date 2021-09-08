from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS

with open('easy.txt') as f:
    env_map = f.read()


sims = 100
cputc = 2

first_room_pos = [(i,j) for i in range(6) for j in range(8)]
second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

options = [
  # primitives, (0,0) is meaningless
  GridWorldOption((0, 0),  {'all'}, 0, 0),
  GridWorldOption((0, 0),  {'all'}, 1, 1),
  GridWorldOption((0, 0),  {'all'}, 2, 2),
  GridWorldOption((0, 0),  {'all'}, 3, 3),

#   GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 4),
#   GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)]), 5),
#   GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)]), 6),
#   GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)]), 7),
]

env = GridWorld(env_map)
mcts = MCTS(env, options) 

# while not env.finished():
#     mcts = MCTS(env, options) 

#     a = mcts.run(sims, cputc)
#     env.step(a)
#     #mcts.set_new_head(a)
#     env.render()
# print(env.get_score())

for _ in range(100):
    env = GridWorld(env_map)
    #mcts.info(2)
    while not env.finished():
        mcts.reset(env)
        a = mcts.run(sims, cputc)
        env.step(a)
        #mcts.set_new_head(a)
        #env.render()
    print(env.get_score())

mcts.save('prim.pickle')
#print(env.get_score())


