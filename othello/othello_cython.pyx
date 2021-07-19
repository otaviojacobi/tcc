# distutils: language = c++
# cython: language_level=3

from libc.string cimport memcpy

import numpy as np

cdef char OUTER = -2
# DO NOT CHANGE EMTPY VALUE
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

cdef char[64] VALID_IDXS = [11, 12, 13, 14, 15, 16, 17, 18,
                            21, 22, 23, 24, 25, 26, 27, 28,
                            31, 32, 33, 34, 35, 36, 37, 38,
                            41, 42, 43, 44, 45, 46, 47, 48,
                            51, 52, 53, 54, 55, 56, 57, 58,
                            61, 62, 63, 64, 65, 66, 67, 68,
                            71, 72, 73, 74, 75, 76, 77, 78,
                            81, 82, 83, 84, 85, 86, 87, 88]


cpdef char action_to_move(char action):
    return (10 * (action // 8)) + 11 + (action % 8)

cpdef char move_to_action(char move):
    return move - 11 - 2 * (move//10 - 1)

#TODO: pass move is yet to be done
cdef class Othello:
    cdef char[100] board
    cdef char[100] empties
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

        self.empties = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1.,
                        1., 1., 1., 1., 1., 1., 0., 0., 1., 1., 1., 1., 1.,
                        1., 1., 1., 0., 0., 1., 1., 1., 1., 1., 1., 1., 1.,
                        0., 0., 1., 1., 1., 0., 0., 1., 1., 1., 0., 0., 1.,
                        1., 1., 0., 0., 1., 1., 1., 0., 0., 1., 1., 1., 1.,
                        1., 1., 1., 1., 0., 0., 1., 1., 1., 1., 1., 1., 1.,
                        1., 0., 0., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0.,
                        0., 0., 0., 0., 0., 0., 0., 0., 0.]

        self.current_player = BLACK


    cpdef object copy(self):
        o = Othello()
        memcpy(o.board, self.board, 100)
        memcpy(o.empties, self.empties, 100)

        o.current_player = self.current_player

        return o

    cpdef char player(self):
        return self.current_player
    
    cpdef char opponent(self):
        return -1 * self.current_player

    cpdef char* get_board(self):
        return self.board

    cpdef bint has_bracket(self, char move):
        for i in range(8):
            if self.find_bracket(move, DIRECTIONS[i]) != -1:
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

    cpdef void flip(self, char move, char direction):
        cdef char bracket = self.find_bracket(move, direction)

        if bracket == -1:
            return

        cdef char square = move + direction
        while square != bracket:
            self.board[square] = self.current_player
            square += direction

    cpdef void play(self, char move):
        self.board[move] = self.current_player
        self.empties[move] = 0

        for i in range(8):
            self.flip(move, DIRECTIONS[i])

        self.current_player = self.opponent()

    cpdef char score(self):
        cdef char black_pieces = 0
        cdef char white_pieces = 0
        for i in range(100):
            if self.board[i] == BLACK:
                black_pieces += 1
            elif self.board[i] == WHITE:
                white_pieces += 1

        return black_pieces - white_pieces

    def get_board_2d(self):
        board_state = np.zeros((3,8,8))

        for valid_idx in range(64):
            array_index = VALID_IDXS[valid_idx]
            if self.board[array_index] == BLACK:
                i, j = (array_index // 10) - 1, (array_index % 10) - 1
                board_state[0, i, j] = 1
            elif self.board[array_index] == WHITE:
                i, j = (array_index // 10) - 1, (array_index % 10) - 1
                board_state[1, i, j] = 1

        if self.current_player == BLACK:
            board_state[2,:,:] = 1 

        return board_state

    def legal_moves(self):
        return [move for move in range(100) if self.empties[move] == 1 and self.has_bracket(move) ]

    def render(self):
        
        board = [OUTER] * 100
        for i in range(100):
            if self.board[i] == OUTER:
                board[i] = '?'
            elif self.board[i] == EMPTY:
                board[i] = '.'
            elif self.board[i] == BLACK:
                board[i] = 'o'
            else:
                board[i] = 'X'
        
        rep = ''
        rep += '  %s\n' % ' '.join(map(str, range(1, 9)))
        for row in range(1, 9):
            begin, end = 10*row + 1, 10*row + 9
            rep += '%d %s\n' % (row, ' '.join(board[begin:end]))
        print(rep)