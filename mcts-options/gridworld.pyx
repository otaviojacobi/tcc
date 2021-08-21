# distutils: language = c++
# cython: language_level=3
from collections import defaultdict

cdef char UP = 0
cdef char DOWN = 1
cdef char RIGHT = 2
cdef char LEFT = 3

cdef str EMPTY = '.'
cdef str FILLED = '*'
cdef str POSITION = 'X'
cdef str GOAL = 'G'


cdef moves = [UP, DOWN, RIGHT, LEFT]


cdef class GridWorldOption:

    cdef int final_x
    cdef int final_y

    cdef set transitions

    cdef bint finished

    def __init__(self, final_state, transitions):
        self.final_x = final_state[0]
        self.final_y = final_state[1]
        self.finished = False
        self.transitions = transitions

    def get_action(self, state):
        cur_x = state.get_cur_x()
        cur_y = state.get_cur_y()

        if (self.final_x, self.final_y) not in self.transitions:
            self.finished = True
            if cur_x == self.final_x and cur_y == self.final_y - 1:
                return UP

            elif cur_x == self.final_x and cur_y == self.final_y + 1:
                return DOWN

            elif cur_x == self.final_x - 1 and cur_y == self.final_y:
                return RIGHT

            elif cur_x == self.final_x + 1 and cur_y == self.final_y:
                return LEFT
            else:
                raise Exception("boom")

        start = (cur_x, cur_y)

        open_set = set([start])
        came_from = {}

        g_score = defaultdict(lambda: 9999999)
        g_score[start] = 0

        f_score = defaultdict(lambda: 9999999)
        f_score[start] = self._h(start)

        while len(open_set) != 0:
            #TODO: use min-heap to make it O(1)
            current = self._get_min(open_set, f_score)

            if current == (self.final_x, self.final_y):
                return self._first_action(came_from, current)

            open_set.remove(current)

            for move in self._possible_moves(current):
                nex_x = current[0]
                nex_y = current[1]

                if move == UP:
                    nex_y += 1
                elif move == DOWN:
                    nex_y -= 1
                elif move == RIGHT:
                    nex_x += 1
                elif move == LEFT:
                    nex_x -= 1

                neib = (nex_x, nex_y)
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neib]:
                    came_from[neib] = current
                    g_score[neib] = tentative_g_score
                    f_score[neib] = g_score[neib] + self._h(neib)

                    if neib not in open_set:
                        open_set.add(neib)


    def _first_action(self, came_from, current):
        total_path = []
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)

        try:
            next_pos = total_path[-2]
        except Exception as e:
            next_pos = (self.final_x, self.final_y)
        first_pos = total_path[-1]

        if next_pos[0] - first_pos[0] == 1:
            return RIGHT
        elif next_pos[0] - first_pos[0] == -1:
            return LEFT
        elif next_pos[1] - first_pos[1] == 1:
            return UP
        elif next_pos[1] - first_pos[1] == -1:
            return DOWN

    def is_over(self, state):
        cur_x = state.get_cur_x()
        cur_y = state.get_cur_y()
        return cur_x == self.final_x and cur_y == self.final_y or self.finished

    def _h(self, state):
        return 0

    def _get_min(self, open_set, f_score):
        min_value = 999999
        best_node = None
        for node in open_set:
            if f_score[node] < min_value:
                min_value = f_score[node]
                best_node = node

        return best_node

    def _possible_moves(self, current):

        valid_moves = []
        for move in moves:
            nex_x = current[0]
            nex_y = current[1]

            if move == UP:
                nex_y += 1
            elif move == DOWN:
                nex_y -= 1
            elif move == RIGHT:
                nex_x += 1
            elif move == LEFT:
                nex_x -= 1

            if (nex_x, nex_y) in self.transitions:
                valid_moves.append(move)

        return valid_moves

