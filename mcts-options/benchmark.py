import matplotlib.pyplot as plt
import ray

from gridworld import GridWorld, GridWorldOption
from mcts_options import MCTS

ray.init()

SIM_RANGE = list(range(7,100))
SMOOTH = 50
CPUTC = 200


@ray.remote
def run_single_sim(sims, smooth, cputc):
    print(sims, smooth)

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
    done = False
    total = 0
    while not done:
        mcts = MCTS(env.copy())
        a = mcts.run(sims, cputc)
        _, r, done = env.step(a)

        total += r

    return total



@ray.remote
def run_single_sim_options(sims, smooth, cputc):
    print(sims, smooth)

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

        a = mcts.run(sims, cputc)
        _, r, done = env.step(a)

        total += r

    return total


@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


@ray.remote
def run_smoothed_options(sims, smooth_factor, cputc):
    features = [run_single_sim_options.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)

features_opts = [run_smoothed_options.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
opts = ray.get(features_opts)

features = [run_smoothed.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out = ray.get(features)


print(out)
print(opts)


plt.plot(out)
plt.plot(opts)

plt.savefig('result.png')