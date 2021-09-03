# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t

from Node import Node

import numpy as np

cdef class MCTS:
    cdef public object root

    def __init__(self, object env, list options):
        self.root = Node(env.copy(), options)

    cpdef object run(self, uint16_t simulations, double c):
        cdef object node
        cdef double value
        cdef double score
        cdef double noisy_score

        for sim in range(simulations):
            node = self.search(c)
            node = node.expand()
            #value = node.simulate()
            score = node.env.get_oracle_score()
            noisy_score = np.random.normal(score, 4)
            value =  min(score, noisy_score)
            node.backprop(value)

        #TODO: use get_higher_value_child too
        return self.root.get_most_visisted_child()

    cpdef object search(self, double c):
        cdef object cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf:
            cur_node = cur_node.get_highest_ucb_child(c)

        return cur_node