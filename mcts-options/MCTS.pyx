# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t

from NodeValue import Node

import numpy as np
from collections import defaultdict
import pickle

cdef class MCTS:
    cdef public object root
    cdef public double mini_q
    cdef public double maxi_q

    cdef public list options

    cdef public dict stats
    cdef public object f


    def __init__(self, object env, list options):
        #self.root = Node(env.copy(), options)
        self.root = Node(env.copy(), options, None)
        self.options = options
        self.stats = {}
        self.f = defaultdict(float)
        self.mini_q = 9999999
        self.maxi_q = -9999999

    def reset(self, object env):
        self.root = Node(env.copy(), self.options, None)
        self.mini_q = 999999
        self.maxi_q = -999999

    cpdef object run(self, uint16_t simulations, double c):
        cdef object node
        cdef double value
        cdef double score
        cdef double noisy_score
        cdef mini_q
        cdef maxi_q
        for sim in range(simulations):
            node = self.search(c)
            prev_node, node, opt_id, r = node.expand()
            value = node.simulate()
            #score = node.env.get_oracle_score()
            #noisy_score = np.random.normal(score, 5)
            #value =  min(score, noisy_score)

            if node.env not in self.stats.keys():
                self.stats[node.env] = [value, 1]
            else:
                self.stats[node.env] = [self.stats[node.env][0] + value, self.stats[node.env][1] + 1]

            self.f[node.env] = self.f[node.env] + 0.1 * (value - self.f[node.env])
            self.f[node.env] = self.stats[node.env][0] / float(self.stats[node.env][1])

            mini_q, maxi_q = node.backprop(self.f[node.env])

            self.mini_q = mini_q if mini_q < self.mini_q else self.mini_q
            self.maxi_q = maxi_q if maxi_q > self.maxi_q else self.maxi_q

        #TODO: use get_higher_value_child too
        return self.root.get_most_visisted_child()

    cpdef object search(self, double c):
        cdef object cur_node = self.root

        while cur_node.is_fully_expanded() and not cur_node.is_leaf:
            cur_node = cur_node.get_highest_ucb_child(c, self.mini_q, self.maxi_q)

        return cur_node

    cpdef void set_new_head(self, int action_id):
        self.root = self.root.child_nodes[action_id]

    cpdef void info(self, double c):
        self.root.info(c, self.mini_q, self.maxi_q)

    cpdef void save(self, str path):
        cpdef dict model = {'f': self.f, 'stats': self.stats, 'mini_q': self.mini_q, 'maxi_q': self.maxi_q}
        with open(path, 'wb') as f:
            pickle.dump(model, f)

    cpdef void load(self, str path):
        cpdef dict model
        with open(path, 'rb') as f:
            model = pickle.load(f)

        self.f, self.stats, self.mini_q, self.maxi_q = model['f'], model['stats'], model['mini_q'], model['maxi_q']