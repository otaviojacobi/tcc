from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from mcts.MCTS import MCTS

from numpy.random import choice
import numpy as np

import ray
import matplotlib.pyplot as plt

SIM_RANGE = list(range(10, 100, 5))
SMOOTH = 10

MAP_NAME = './maps/door.map'
with open(MAP_NAME) as f:
    env_map = f.read()

@ray.remote
def run_single_sim(sims, smooth):
    print('only prims', sims, smooth)

    options = [
      # primitives, (0,0) is meaningless
      GridWorldOption((0, 0),  {'all'}, 0, 0),
      GridWorldOption((0, 0),  {'all'}, 1, 1),
      GridWorldOption((0, 0),  {'all'}, 2, 2),
      GridWorldOption((0, 0),  {'all'}, 3, 3),
    ]

    env = GridWorld(env_map)
    done = False
    R = 0.0
    while not done:
        mcts = MCTS(env.copy(), options)
        pi = mcts.run_sim(sims)
        #opt = choice(options, 1, p=pi)[0]
        opt_index = np.argmax(pi)
        opt = options[opt_index]
        while True:
            a, should_break = opt.get_action(env)

            if a == -1 or done:
                break
            
            _, r, done = env.step(a)

            R += r

            if should_break:
                break

    return R
@ray.remote
def run_smoothed(sims, smooth_factor):
    features = [run_single_sim.remote(sims, smooth) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


@ray.remote
def run_single_sim_options(sims, smooth):
    print('random opts', sims, smooth)

    env = GridWorld(env_map)

    options = [
      # primitives, (0,0) is meaningless
      GridWorldOption((0, 0),   {'all'}, 0, 0),
      GridWorldOption((0, 0),   {'all'}, 1, 1),
      GridWorldOption((0, 0),   {'all'}, 2, 2),
      GridWorldOption((0, 0),   {'all'}, 3, 3),
      GridWorldOption((2, 11),  {'all'}, 4),
      GridWorldOption((9, 4),   {'all'}, 5),
    ]

    env = GridWorld(env_map)
    done = False
    R = 0.0
    while not done:
        mcts = MCTS(env.copy(), options)
        pi = mcts.run_sim(sims)
        #opt = choice(options, 1, p=pi)[0]
        opt_index = np.argmax(pi)
        opt = options[opt_index]
        while True:
            a, should_break = opt.get_action(env)

            if a == -1 or done:
                break
            
            _, r, done = env.step(a)

            R += r

            if should_break:
                break

    return R
    
@ray.remote
def run_smoothed_options(sims, smooth_factor):
    features = [run_single_sim_options.remote(sims, smooth) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)



@ray.remote
def run_single_sim_doors(sims, smooth):
    print('door opts', sims, smooth)

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
      GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)]), 4),
      GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)]), 5),
      GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)]), 6),
      GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)]), 7),
    ]

    env = GridWorld(env_map)
    done = False
    R = 0.0
    while not done:
        mcts = MCTS(env.copy(), options)
        pi = mcts.run_sim(sims)
        #opt = choice(options, 1, p=pi)[0]
        opt_index = np.argmax(pi)
        opt = options[opt_index]
        while True:
            a, should_break = opt.get_action(env)

            if a == -1 or done:
                break
            
            _, r, done = env.step(a)

            R += r

            if should_break:
                break

    return R

@ray.remote
def run_smoothed_doors(sims, smooth_factor):
    features = [run_single_sim_doors.remote(sims, smooth) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


features = [run_smoothed.remote(sims, SMOOTH) for sims in SIM_RANGE]
out = ray.get(features)

features = [run_smoothed_options.remote(sims, SMOOTH) for sims in SIM_RANGE]
out2 = ray.get(features)

features = [run_smoothed_doors.remote(sims, SMOOTH) for sims in SIM_RANGE]
out3 = ray.get(features)


print('RESULT 1', out)
print('RESULT 2', out2)
print('RESULT 3', out3)

plt.title('MCTS-O: Planning with Options, Acting with options following Argmax')

plt.ylabel('Average Total Undiscounted Return')
plt.xlabel('MCTS Simulations')

plt.plot(SIM_RANGE, out, label='primitive options')
plt.plot(SIM_RANGE, out2, label='random options')
plt.plot(SIM_RANGE, out3, label='dooor options')

plt.hlines(-24, SIM_RANGE[0], SIM_RANGE[-1], colors='red', label='optimal')

mini = min([min(out), min(out2), min(out3)])
plt.ylim((mini,0))

plt.legend()
#plt.show()

plt.savefig('test.png')