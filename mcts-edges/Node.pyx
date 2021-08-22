# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint16_t, int8_t
from libc.math cimport INFINITY

from random import choice, shuffle
from Edge import Edge

import numpy as np

cdef class Node:
    cdef public object board
    cdef object _parent_edge
    cdef public dict child_edges

    cdef list _moves

    cdef bint _is_leaf
    cdef public bint expanded

    cdef public uint16_t edge_count_sum

    cdef double _state_value

    def __init__(self, object board):
        self.board = board
        self._parent_edge = None
        self.expanded = False
        self._moves = board.legal_moves()
        self._is_leaf = len(self._moves) == 0
        self.edge_count_sum = 0
        self.child_edges = {}

    cpdef uint16_t get_total_count(self):
        return self.edge_count_sum

    cpdef bint is_expanded(self):
        return self.expanded

    cpdef bint is_leaf(self):
        return self._is_leaf

    cpdef void set_parent_edge(self, object parent_edge):
        self._parent_edge = parent_edge

    cpdef object get_parent_edge(self):
        return self._parent_edge

    cpdef dict getchild_edges(self):
        return self.child_edges

    cpdef void increment_counter(self):
        self.edge_count_sum += 1

    # TODO: maybe we can avoid this loop by using a heap
    # Everytime we backprop in the tree each edge traversed updates its ucb value and updates the heap
    # So we always keep track of the maximum ucb in first position and this funcion goes from O(n) -> O(1)
    # HOWEVER, this is prob unecessary unless branching factor is really really high
    cpdef object get_highest_ucb_child(self, double c):
        cdef double highest = -INFINITY
        cdef double ucb = -INFINITY

        cdef object edge = None
        cdef object best_edge = None

        for edge in shuffle(self.child_edges.values()):
            ucb = edge.ucb(c)
            if ucb > highest:
                highest = ucb
                best_edge = edge

        return best_edge.get_child()

    cpdef object get_most_visisted_child(self):
        cdef uint16_t higher_count = 0

        cdef uint16_t count
        cdef int8_t most_visited_move

        for action, edge in self.child_edges.items():
            count = edge.get_count()
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef double expand(self):

        if self._is_leaf:
            return 0

        #cdef double score = self.simulate()

        cdef object node = self
        cdef object option = choice(node.board.get_valid_options())
        cdef int8_t option_action
        
        cdef object new_node
        cdef object new_edge

        while not option.finished and not node.is_leaf():
            option_action = option.get_action(node.board)

            if option_action == -1:
                break

            node.edge_count_sum += 1
            node.expanded = True

            for move in node.board.legal_moves():
                board = node.board.copy()
                board.play(move)

                new_node = Node(board)
                new_edge = Edge(1, node, new_node)

                new_node.set_parent_edge(new_edge)
                node.child_edges[move] = new_edge

            node = node.child_edges[option_action].get_child()

        cdef double score = np.random.normal(node.board.get_oracle_score(), 4)


        return score

    cpdef double simulate(self):
        cdef simulationboard = self.board.copy()

        cdef list moves = self._moves
        cdef int8_t move

        while not simulationboard.finished():
            move = choice(moves)
            simulationboard.play(move)
            moves = simulationboard.legal_moves()
        
        return simulationboard.get_score()

    cpdef void backprop(self, double value):
        cdef object cur_edge = self._parent_edge

        while cur_edge != None:
            cur_edge.update(value)
            cur_edge = cur_edge.get_parent().get_parent_edge()

    cpdef void info(self, double c):
        for action, edge in self.child_edges.items():
            print('Action: ', action)
            edge.info(c)