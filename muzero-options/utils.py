import numpy as np 

import matplotlib.pyplot as plt

def get_grid(MAP_NAME):
    with open(MAP_NAME) as f:
        env_map = f.read()

    env_map = env_map.split('\n')[4:]


    grid = np.zeros((len(env_map), len(env_map[0])))
    for i in range(len(env_map)):
        for j in range(len(env_map[0])):
            if env_map[i][j] != '.':
                grid[i][j] = -1
            else:
                grid[i][j] = 0

    return grid
 

def plot_mu_v(mu, MAP_NAME): 

    grid = get_grid(MAP_NAME)

    mini = min(mu.f.v_table.values())
    maxi = max(mu.f.v_table.values())
    for k, v in mu.f.v_table.items():
        grid[k] = (v - mini)/(maxi-mini)

    _, ax = plt.subplots()
    ax.imshow(grid)

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-0.5, 0, 1))
    ax.set_yticks(np.arange(-0.5, 0, 1))

    ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.set_title('')

    ax.plot()

def plot_trajectory(states, MAP_NAME):

    grid = get_grid(MAP_NAME)

    for s in states:
        grid[s] = 2
        
    _, ax = plt.subplots()
    ax.imshow(grid)

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-0.5, 0, 1))
    ax.set_yticks(np.arange(-0.5, 0, 1))

    ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.set_title('')

    ax.plot()