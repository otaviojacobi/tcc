# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t

from Node import Node
from copy import deepcopy
import numpy as np

import time

cdef class MCTS:
    cdef public object root
    cdef public list options

    def __init__(self, object env, list options):
        self.root = Node(env.copy(), options)
        self.options = deepcopy(options)

    def run(self, uint16_t simulations, double c):
        cdef object node
        cdef double value
        cdef double score
        cdef double noisy_score
        cdef double total_time = 0
        cdef double prev = time.time() * 1000
        cdef double cur
        cdef int total_sims = 0
        #while total_time < simulations - 3:
        for sim in range(simulations):
            node = self.search(c)
            _, node, _, _ = node.expand()
            #if not node.is_leaf:
            #score = node.env.get_oracle_score()
            #print('predicted score', score)
            #noisy_score = np.random.normal(score, 2)
            #value =  min(score, noisy_score)
            #print('value', value)
            #print('cost', node.env.score)
            value = node.simulate()
            # else:
            #     value = 0
            node.backprop(value)

            cur = time.time() * 1000
            total_time = cur - prev

            total_sims += 1


        #TODO: use get_higher_value_child too
        cdef option_id = self.root.get_most_visisted_child()
        #print(option_id)
        for option in self.options:
            if option.opt_id == option_id:
                return option, total_sims

        #print('BOOM')
        return -1, -1


    cpdef object search(self, double c):
        cdef object cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf:
            cur_node = cur_node.get_highest_ucb_child(c)

        return cur_node