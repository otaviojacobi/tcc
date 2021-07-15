# distutils: language = c++
# cython: language_level=3
from othello_cython import Othello

from libc.math cimport sqrt, log
from libc.stdlib cimport rand

from cpython.ref cimport PyObject

cdef class Node:
    cdef object state
    cdef PyObject* parent
    cdef unsigned int won
    cdef unsigned int visits

    cdef dict children
    cdef set unexpanded

    def __init__(self, object board, object parent = None):
        self.state = board
        self.won = 0
        self.visits = 0

        self.parent = <PyObject*>parent

        self.unexpanded = set()
        self.children = dict()
        for move in board.legal_moves():
            self.children[move] = None
            self.unexpanded.add(move)

    cpdef bint is_fully_expanded(self):
        return len(self.unexpanded) == 0

    cpdef bint is_leaf(self):
        return len(self.children) == 0

    cpdef double ucb(self, unsigned int c = 2):
        parent = <object>self.parent
        return (self.won/self.visits) + c * sqrt(2 * log(parent.visits_count())/self.visits )

    cpdef object get_highest_ucb_child(self):
        cdef double hi = -100.0

        cdef double ucb
        cdef object best_child

        for child_node in self.children.values():
            ucb = child_node.ucb()
            if ucb > hi:
                hi = ucb
                best_child = child_node

        return best_child

    cpdef char get_random_unexplored_action(self):
        return next(iter(self.unexpanded))

    cpdef object get_state_copy(self):
        state = self.state
        return state.copy()

    cpdef void expand(self, char action, object new_child):
        self.unexpanded.remove(action)
        self.children[action] = new_child

    cpdef char get_player(self):
        state = <object>self.state
        return state.player()

    cpdef unsigned int visits_count(self):
        return self.visits

    cpdef unsigned int won_count(self):
        return self.won

    cpdef void increment_visits(self):
        self.visits += 1

    cpdef void increment_won(self):
        self.won += 1

    cpdef object get_parent(self):
        return <object>self.parent

    cpdef char get_best_action(self):
        cdef double prob_winning = -1
        cdef char max_action

        cdef char action
        cdef object node
        cdef double chance_of_winning

        for action in self.children.keys():
            node = self.children[action]
            chance_of_winning = node.won_count()/node.visits_count()
            if chance_of_winning > prob_winning:
                prob_winning = chance_of_winning
                max_action = action

        print(prob_winning)
        return max_action

cdef class MCTS:

    cdef object root

    def __init__(self, object board):
        self.root = Node(board.copy())

    cpdef char run(self, unsigned int simulations):
        cdef object node_to_expand
        cdef object new_expanded_node
        cdef bint current_player_won

        for _ in range(simulations):
            node_to_expand = self.search()
            new_expanded_node = self.expand(node_to_expand)
            current_player_won = self.simulate(new_expanded_node)
            self.backprop(new_expanded_node, current_player_won)

        return self.root.get_best_action()

    cpdef object search(self):
        cdef object cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf():
            cur_node = cur_node.get_highest_ucb_child()
        
        return cur_node

    cpdef object expand(self, object node):
        if node.is_leaf():
            return node

        cdef char action = node.get_random_unexplored_action()

        cdef object new_board = node.get_state_copy()
        new_board.play(action)

        cdef object new_node = Node(new_board, parent=node)
        node.expand(action, new_node)

        return new_node

    cpdef bint simulate(self, object node):
        cdef object board_copy = node.get_state_copy()

        cdef list legal_moves = board_copy.legal_moves()
        cdef int random_index
        cdef int len_legal_moves = len(legal_moves)

        while len_legal_moves != 0:
            random_index = int(rand() % len_legal_moves)
            a = legal_moves[random_index]
            board_copy.play(a)

            legal_moves = board_copy.legal_moves()
            len_legal_moves = len(legal_moves)

        score = board_copy.score()

        # black wins
        if score > 0.:
            if node.get_player() == -1:
                return 1
            else:
                return 0
        # white wins
        else:
            if node.get_player() == 1:
                return 1
            else:
                return 0

    cpdef void backprop(self, object node, bint won):
        while node is not None:
            node.increment_visits()

            if not won:
                node.increment_won()

            won = not won
            node = node.get_parent()



