from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
import ray

import matplotlib.pyplot as plt

SIM_RANGE = list(range(10,80))
SMOOTH = 50
CPUTC = 20

env_map = '''
........*......
.X......*......
........*......
...............
........*......
........*......
***.*********.*
........*......
........*......
........*...G..
........*......
...............
........*......
'''

@ray.remote
def run_single_sim(sims, smooth, cputc):
    print('only prims', sims, smooth)

    env = GridWorld(env_map)
    counter = 0
    while not env.finished():
        mcts = MCTS(env)
        a = mcts.run(sims, cputc)
        env.play(a)

        counter += 1
        if counter > 100000:
            break 

    return env.get_score()
@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


@ray.remote
def run_single_sim_options(sims, smooth, cputc):
    print('random opts', sims, smooth)

    env = GridWorld(env_map)
    env.add_option(GridWorldOption((2,11), {'all'}))
    env.add_option(GridWorldOption((9,4), {'all'}))
    env.add_option(GridWorldOption((11,11), {'all'}))

    counter = 0
    while not env.finished():
        mcts = MCTS(env)
        a = mcts.run(sims, cputc)
        env.play(a)

        counter += 1
        if counter > 100000:
            break 

    return env.get_score()
    
@ray.remote
def run_smoothed_options(sims, smooth_factor, cputc):
    features = [run_single_sim_options.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)



@ray.remote
def run_single_sim_doors(sims, smooth, cputc):
    print('door opts', sims, smooth)

    env = GridWorld(env_map)
    first_room_pos = [(i,j) for i in range(6) for j in range(8)]
    second_room_pos = [(i,j) for i in range(6) for j in range(9, 15)]
    third_room_pos = [(i,j) for i in range(7,13) for j in range(8)]
    fourth_room_pos = [(i,j) for i in range(7,13) for j in range(9,15)]

    env.add_option(GridWorldOption((3,8),  set(first_room_pos + second_room_pos + [(6,3)] + [(6,13)])))
    env.add_option(GridWorldOption((6,3),  set(first_room_pos + third_room_pos + [(3,8)] + [(11,8)])))
    env.add_option(GridWorldOption((6,13), set(second_room_pos + fourth_room_pos + [(3,8)] + [(11,8)])))
    env.add_option(GridWorldOption((11,8), set(third_room_pos + fourth_room_pos + [(6,3)] + [(6,13)])))

    counter = 0
    while not env.finished():
        mcts = MCTS(env)
        a = mcts.run(sims, cputc)
        env.play(a)

        counter += 1
        if counter > 100000:
            break 

    return env.get_score()

@ray.remote
def run_smoothed_doors(sims, smooth_factor, cputc):
    features = [run_single_sim_doors.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


features = [run_smoothed.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out = ray.get(features)

features = [run_smoothed_options.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out2 = ray.get(features)

features = [run_smoothed_doors.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out3 = ray.get(features)


print('RESULT 1', out)
print('RESULT 2', out2)
print('RESULT 3', out3)



plt.plot(out)
plt.plot(out2)
plt.plot(out3)


plt.savefig('result.png')