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

    cdef set activate_positions
    cdef public int8_t primitive
    cdef public bint executed

    cdef public int8_t opt_id

    def __init__(self, tuple final_state, set activate_positions, int8_t opt_id, int8_t primitive = -1):
        self._final_x, self._final_y = final_state
        self.activate_positions = activate_positions
        self.opt_id = opt_id
        self.primitive = primitive
        self.executed = False

    def __hash__(self):
      return self.opt_id

    def __eq__(self, other):
      return self.opt_id == other.opt_id

    def __repr__(self):
        return str(self.opt_id)

    cpdef bint is_valid(self, object state):

        if self.primitive != -1:
            return True

        # do not allow for options that take you to the same place
        # TODO: be careful about single step actions
        if state[0] == self._final_x and state[1] == self._final_y:
            return False

        if 'all' in self.activate_positions:
            return True

        return (state[0], state[1]) in self.activate_positions

    # CAUTION ! this function returns -1 when the option finishes !
    cpdef (int8_t, bint) get_action(self, object grid_world):

        #TODO: not STATELESS !!!!
        if self.primitive != -1:
            return self.primitive, True

        x, y = grid_world.cur_x, grid_world.cur_y
        gx, gy = self._final_x, self._final_y

        if x == gx and y == gy:
          return -1, True

        cdef list stack = list()
        cdef object run_board = grid_world

        cdef set open_set = set()
        open_set.add((x,y))
        cdef dict came_from = {}

        g_score = defaultdict(self._inf)
        g_score[(x, y)] = 0

        f_score = defaultdict(self._inf)
        f_score[(x, y)] = self._h((x, y), (gx, gy))

        cdef object current
        while len(open_set) != 0:

            current = self._lowest(open_set, f_score)
            x, y = current
            if x == gx and y == gy:
                return self._first_action(came_from, current), False

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
                    f_score[(neib_x, neib_y)] = g_score[(neib_x, neib_y)] + self._h((neib_x, neib_y), (gx, gy)) #TODO: _h(neib)

                    if (neib_x, neib_y) not in open_set:
                        open_set.add((neib_x, neib_y))

    cpdef object _lowest(self, set open_set, object f_score):
        cdef double high = INFINITY
        cdef object best_node
        for node in open_set:
            if f_score[node] < high:
                high = f_score[node]
                best_node = node

        return best_node

    cpdef int _h(self, tuple cur, tuple goal):
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

cdef class GridWorldMacroAction:
    cdef public int8_t primitive
    cdef public int8_t cur_count
    cdef public int8_t repeat
    cdef public int8_t opt_id


    def __init__(self, int8_t primitive, int8_t repeat, int8_t opt_id):
        self.primitive = primitive
        self.repeat = repeat
        self.opt_id = opt_id
        self.cur_count = 0

    def __hash__(self):
      return self.opt_id

    def __eq__(self, other):
      return self.opt_id == other.opt_id

    def __repr__(self):
        return str(self.opt_id)

    cpdef bint is_valid(self, object state):
            return True

    # CAUTION ! this function returns -1 when the option finishes !
    cpdef (int8_t, bint) get_action(self, object grid_world):
        self.cur_count += 1

        if self.cur_count > self.repeat:
            print("Macro action state is invalid !!")

        if self.cur_count == self.repeat:
            self.cur_count = 0
            return self.primitive, True
        
        return self.primitive, False