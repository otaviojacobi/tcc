# distutils: language = c++
# cython: language_level=3
from othello_cython import Othello

from libc.math cimport sqrt, log
from libc.stdlib cimport rand

from random import choices

cdef class Edge:
    cdef double prior
    cdef int count
    cdef double action_value
    cdef double value_sum

    cdef object child_node
    cdef object parent_node

    def __init__(self, double prior, object child_node, object parent_node):
        self.prior = prior
        self.count = 0
        self.action_value = 0
        self.value_sum = 0

        self.child_node = child_node
        self.parent_node = parent_node

    cpdef object get_parent_node(self):
        return self.parent_node

    cpdef object get_child_node(self):
        return self.child_node

    cpdef void update_edge_value(self, double value):
        self.count += 1
        self.value_sum += value

        self.action_value = self.value_sum / self.count

    cpdef object get_count(self):
        return self.count

    cpdef double ucb(self, double c = 2):
        total_count = self.parent_node.get_total_count()
        return self.action_value + (c * self.prior * sqrt(total_count) / (1 + self.count))

cdef class Node:
    cdef object state
    cdef object parent_edge
    cdef dict edge
    
    cdef bint is_leaf
    cdef bint is_expanded

    def __init__(self, object board):
        self.state = board
        self.parent_edge = None

        self.edge = dict()

        self.is_expanded = False
        self.is_leaf = len(board.legal_moves()) == 0

    cpdef bint get_is_expanded(self):
        return self.is_expanded

    cpdef bint get_is_leaf(self):
        return self.is_leaf

    cpdef void set_parent_edge(self, object edge):
        self.parent_edge = edge

    cpdef object get_parent_edge(self):
        return self.parent_edge

    cpdef object get_highest_ucb_child(self):
        cdef double hi = -100.0

        cdef double ucb
        cdef object best_edge

        for edge in self.edge.values():
            ucb = edge.ucb()
            if ucb > hi:
                hi = ucb
                best_edge = edge

        return edge.get_child_node()

    #TODO: this can be optimizing by also adding total visits to the node 
    # so we don't have to loop for all the edges every time
    cpdef int get_total_count(self):
        cdef int total = 0
        for edge in self.edge.values():
            total += edge.get_count()
        return total

    cpdef char get_play_action(self, double T):
        cdef list legal_moves = self.state.legal_moves()
        cdef list move_prob = list()
        cdef double total_prob
        cdef double prob

        cdef double temperature = 1 / T

        for move in legal_moves:
            prob = self.edges[move].get_count() ** temperature
            total_prob += prob
            move_prob.append(prob)

        move_prob = [m/total_prob for m in move_prob] 

        return choices(legal_moves, move_prob)

    cpdef double expand(self):

        #p, v = nn(self.state.get_board_2d())
        p = [0.0] * 100.
        v = 1.2

        legal_moves = self.state.legal_moves()

        for move in legal_moves:
            new_state = self.state.copy()
            new_state.play(move)

            new_node = Node(new_state)

            # Next lines do two way binding between new_node <-> edge <-> child_node
            #TODO: p[moves] won't sum 1 bcs priors are distributed over non legal moves too...
            new_edge = Edge(p[move], 0, 0, new_node, self)
            new_node.set_parent_edge(new_edge)
            self.edge[move] = new_edge

        self.is_expanded = True

        return v

    cpdef void backprop(self, double value):
        cpdef object cur_edge = self.parent_edge
        while cur_edge is not None:
            cur_edge.update_edge_value(value)
            cur_edge = cur_edge.get_parent_node().get_parent_edge()

cdef class MCTS:

    cdef object root

    def __init__(self, object board):
        self.root = Node(board.copy())

    cpdef char run(self, unsigned int simulations):
        cdef object node
        cdef double value
        cdef bint current_player_won

        for _ in range(simulations):
            node = self.search()
            value = node.expand()
            node.backprop(value)

        return self.root.get_best_action()

    cpdef object search(self):
        cdef object cur_node = self.root

        while cur_node.get_is_expanded() and not cur_node.get_is_leaf():
            cur_node = cur_node.get_highest_ucb_child()
        
        return cur_node

