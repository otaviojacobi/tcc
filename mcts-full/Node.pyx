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

    cdef bint _is_leaf
    cdef public bint expanded

    cdef public uint16_t edge_count_sum

    cdef double _state_value

    def __init__(self, object board):
        self.board = board
        self._parent_edge = None
        self.expanded = False
        self._is_leaf = board.is_leaf()
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

        values = list(self.child_edges.values())
        shuffle(values)
        for edge in values:
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

    cpdef object get_higher_value_child(self):
        cdef double higher_count = -999999.0

        cdef double count
        cdef int8_t most_visited_move

        for action, edge in self.child_edges.items():
            #count = edge.cost + edge.get_action_value()
            count = edge.get_action_value()
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef double expand(self):

        if self._is_leaf:
            return 0

        cdef object board
        cdef object new_node
        cdef object new_edge
        cdef double cost

        for option in self.board.get_valid_options():

            board = self.board.copy()
            _, cost, _ = board.play(option)

            new_node = Node(board)
            new_edge = Edge(1, self, new_node, cost)
            new_node.set_parent_edge(new_edge)

            self.child_edges[option.opt_id] = new_edge

        self.edge_count_sum += 1
        self.expanded = True

        cdef double score = self.board.get_oracle_score()
        cdef double noisy_score = np.random.normal(score, 10)
        return min(score, noisy_score)
        #return score-1

        #return self.simulate()


    cpdef double simulate(self):
        cdef simulationboard = self.board.copy()

        cdef list moves = simulationboard.legal_moves()
        cdef int8_t move

        while not simulationboard.finished():
            move = choice(moves)
            simulationboard.step(move)
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