cdef class GridWorld:
    cdef int cur_x
    cdef int cur_y
    cdef int goal_x
    cdef int goal_y

    cdef int init_x
    cdef int init_y

    cdef set valid_positions

    cdef bint finished

    cdef list base_options

    def __init__(self, str position_map):

        self.base_options = []

        if position_map == '':
            return

        self.finished = False
        self.valid_positions = set()

        lines = position_map.split('\n')
        for line_idx in range(len(lines)):
            for char_idx in range(len(lines[line_idx])):

                if lines[line_idx][char_idx] != FILLED:
                    self.valid_positions.add((char_idx, line_idx))

                if lines[line_idx][char_idx] == GOAL:
                    self.goal_x = char_idx
                    self.goal_y = line_idx

                if lines[line_idx][char_idx] == POSITION:
                    self.init_x = char_idx
                    self.init_y = line_idx
                    self.cur_x = char_idx
                    self.cur_y = line_idx

    def add_options(self, options):
        self.base_options = options

    def get_options(self):
        options = []
        for move in self.legal_moves():

            nex_x = self.cur_x
            nex_y = self.cur_y

            if move == UP:
                nex_y += 1
            elif move == DOWN:
                nex_y -= 1
            elif move == RIGHT:
                nex_x += 1
            elif move == LEFT:
                nex_x -= 1

            options.append(GridWorldOption((nex_x, nex_y), self.valid_positions.copy()))
        
        return options + self.base_options


    def step(self, action):
        if self.finished:
            return (self.cur_x, self.cur_y), 0.0, True

        nex_x = self.cur_x
        nex_y = self.cur_y

        if action == UP:
            nex_y += 1
        elif action == DOWN:
            nex_y -= 1
        elif action == RIGHT:
            nex_x += 1
        elif action == LEFT:
            nex_x -= 1

        if (nex_x, nex_y) in self.valid_positions:
            self.cur_x = nex_x
            self.cur_y = nex_y

        if self.cur_x == self.goal_x and self.cur_y == self.goal_y:
            self.finished = True
            return (self.cur_x, self.cur_y), 1000.0, True

        return (self.cur_x, self.cur_y), -1.0, False

    def copy(self):
        gw = GridWorld('')

        gw.add_options(self.base_options)

        gw.set_cur_x(self.get_cur_x())
        gw.set_cur_y(self.get_cur_y())
        gw.set_goal_x(self.get_goal_x())
        gw.set_goal_y(self.get_goal_y())

        gw.set_init_x(self.get_init_x())
        gw.set_init_y(self.get_init_y())

        gw.set_valid_positions(self.get_valid_positions().copy())
        gw.set_over(self.is_over())

        return gw

    def state(self):
        return (self.cur_x, self.cur_y)

    def legal_moves(self):
        if self.finished:
            return []

        # valid_moves = []
        # for move in moves:
        #     nex_x = self.cur_x
        #     nex_y = self.cur_y

        #     if move == UP:
        #         nex_y += 1
        #     elif move == DOWN:
        #         nex_y -= 1
        #     elif move == RIGHT:
        #         nex_x += 1
        #     elif move == LEFT:
        #         nex_x -= 1

        #     if (nex_x, nex_y) in self.valid_positions:
        #         valid_moves.append(move)

        # return valid_moves
        return moves

    def reset(self):
        self.finished = False
        self.cur_x = self.init_x
        self.cur_y = self.init_y

    cpdef int get_cur_x(self):
        return self.cur_x

    cpdef int set_cur_x(self, new_x):
        self.cur_x = new_x

    cpdef int get_cur_y(self):
        return self.cur_y

    cpdef int set_cur_y(self, new_y):
        self.cur_y = new_y

    cpdef int get_goal_x(self):
        return self.goal_x

    cpdef int set_goal_x(self, new_goal_x):
        self.goal_x = new_goal_x

    cpdef int get_goal_y(self):
        return self.goal_y

    cpdef int set_goal_y(self, new_goal_y):
        self.goal_y = new_goal_y

    cpdef int get_init_x(self):
        return self.init_x

    cpdef int set_init_x(self, new_init_x):
        self.init_x = new_init_x

    cpdef int get_init_y(self):
        return self.init_y

    cpdef int set_init_y(self, new_init_y):
        self.init_y = new_init_y

    cpdef set get_valid_positions(self):
        return self.valid_positions

    cpdef set set_valid_positions(self, new_valid_positions):
        self.valid_positions = new_valid_positions

    cpdef bint is_over(self):
        return self.finished

    cpdef void set_over(self, bint over):
        self.finished = over
