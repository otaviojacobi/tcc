# distutils: language = c++
# cython: language_level=3
from libc.stdint cimport int8_t, uint16_t

from Node import Node
from copy import deepcopy
import numpy as np
from collections import defaultdict

import pickle
import time

cdef class MCTS:
    cdef public object root
    cdef public list options

    cdef public dict g
    cdef public object f
    cdef public dict stats

    cdef public double maxi
    cdef public double mini

    def __init__(self, object env, list options):
        self.root = Node(env.copy(), options)
        self.options = deepcopy(options)
        self.g = {}
        self.f = defaultdict(float)
        self.stats = {}

        self.maxi = 0
        self.mini = 1

    def reset(self, object env):
        self.root = Node(env.copy(), self.options)

    def normalize(self, double value):
        if value < self.mini:
            self.mini = value

        return (value - self.mini) / (self.maxi - self.mini)

    def learn(self, uint16_t simulations, double c):
        cdef object node
        cdef tuple state_option
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
            prev_node, node, opt_id, r = node.expand()
            #if not node.is_leaf:
            #score = node.env.get_oracle_score()
            #print('predicted score', score)
            #noisy_score = np.random.normal(score, 0)
            #value =  min(score, noisy_score)
            #print('value', value)
            #print('cost', node.env.score)

            self.g[(prev_node.env.copy(), opt_id)] = (node.env.copy(), r)
            value = node.simulate()
            if node.env not in self.stats.keys():
                self.stats[node.env] = [value, 1]
            else:
                self.stats[node.env] = [self.stats[node.env][0] + value, self.stats[node.env][1] + 1]

            #self.f[node.env] = self.f[node.env] + 0.1 * (value - self.f[node.env])
            self.f[node.env] = self.stats[node.env][0] / float(self.stats[node.env][1])
            node.backprop(self.f[node.env])

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

    def run(self, uint16_t simulations, double c):
        cdef object node
        cdef tuple state_option
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
            prev_node, node, option = node.expand_with_model(self.g)
            #if not node.is_leaf:
            #score = node.env.get_oracle_score()
            #print('predicted score', score)
            #noisy_score = np.random.normal(score, 0)
            #value =  min(score, noisy_score)
            #print('value', value)
            #print('cost', node.env.score)

            #value = node.simulate()
            # else:
            #     value = 0
            node.backprop(self.f[node])

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

    cpdef void save(self, str path):
        cpdef dict model = {'f': self.f, 'g': self.g, 'stats': self.stats}
        with open(path, 'wb') as f:
            pickle.dump(model, f)

    cpdef void load(self, str path):
        cpdef dict model
        with open(path, 'rb') as f:
            model = pickle.load(f)

        self.f, self.g, self.stats = model['f'], model['g'], model['stats']