import numpy as np
from random import choice

from Hallway import Options

def render_V(ax, V, title, factor=4):
    grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    for v in V:
        grid[v[0]][v[1]] += factor * V[v]

    ax.imshow(grid)

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-0.5, 12, 1))
    ax.set_yticks(np.arange(-0.5, 12, 1))

    ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.set_title(title)

    ax.plot()

def filter_space(search_space, primitives, s):
    possibles = set()
    for option in search_space:
        if option in primitives:
            possibles.add(option)
        else:
            # first room
            if s[0] >= 7 and s[0] <= 11 and s[1] >= 1 and s[1] <= 5:
                if option == Options.OUT_11 or option == Options.OUT_12:
                    possibles.add(option)

            # second room
            if s[0] >= 1 and s[0] <= 5 and s[1] >= 1 and s[1] <= 5:
                if option == Options.OUT_21 or option == Options.OUT_22:
                    possibles.add(option)

            # third room
            if s[0] >= 1 and s[0] <= 6 and s[1] >= 7 and s[1] <= 11:
                if option == Options.OUT_31 or option == Options.OUT_32:
                    possibles.add(option)

            # fourth room
            if s[0] >= 8 and s[0] <= 11 and s[1] >= 7 and s[1] <= 11:
                if option == Options.OUT_41 or option == Options.OUT_42:
                    possibles.add(option)

    return possibles

def greedy(options):
    max_option = choice(list(options.keys()))
    maxo = options[max_option]
    for option, value in options.items():
        if value > maxo:
            max_option = option
            maxo = value
    return max_option

def e_greedy(options, e):
    if np.random.sample() <= e:
        return choice(list(options.keys()))
    else:
        return greedy(options)

def get_q_table(search_space, po, states, options_to_iterate):

    Q = {s: {action: 0.0 for action in filter_space(search_space, po, s)} for s in states}

    if options_to_iterate == 'multistep-only' or options_to_iterate == 'all':
        Q[(3, 6)][Options.OUT_32] = 0.0
        Q[(3, 6)][Options.OUT_11] = 0.0

        Q[(10, 6)][Options.OUT_41] = 0.0
        Q[(10, 6)][Options.OUT_12] = 0.0

        Q[(7, 9)][Options.OUT_42] = 0.0
        Q[(7, 9)][Options.OUT_31] = 0.0

        Q[(6, 2)][Options.OUT_12] = 0.0
        Q[(6, 2)][Options.OUT_22] = 0.0

    return Q
