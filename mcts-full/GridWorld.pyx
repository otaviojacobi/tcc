# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t
from libc.math cimport INFINITY, abs
from collections import defaultdict

from GridWorldOption import GridWorldOption

cdef int8_t UP = 0
cdef int8_t DOWN = 1
cdef int8_t RIGHT = 2
cdef int8_t LEFT = 3

cdef class GridWorld:
    cdef public bint is_over
    cdef public double score
    cdef public set possible_positions

    cdef public int cur_x
    cdef public int cur_y

    cdef public int goal_x
    cdef public int goal_y

    cdef public int initial_x
    cdef public int initial_y

    cdef public str grid_map

    cdef list composed_options

    def __init__(self, str grid_map = None):

        if grid_map == None:
            return

        self.grid_map = grid_map

        cdef list lines = grid_map.strip('\n ').split('\n')
        self.possible_positions = set()
        for x, line in enumerate(lines):
            for y, char in enumerate(line):
                if char.upper() == 'X':
                    self.cur_x, self.cur_y = x, y
                    self.initial_x, self.initial_y = x, y

                if char.upper() == 'G':
                    self.goal_x, self.goal_y = x, y

                if char == '.' or char == 'X' or char == 'G':
                    self.possible_positions.add((x, y))

        self.composed_options = list()
        self.is_over = False
        self.score = 0.0

    cpdef bint finished(self):
        return self.is_over

    cpdef double get_score(self):
        return self.score

    cpdef list legal_moves(self):
        if self.is_over:
            return []
        return [UP, DOWN, RIGHT, LEFT]

    cpdef double _inf(self):
        return INFINITY

    cpdef void add_option(self, object option):
        self.composed_options.append(option)

    cpdef list get_valid_options(self):
        cdef list valid_options = list()

        for option in self.composed_options:
            if option.is_valid_option(self):
                valid_options.append(option)

        for move in self.legal_moves():

            next_x = self.cur_x
            next_y = self.cur_y
            if move == UP:
                next_x -= 1
            elif move == DOWN:
                next_x += 1
            elif move == RIGHT:
                next_y += 1
            elif move == LEFT:
                next_y -= 1

            valid_options.append(GridWorldOption((next_x, next_y), {'all'}, move, primitive=move))

        return valid_options


    # This is a debugging/test function
    # It returns -MIN_NUMBER_STEPS to reach the goal G from current position
    cpdef double get_oracle_score(self):

        if self.is_over:
            return 0

        x, y = self.cur_x, self.cur_y
        gx, gy = self.goal_x, self.goal_y

        cdef list stack = list()
        cdef object run_board = self.copy()

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
                counter = 0
                while current in came_from.keys():
                    current = came_from[current]
                    counter += 1
                return -counter

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

                if (possible_x, possible_y) in self.possible_positions:
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

        print('ERROR!')

    cpdef bint is_leaf(self):
        return self.cur_x == self.goal_x and self.cur_y == self.goal_y

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

    def render(self):
        cdef list lines = self.grid_map.strip('\n ').split('\n')

        lines = [line.replace('X', '.') for line in lines]

        as_list = list(lines[self.cur_x])
        as_list[self.cur_y] = 'X'
        lines[self.cur_x] = ''.join(as_list)

        print('\n'.join(lines))

    def get_option_by_id(self, int8_t option_id):
        if option_id in [UP, DOWN, RIGHT, LEFT]:
            return GridWorldOption((-1, -1), {'all'}, option_id, primitive=option_id)

        for option in self.composed_options:
            if option.opt_id == option_id:
                return option

        print(f'BOOM opt id {option_id} not found')
        exit(-1)

    def play(self, object option):

        if option.primitive != -1:
            return self.step(option.get_action(self))

        cum_r = 0.0
        while True:
            move = option.get_action(self)
            if move == -1 or self.is_over:
                break
            s, r, f = self.step(move)
            cum_r += r

        return s, cum_r, f

    def step(self, int8_t move):
        if self.is_over:
            return (self.cur_x, self.cur_y), 0.0, True

        possible_x = self.cur_x
        possible_y = self.cur_y
        if move == UP:
            possible_x -= 1
        elif move == DOWN:
            possible_x += 1
        elif move == RIGHT:
            possible_y += 1
        elif move == LEFT:
            possible_y -= 1
        else:
            print('Tried to play unknown action ', move)
            exit(-1)

        if (possible_x, possible_y) in self.possible_positions:
            self.cur_x, self.cur_y = possible_x, possible_y

        if self.cur_x == self.goal_x and self.cur_y == self.goal_y:
            self.is_over = True
        else:
            self.score -= 1.0

        if self.is_over:
            return (self.cur_x, self.cur_y), 0.0, True
        else:
            return (self.cur_x, self.cur_y), -1.0, False

    cpdef object reset(self):
        self.is_over = False
        self.cur_x = self.initial_x
        self.cur_y = self.initial_y
        self.score = 0.0

    cpdef object copy(self):
        g = GridWorld()

        g.is_over = self.is_over
        g.score = self.score

        #TODO: do I need to deepcopy this ? considering it possible_positions shouldn't change, I don't think so
        g.possible_positions = self.possible_positions

        g.cur_x = self.cur_x
        g.cur_y = self.cur_y

        g.goal_x = self.goal_x
        g.goal_y = self.goal_y

        g.initial_x = self.initial_x
        g.initial_y = self.initial_y

        g.composed_options = self.composed_options

        return g