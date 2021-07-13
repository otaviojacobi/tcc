import numpy as np

OUTER = -1
EMPTY = 0
BLACK = 1
WHITE = 2

UP, DOWN, LEFT, RIGHT = -10, 10, -1, 1
UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = -9, 11, 9, -11
DIRECTIONS = (UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT)

class Othello:
    def __init__(self):
        
        self.__squares = np.array([i for i in range(11, 89) if 1 <= (i % 10) <= 8])
        self.__board, self.__empties = self.__new_board()
        self.__current_player = BLACK
        
    def player(self):
        return self.__current_player
    
    def opponent(self):
        return BLACK if self.__current_player is WHITE else WHITE
    
    def legal_moves(self):
        return [move for move in self.__empties if self.__has_bracket(move)]

    def play(self, move):
        self.__board[move] = self.__current_player
        self.__empties.remove(move)
        
        
        for direction in DIRECTIONS:
            self.__flip(move, direction)
            
        self.__current_player = self.opponent()
        
    def score(self):
        black_pieces = np.count_nonzero(self.__board == BLACK)
        white_pieces = np.count_nonzero(self.__board == WHITE)
        
        return black_pieces - white_pieces
            
    def __flip(self, move, direction):
        bracket = self.__find_bracket(move, direction)
        if not bracket:
            return
        square = move + direction
        while square != bracket:
            self.__board[square] = self.__current_player
            square += direction
    
    
    def __find_bracket(self, square, direction):
        bracket = square + direction
        if self.__board[bracket] == self.__current_player:
            return None

        while self.__board[bracket] == self.opponent():
            bracket += direction

        return None if self.__board[bracket] in (OUTER, EMPTY) else bracket
    
    def __has_bracket(self, move):
            return any(map(lambda d: self.__find_bracket(move, d), DIRECTIONS))
    
    
    def __new_board(self):
        board = -1 * np.ones(100)
        board[self.__squares] = EMPTY
        
        empties = set()
        
        for val in self.__squares:
            empties.add(val)

        board[44], board[45] = WHITE, BLACK
        board[54], board[55] = BLACK, WHITE
        
        empties.discard(44)
        empties.discard(45)
        empties.discard(54)
        empties.discard(55)
        
        return board, empties
    
    def __str__(self):
        
        board = [OUTER] * 100
        for i in range(100):
            if self.__board[i] == OUTER:
                board[i] = '?'
            elif self.__board[i] == EMPTY:
                board[i] = '.'
            elif self.__board[i] == BLACK:
                board[i] = 'o'
            else:
                board[i] = 'X'
        
        rep = ''
        rep += '  %s\n' % ' '.join(map(str, range(1, 9)))
        for row in range(1, 9):
            begin, end = 10*row + 1, 10*row + 9
            rep += '%d %s\n' % (row, ' '.join(board[begin:end]))
        return rep
