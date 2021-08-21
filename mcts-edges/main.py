from GridWorld import GridWorld
from MCTS import MCTS
import ray

import matplotlib.pyplot as plt

SIM_RANGE = list(range(10,60))
SMOOTH = 50
CPUTC = 20


@ray.remote
def run_single_sim(sims, smooth, cputc):
    print(sims, smooth)

    env = GridWorld('''
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
''')

    while not env.finished():
        mcts = MCTS(env)
        a = mcts.run(sims, cputc)
        env.play(a)

    return env.get_score()


@ray.remote
def run_smoothed(sims, smooth_factor, cputc):
    features = [run_single_sim.remote(sims, smooth, cputc) for smooth in range(smooth_factor)]
    totals = ray.get(features)
    print(totals)
    return sum(totals)/len(totals)


features = [run_smoothed.remote(sims, SMOOTH, CPUTC) for sims in SIM_RANGE]
out = ray.get(features)

plt.plot(out)

plt.savefig('result.png')