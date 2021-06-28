import numpy as np
from enum import Enum
from random import choice
import matplotlib.pyplot as plt
from copy import deepcopy

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

def get_q_table(search_space, po, states, options_to_iterate):

    Q = {s: {action: -np.random.sample() for action in filter_space(search_space, po, s)} for s in states}

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

class Options(Enum):
    # Primitive options
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    # Multi-step options
    OUT_11 = 4
    OUT_12 = 5
    OUT_21 = 6
    OUT_22 = 7
    OUT_31 = 8
    OUT_32 = 9
    OUT_41 = 10
    OUT_42 = 11


class Hallway:
    def __init__(self):

        self.primitive_options = [Options.UP, Options.DOWN, Options.LEFT, Options.RIGHT]
        self.multistep_options = [Options.OUT_11,
                                  Options.OUT_12,
                                  Options.OUT_21,
                                  Options.OUT_22,
                                  Options.OUT_31,
                                  Options.OUT_32,
                                  Options.OUT_41,
                                  Options.OUT_42]

        self._all_options = self.primitive_options + self.multistep_options

        self._grid = self.__get_grid()
        self._states = self.__get_states()

        self._reward_means = get_q_table(self._all_options, self.primitive_options, self._states, 'all')

    def execute(self, s, option):

        self._current_state = s

        if option in self.primitive_options:
            next_state, r = self.__primitive_step(option)
            k = 1
        else:
            next_state, k, r = self.__composed_step(option)

        self._current_state = next_state

        return r, k

    def __primitive_step(self, option):

        real_option = option
        if np.random.random_sample() <= 1. / 3.:
            real_option = choice([op for op in self.primitive_options if op != option])

        if real_option == Options.UP:
            new_state = (self._current_state[0] - 1, self._current_state[1])
        elif real_option == Options.DOWN:
            new_state = (self._current_state[0] + 1, self._current_state[1])
        elif real_option == Options.LEFT:
            new_state = (self._current_state[0], self._current_state[1] - 1)
        elif real_option == Options.RIGHT:
            new_state = (self._current_state[0], self._current_state[1] + 1)
        else:
            raise Exception('Invalid option called' + str(option))

        if new_state not in self._states:
            new_state = self._current_state

        r = np.random.normal(self._reward_means[new_state][real_option], 0.1)

        return new_state, r

    # TODO: check if option is possible in current state
    def __composed_step(self, option):
        if option == Options.OUT_11:
            final_state = (6, 2)
        elif option == Options.OUT_12:
            final_state = (10, 6)
        elif option == Options.OUT_21:
            final_state = (6, 2)
        elif option == Options.OUT_22:
            final_state = (3, 6)
        elif option == Options.OUT_31:
            final_state = (3, 6)
        elif option == Options.OUT_32:
            final_state = (7, 9)
        elif option == Options.OUT_41:
            final_state = (7, 9)
        elif option == Options.OUT_42:
            final_state = (10, 6)

        k = 0
        total_r = 0
        while self._current_state != final_state:
            k += 1

            option = self.__options_policy(final_state)

            # outside of the room!
            if option is None:
                return self._current_state, k, total_r

            self._current_state, r = self.__primitive_step(option)

            total_r += (0.9 ** (k - 1)) * r

        return final_state, k, total_r

    def __options_policy(self, final_state):
        # first room
        s = tuple(self._current_state)
        if (s[0] >= 7 and s[0] <= 11 and s[1] >= 1 and s[1] <= 5) or (s == (6, 2) and final_state == (10, 6)) or (s == (10, 6) and final_state == (6, 2)):
            if final_state == (6, 2):
                if s in [(7, 2),
                         (8, 1), (8, 2), (8, 3),
                         (9, 1), (9, 2), (9, 3),
                         (10, 1), (10, 2), (10, 3),
                         (11, 1), (11, 2), (11, 3)]:
                    return Options.UP
                elif s in [(7, 4), (7, 5),
                           (8, 4), (8, 5),
                           (9, 4), (9, 5),
                           (10, 4), (10, 5),
                           (11, 4), (11, 5),
                           (7, 3), (10, 6)]:
                    return Options.LEFT
                elif s in [(7, 1)]:
                    return Options.RIGHT
                else:
                    raise Exception('Failed ' + str(s))

            if final_state == (10, 6):
                if s in [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5),
                         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
                         (9, 5), (6, 2)]:
                    return Options.DOWN
                elif s in [(9, 1), (9, 2), (9, 3), (9, 4),
                           (10, 1), (10, 2), (10, 3), (10, 4), (10, 5),
                           (11, 1), (11, 2), (11, 3), (11, 4)]:
                    return Options.RIGHT
                elif s in [(11, 5)]:
                    return Options.UP
                else:
                    raise Exception('Failed ' + str(s))

        # second room
        elif (s[0] >= 1 and s[0] <= 5 and s[1] >= 1 and s[1] <= 5) or (s == (3, 6) and final_state == (6, 2)) or (s == (6, 2) and final_state == (3, 6)):
            if final_state == (3, 6):
                if s in [(1, 1), (1, 2), (1, 3), (1, 4),
                         (2, 1), (2, 2), (2, 3),
                         (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
                         (4, 1), (4, 2), (4, 3), (4, 4),
                         (5, 1), (5, 2), (5, 3)]:
                    return Options.RIGHT
                elif s in [(1, 5), (2, 5), (2, 4)]:
                    return Options.DOWN
                elif s in [(4, 5), (5, 4), (5, 5), (6, 2)]:
                    return Options.UP
                else:
                    raise Exception('Failed ' + str(s))

            if final_state == (6, 2):
                if s in [(1, 1), (1, 2), (1, 3),
                         (2, 1), (2, 2), (2, 3),
                         (3, 1), (3, 2), (3, 3),
                                 (4, 2),
                                 (5, 2)]:
                    return Options.DOWN
                elif s in [(1, 4), (1, 5),
                           (2, 4), (2, 5),
                           (3, 4), (3, 5), (3, 6),
                           (4, 3), (4, 4), (4, 5),
                           (5, 3), (5, 4), (5, 5)]:
                    return Options.LEFT
                elif s in [(4, 1), (5, 1)]:
                    return Options.RIGHT
                else:
                    raise Exception('Failed ' + str(s))

        # third room
        elif (s[0] >= 1 and s[0] <= 6 and s[1] >= 7 and s[1] <= 11) or (s == (3, 6) and final_state == (7, 9)) or (s == (7, 9) and final_state == (3, 6)):
            if final_state == (3, 6):
                if s in [(4, 7), (4, 8), (4, 9), (4, 10), (4, 11),
                         (5, 7), (5, 8), (5, 9), (5, 10), (5, 11),
                         (6, 7), (6, 8), (6, 9), (6, 10), (6, 11),
                         (7, 9)]:
                    return Options.UP
                elif s in [(1, 8), (1, 9), (1, 10), (1, 11),
                           (2, 8), (2, 9), (2, 10), (2, 11),
                           (3, 7), (3, 8), (3, 9), (3, 10), (3, 11)]:
                    return Options.LEFT
                elif s in [(1, 7), (2, 7)]:
                    return Options.DOWN
                else:
                    raise Exception('Failed ' + str(s))

            if final_state == (7, 9):
                if s in [(1, 7), (1, 8),
                         (2, 7), (2, 8),
                         (3, 6), (3, 7), (3, 8),
                         (4, 7), (4, 8),
                         (5, 7), (5, 8),
                         (6, 7), (6, 8)]:
                    return Options.RIGHT
                elif s in [(1, 9), (1, 10), (1, 11),
                           (2, 9), (2, 10), (2, 11),
                           (3, 9), (3, 10), (3, 11),
                           (4, 9), (4, 10), (4, 11),
                           (5, 9), (5, 11),
                           (6, 9)]:
                    return Options.DOWN
                elif s in [(5, 10), (6, 10), (6, 11)]:
                    return Options.LEFT
                else:
                    raise Exception('Failed ' + str(s))

        # fourth room
        elif (s[0] >= 8 and s[0] <= 11 and s[1] >= 7 and s[1] <= 11) or (s == (7, 9) and final_state == (10, 6)) or (s == (10, 6) and final_state == (7, 9)):
            if final_state == (7, 9):
                if s in [(8, 7), (8, 8), (10, 6)]:
                    return Options.RIGHT
                elif s in [(9, 7), (9, 8), (9, 9), (9, 10), (9, 11),
                           (10, 7), (10, 8), (10, 9), (10, 10), (10, 11),
                           (11, 7), (11, 8), (11, 9), (11, 10), (11, 11), (8, 9)]:
                    return Options.UP
                elif s in [(8, 10), (8, 11)]:
                    return Options.LEFT
                else:
                    raise Exception('Failed ' + str(s))

            if final_state == (10, 6):
                if s in [(8, 8), (8, 9), (8, 10), (8, 11),
                         (9, 8), (9, 9), (9, 10), (9, 11),
                         (10, 8), (10, 9), (10, 10), (10, 11),
                         (11, 8), (11, 9), (11, 10), (11, 11), (10, 7)]:
                    return Options.LEFT
                elif s in [(8, 7), (9, 7), (7, 9)]:
                    return Options.DOWN
                elif s in [(11, 7)]:
                    return Options.UP
                else:
                    raise Exception('Failed ' + str(s))
        else:
            raise Exception('Current state is invalid' + str(s))

    def __get_states(self):
        states = set()
        for row in range(len(self._grid)):
            for column in range(len(self._grid[0])):
                if self._grid[row][column] > 0:
                    states.add((row, column))
        return states

    def __get_grid(self):
        return [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 2, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 0, 0, 2, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def __option_d(self, option):
        if option == Options.UP:
            return (-1, 0)
        elif option == Options.DOWN:
            return (1, 0)
        elif option == Options.LEFT:
            return (0, -1)
        elif option == Options.RIGHT:
            return (0, 1)
        else:
            raise Exception('Error')
