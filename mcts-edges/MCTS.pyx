# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t

from Node import Node

cdef class MCTS:
    cdef public object root

    def __init__(self, object board):
        self.root = Node(board.copy())

    cpdef int8_t run(self, uint16_t simulations, double c):
        cdef object node
        cdef double value
        for _ in range(simulations):
            node = self.search(c)
            value = node.expand()
            node.backprop(value)

        return self.root.get_most_visisted_child()

    cpdef object search(self, double c):
        cdef object cur_node = self.root

        while cur_node.is_expanded() and not cur_node.is_leaf():
            cur_node = cur_node.get_highest_ucb_child(c)

        return cur_node