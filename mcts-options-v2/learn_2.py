from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTSLearn import MCTS

import pickle

with open('easy.txt') as f:
    env_map = f.read()

env = GridWorld(env_map)
first_room_pos = [(i,j) for i in range(6) for j in range(8)]
second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

options = [
    # primitives, (0,0) is meaningless
    GridWorldOption((0, 0),   {'all'}, 0, 0),
    GridWorldOption((0, 0),   {'all'}, 1, 1),
    GridWorldOption((0, 0),   {'all'}, 2, 2),
    GridWorldOption((0, 0),   {'all'}, 3, 3),
    #GridWorldOption((9, 12),   {'all'}, 8),

    GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 4),
    GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)]), 5),
    GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)]), 6),
    GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)]), 7),
]

TIME_LIMIT = 30
cputc = 20

env = GridWorld(env_map)
mcts = MCTS(env, options)

results = []
for learning in range(100):
    print(learning)
    env = GridWorld(env_map)
    total = 0
    while not env.finished():
        mcts.reset(env)
        option, _ = mcts.learn(TIME_LIMIT, cputc)
        option.executed = False
        while True:
            action = option.get_action(env)

            if action == -1 or env.finished():
                break
            env.step(action)
            total -= 1
        option.executed = False
        
    results.append(env.get_score())
    
    print(total)
    print(env.get_score())

with open('results/door_30_steps.pickle', 'wb') as f:
    pickle.dump(results, f)

mcts.save('models/door_30_steps.pickle')