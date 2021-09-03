from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
import time

with open('easy.txt') as f:
    env_map = f.read()

env = GridWorld(env_map)
first_room_pos = [(i,j) for i in range(6) for j in range(8)]
second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

options = [
    # primitives, (0,0) is meaningless
    GridWorldOption((0, 0), {'all'}, 0, 0),
    GridWorldOption((0, 0), {'all'}, 1, 1),
    GridWorldOption((0, 0), {'all'}, 2, 2),
    GridWorldOption((0, 0), {'all'}, 3, 3),
    GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 4),
    GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)]), 5),
    GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)]), 6),
    GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)]), 7),
]

TIME_LIMIT = 40
env = GridWorld(env_map)


pre_booted = False
while not env.finished():
    if not pre_booted:
        mcts = MCTS(env, options)

    option, _ = mcts.run(TIME_LIMIT, 20)

    env_copy = env.copy()
    steps = 0
    while True:
        action = option.get_action(env_copy)
        if env_copy.finished() or action == -1:
            break
        env_copy.step(action)
        steps += 1

    option.executed = False

    mcts = MCTS(env_copy, options)
    while True:
        action = option.get_action(env)
        if env.finished() or action == -1:
            break
        env.step(action)
        mcts.run(TIME_LIMIT-1, 20)
        pre_booted = True

print(env.get_score())