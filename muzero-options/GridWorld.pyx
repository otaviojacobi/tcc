# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, int32_t

cdef int8_t UP = 0
cdef int8_t DOWN = 1
cdef int8_t RIGHT = 2
cdef int8_t LEFT = 3

cdef class GridWorld:
    cdef public set possible_positions

    cdef public int32_t cur_x
    cdef public int32_t cur_y

    cdef public int32_t goal_x
    cdef public int32_t goal_y

    cdef public int32_t initial_x
    cdef public int32_t initial_y

    cdef public int32_t time_limit
    cdef public int32_t cur_t

    cdef public str grid_map

    def __init__(self, str grid_map, int32_t time_limit = -1):

        self.grid_map = grid_map
        self.cur_t = 0
        self.time_limit = time_limit 


        cdef list lines = grid_map.strip('\n ').split('\n')[4:]

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

    def __hash__(self):
      return hash((self.cur_x, self.cur_y))

    def __eq__(self, other):
      return self.cur_x == other.cur_x and self.cur_y == other.cur_y

    def __repr__(self):
        return str((self.cur_x, self.cur_y))

    cpdef void render(self):
        cdef list lines = self.grid_map.strip('\n ').split('\n')[4:]

        lines = [line.replace('X', '.') for line in lines]

        as_list = list(lines[self.cur_x])
        as_list[self.cur_y] = 'X'
        lines[self.cur_x] = ''.join(as_list)

        print('\n'.join(lines))
        print('\n')

    cpdef ((int, int), double, bint) step(self, int8_t move):

        if self.cur_x == self.goal_x and self.cur_y == self.goal_y:
            return (self.cur_x, self.cur_y), 0.0, True

        self.cur_t += 1

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


        if (possible_x, possible_y) in self.possible_positions:
            self.cur_x, self.cur_y = possible_x, possible_y

        if self.time_limit != -1 and self.cur_t >= self.time_limit:
            return (self.cur_x, self.cur_y), -1.0, True

        if self.cur_x == self.goal_x and self.cur_y == self.goal_y:
            return (self.cur_x, self.cur_y), -1.0, True

        return (self.cur_x, self.cur_y), -1.0, False

    cpdef object reset(self):
        self.cur_x = self.initial_x
        self.cur_y = self.initial_y
        self.cur_t = 0

        return (self.cur_x, self.cur_y)
