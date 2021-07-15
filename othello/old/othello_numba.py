from numba import int8
from numba.experimental import jitclass
import numpy as np

OUTER = int8(-500)
EMPTY = int8(0)
BLACK = int8(1)
WHITE = int8(-1)

UP, DOWN, LEFT, RIGHT = int8(-10), int8(10), int8(-1), int8(1)
UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = int8(-9), int8(11), int8(9), int8(-11)
DIRECTIONS = np.array([UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT], dtype=np.int8)

squares = np.array([i for i in range(11, 89) if 1 <= (i % 10) <= 8], dtype=np.int8)
values = np.array([i for i in range(11, 89) if 1 <= (i % 10) <= 8], dtype=np.int8)
values = values[np.where(values != 44)]
values = values[np.where(values != 45)]
values = values[np.where(values != 54)]
values = values[np.where(values != 55)]

default_empties = np.zeros(100, np.int8)

for value in values:
    default_empties[value] = int8(1)

initial_board = OUTER * np.ones(100, dtype=np.int8)
initial_board[squares] = EMPTY
initial_board[44] = WHITE
initial_board[45] = BLACK
initial_board[54] = BLACK
initial_board[55] = WHITE

spec = [
    ('player', int8),
    ('board', int8[:]),
    ('empties', int8[:])
]
@jitclass(spec)
class Othello(object):
    def __init__(self, board, player, empties):
        self.board = board
        self.player = player
        self.empties = empties

    @staticmethod
    def new():
        return Othello(initial_board.copy(), int8(BLACK), default_empties.copy())

    def copy(self):
        return Othello(self.board.copy(), self.player, self.empties.copy())

    def finished(self):
        return len(self.legal_moves()) == 0

    def reset(self):
        self.board = initial_board.copy()
        self.player = int8(BLACK)
        self.empties = default_empties.copy()

    def play(self, move):
        self.board[move] = self.player
        self.empties[move] = 0

        for direction in DIRECTIONS:
            self.__flip(move, direction)

        self.player = self.opponent()

    def score(self):
        return np.sum(self.board[squares])

    def legal_moves(self):
        return list(filter(self.__has_bracket, np.where(self.empties == 1)[0]))

    def opponent(self):
        return -1 * self.player

    def __find_bracket(self, square, direction):
        bracket = square + direction
        if self.board[bracket] == self.player:
            return -1

        op = self.opponent()
        while self.board[bracket] == op:
            bracket += direction

        if self.board[bracket] == OUTER or self.board[bracket] == EMPTY:
            return -1

        return bracket

    def __has_bracket(self, move):
        for direction in DIRECTIONS:
            if self.__find_bracket(move, direction) != -1:
                return True
        return False

    def __flip(self, move, direction):
        bracket = self.__find_bracket(move, direction)
        if bracket == -1:
            return
        square = move + direction
        while square != bracket:
            self.board[square] = self.player
            square += direction