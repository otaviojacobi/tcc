# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t
from libc.math cimport INFINITY, abs
from collections import defaultdict

cdef int8_t UP = 0
cdef int8_t DOWN = 1
cdef int8_t RIGHT = 2
cdef int8_t LEFT = 3

cdef class GridWorldOption:
    cdef int _final_x
    cdef int _final_y

    cdef public bint finished

    cdef set activate_positions

    cdef public bint is_primitive

    def __init__(self, tuple final_state, set activate_positions, bint is_primitive=False):
        self._final_x, self._final_y = final_state
        self.activate_positions = activate_positions
        self.finished = False
        self.is_primitive = is_primitive

    cpdef bint is_valid_option(self, object grid_world):

        # do not allow for options that take you to the same place
        # TODO: be careful about single step actions
        if grid_world.cur_x == self._final_x and grid_world.cur_y == self._final_y:
            return False

        if 'all' in self.activate_positions:
            return True

        return (grid_world.cur_x, grid_world.cur_y) in self.activate_positions

    # CAUTION ! this function returns -1 when the option finishes !
    cpdef int8_t get_action(self, object grid_world):

        x, y = grid_world.cur_x, grid_world.cur_y
        gx, gy = self._final_x, self._final_y

        if (gx, gy) not in grid_world.possible_positions:
            self.finished = True

            if x == gx and y == gy - 1:
                return RIGHT

            elif x == gx and y == gy + 1:
                return LEFT

            elif x == gx - 1 and y == gy:
                return DOWN

            elif x == gx + 1 and y == gy:
                return UP

        if x == gx and y == gy:
          self.finished = True
          return -1

        cdef list stack = list()
        cdef object run_board = grid_world.copy()

        cdef set open_set = set()
        open_set.add((x,y))
        cdef dict came_from = {}

        g_score = defaultdict(self._inf)
        g_score[(x, y)] = 0

        f_score = defaultdict(self._inf)
        f_score[(x, y)] = self.h((x, y), (gx, gy))

        cdef object current
        while len(open_set) != 0:

            current = self.lowest(open_set, f_score)
            x, y = current
            if x == gx and y == gy:
                return self._first_action(came_from, current)

            open_set.remove(current)

            for move in range(4):
                possible_x = x
                possible_y = y
                if move == UP:
                    possible_x -= 1
                elif move == DOWN:
                    possible_x += 1
                elif move == RIGHT:
                    possible_y += 1
                elif move == LEFT:
                    possible_y -= 1

                if (possible_x, possible_y) in grid_world.possible_positions:
                    neib_x, neib_y = possible_x, possible_y
                else:
                    neib_x, neib_y = x, y

                tentative_g_score = g_score[(x, y)] + 1
                if tentative_g_score < g_score[(neib_x, neib_y)]:
                    came_from[(neib_x, neib_y)] = (x, y)
                    g_score[(neib_x, neib_y)] = tentative_g_score
                    f_score[(neib_x, neib_y)] = g_score[(neib_x, neib_y)] + self.h((neib_x, neib_y), (gx, gy)) #TODO: h(neib)

                    if (neib_x, neib_y) not in open_set:
                        open_set.add((neib_x, neib_y))

    cpdef object lowest(self, set open_set, object f_score):
        cdef double high = INFINITY
        cdef object best_node
        for node in open_set:
            if f_score[node] < high:
                high = f_score[node]
                best_node = node

        return best_node

    cpdef int h(self, tuple cur, tuple goal):
        return abs(cur[0] - goal[0]) + abs(cur[1] - goal[1])

    cpdef double _inf(self):
        return INFINITY

    cpdef int8_t _first_action(self, dict came_from, tuple current):
        cdef list total_path = []
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)

        try:
            next_pos = total_path[-2]
        except Exception as e:
            next_pos = (self._final_x, self._final_y)
        first_pos = total_path[-1]

        if next_pos[0] - first_pos[0] == 1:
            return DOWN
        elif next_pos[0] - first_pos[0] == -1:
            return UP
        elif next_pos[1] - first_pos[1] == 1:
            return RIGHT
        elif next_pos[1] - first_pos[1] == -1:
            return LEFT
