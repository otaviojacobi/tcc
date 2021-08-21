# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint16_t, int8_t
from libc.math cimport INFINITY

from random import choice
from Edge import Edge

import numpy as np

cdef class Node:
    cdef object _board
    cdef object _parent_edge
    cdef dict _child_edges

    cdef list _moves

    cdef bint _is_leaf
    cdef bint _is_expanded

    cdef uint16_t _edge_count_sum

    cdef double _state_value

    def __init__(self, object board):
        self._board = board
        self._parent_edge = None
        self._is_expanded = False
        self._moves = board.legal_moves()
        self._is_leaf = len(self._moves) == 0
        self._edge_count_sum = 0
        self._child_edges = {}

    cpdef uint16_t get_total_count(self):
        return self._edge_count_sum

    cpdef bint is_expanded(self):
        return self._is_expanded

    cpdef bint is_leaf(self):
        return self._is_leaf

    cpdef void set_parent_edge(self, object parent_edge):
        self._parent_edge = parent_edge

    cpdef object get_parent_edge(self):
        return self._parent_edge

    cpdef dict get_child_edges(self):
        return self._child_edges

    cpdef void increment_counter(self):
        self._edge_count_sum += 1

    # TODO: maybe we can avoid this loop by using a heap
    # Everytime we backprop in the tree each edge traversed updates its ucb value and updates the heap
    # So we always keep track of the maximum ucb in first position and this funcion goes from O(n) -> O(1)
    # HOWEVER, this is prob unecessary unless branching factor is really really high
    cpdef object get_highest_ucb_child(self, double c):
        cdef double highest = -INFINITY
        cdef double ucb = -INFINITY

        cdef object edge = None
        cdef object best_edge = None

        for edge in self._child_edges.values():
            ucb = edge.ucb(c)
            if ucb > highest:
                highest = ucb
                best_edge = edge

        return best_edge.get_child()

    cpdef object get_most_visisted_child(self):
        cdef uint16_t higher_count = 0

        cdef uint16_t count
        cdef int8_t most_visited_move

        for action, edge in self._child_edges.items():
            count = edge.get_count()
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef double expand(self):

        #cdef double score = self.simulate()
        cdef double score = np.random.normal(self._board.get_oracle_score(), 5)

        cdef object board
        cdef object new_node
        cdef object new_edge

        for move in self._moves:
            board = self._board.copy()
            board.play(move)

            new_node = Node(board)
            new_edge = Edge(1, self, new_node)

            new_node.set_parent_edge(new_edge)
            self._child_edges[move] = new_edge


        self._edge_count_sum += 1
        self._is_expanded = True

        return score

    cpdef double simulate(self):
        cdef simulation_board = self._board.copy()

        cdef list moves = self._moves
        cdef int8_t move

        while not simulation_board.finished():
            move = choice(moves)
            simulation_board.play(move)
            moves = simulation_board.legal_moves()
        
        return simulation_board.get_score()

    cpdef void backprop(self, double value):
        cdef object cur_edge = self._parent_edge

        while cur_edge != None:
            cur_edge.update(value)
            cur_edge = cur_edge.get_parent().get_parent_edge()

    cpdef void info(self, double c):
        for action, edge in self._child_edges.items():
            print('Action: ', action)
            edge.info(c)