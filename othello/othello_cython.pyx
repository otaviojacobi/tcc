# distutils: language = c++
#cython: language_level=3

from libcpp.set cimport set

cdef char OUTER = -2
cdef char EMPTY = 0
cdef char BLACK = -1
cdef char WHITE = 1

cdef char UP = -10
cdef char DOWN = 10
cdef char LEFT = -1
cdef char RIGHT = 1
cdef char UP_RIGHT = -9
cdef char DOWN_RIGHT = 11
cdef char DOWN_LEFT = 9
cdef char UP_LEFT = -11

cdef char[8] DIRECTIONS = [UP, DOWN, LEFT, RIGHT, UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT]

cdef class Othello:
    cdef char[100] board
    cdef set[char] empties
    cdef char current_player

    def __init__(self):
        self.board = [OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        OUTER, OUTER, EMPTY, EMPTY, EMPTY, WHITE, BLACK, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY,
                        EMPTY, EMPTY, BLACK, WHITE, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                        EMPTY, OUTER, OUTER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OUTER, OUTER,
                        OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER]

        for i in range(100):
            if self.board[i] == EMPTY:
                self.empties.insert(i)

        self.current_player = BLACK

    cpdef char player(self):
        return self.current_player
    
    cpdef char opponent(self):
        return -1 * self.current_player

    cpdef bint has_bracket(self, char move):
        for direction in DIRECTIONS:
            if self.find_bracket(move, direction) != -1:
                return 1
        return 0

    cpdef char find_bracket(self, char square, char direction):
        cdef char bracket = square + direction
        if self.board[bracket] == self.current_player:
            return -1

        op = self.opponent()
        while self.board[bracket] == op:
            bracket += direction

        if self.board[bracket] == OUTER or self.board[bracket] == EMPTY:
            return -1

        return bracket

    def legal_moves(self):
        cdef list moves = []
        for move in self.empties:
            if self.has_bracket(move):
                moves.append(move)

        return moves