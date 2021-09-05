from GridWorld import GridWorld
from GridWorldOption import GridWorldOption
from MCTS import MCTS
import ray

import matplotlib.pyplot as plt

SIM_RANGE = list(range(12,52))
SMOOTH = 5
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

    options = [
      # primitives, (0,0) is meaningless
      GridWorldOption((0, 0),  {'all'}, 0, 0),
      GridWorldOption((0, 0),  {'all'}, 1, 1),
      GridWorldOption((0, 0),  {'all'}, 2, 2),
      GridWorldOption((0, 0),  {'all'}, 3, 3),
    ]

    env = GridWorld(env_map)
    while not env.finished():
        mcts = MCTS(env, options)
        a = mcts.run(sims, cputc)
        env.step(a)

    return env.get_score()
@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


@ray.remote
def run_single_sim_reuse(sims, smooth, cputc):
    print('only prims', sims, smooth)

    options = [
      # primitives, (0,0) is meaningless
      GridWorldOption((0, 0),  {'all'}, 0, 0),
      GridWorldOption((0, 0),  {'all'}, 1, 1),
      GridWorldOption((0, 0),  {'all'}, 2, 2),
      GridWorldOption((0, 0),  {'all'}, 3, 3),
    ]

    env = GridWorld(env_map)
    while not env.finished():
        mcts = MCTS(env, options)
        a = mcts.run(sims, cputc)
        env.step(a)

    return env.get_score()
@ray.remote
def run_smoothed_reuse(sims, smooth_factor, cputc):
    features = [run_single_sim_reuse.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)

features = [run_smoothed.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out = ray.get(features)

features = [run_smoothed_reuse.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out2 = ray.get(features)


print('RESULT 1', out)
print('RESULT 2', out2)


plt.title('MCTS-O: Planning with Options, Acting with actions (reusing tree)')

plt.ylabel('Average Total Return')
plt.xlabel('MCTS Simulations')

plt.plot(SIM_RANGE, out, label='No tree reuse')
plt.plot(SIM_RANGE, out2, label='Tree reuse')


plt.hlines(-20, SIM_RANGE[0], SIM_RANGE[-1], colors='red', label='optimal')

mini = min([min(out), min(out2)])
plt.ylim((mini,0))

plt.legend()
#plt.show()

plt.savefig('test.png')