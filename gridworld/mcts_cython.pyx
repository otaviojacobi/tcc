from cpython.ref cimport PyObject

from libc.math cimport sqrt, log
from libc.stdlib cimport rand

cdef class Node:
    cdef object state
    cdef PyObject* parent
    cdef unsigned int visits
    cdef double value
    cdef double total

    cdef dict children
    cdef set unexpanded


    def __init__(self, object board, object parent = None):
        self.state = board
        self.total = 0.0
        self.value = 0.0
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

    ## TODO: change me for correct ucb with value sum
    cpdef double ucb(self, unsigned int c = 2):
        parent = <object>self.parent
        return self.value + c * sqrt(2 * log(parent.visits_count())/self.visits )

    cpdef object get_highest_ucb_child(self):
        cdef double hi = -99999.0

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

    cpdef unsigned int visits_count(self):
        return self.visits

    cpdef void increment_visits(self):
        self.visits += 1

    cpdef object get_parent(self):
        return <object>self.parent

    cpdef char get_best_action(self):
        cdef double most_visits = -9999
        cdef char max_action

        cdef char action
        cdef object node
        cdef double nr_visits

        for action in self.children.keys():
            node = self.children[action]
            nr_visits = node.visits_count()
            #print(action, nr_visits)
            if nr_visits > most_visits:
                most_visits = nr_visits
                max_action = action

        #print(prob_winning)
        return max_action

    cpdef void update(self, double value):
        self.visits += 1
        self.total += value
        self.value = self.total / self.visits

    cpdef object expand(self):
        if self.is_leaf():
            return self 

        cdef char action = self.get_random_unexplored_action()

        cdef object new_board = self.state.copy()
        new_board.step(action)

        cdef object new_node = Node(new_board, parent=self)
        self.unexpanded.remove(action)
        self.children[action] = new_node

        return new_node

    cpdef double simulate(self):
        cdef object board_copy = self.get_state_copy()

        cdef list legal_moves = board_copy.legal_moves()
        cdef int random_index
        cdef int len_legal_moves = len(legal_moves)

        cdef double score = 0

        while len_legal_moves != 0:
            random_index = int(rand() % len_legal_moves)
            a = legal_moves[random_index]
            _, r, _ = board_copy.step(a)

            score += r

            legal_moves = board_copy.legal_moves()
            len_legal_moves = len(legal_moves)

        return score


    cpdef void backprop(self, double value):

        cdef object node = self
        while node is not None:
            node.update(value)
            node = node.get_parent()


cdef class MCTS():
    cdef object root

    def __init__(self, object game):
        self.root = Node(game.copy())

    cpdef char run(self, unsigned int simulations):
        for _ in range(simulations):
            node_to_expand = self.search()
            new_node = node_to_expand.expand()
            score = new_node.simulate()
            new_node.backprop(score)
        
        return self.root.get_best_action()

    cpdef object search(self):
        cdef object cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf():
            cur_node = cur_node.get_highest_ucb_child()
        
        return cur_node