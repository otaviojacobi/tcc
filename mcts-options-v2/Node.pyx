# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint16_t, int8_t
from libc.math cimport INFINITY

from random import choice, shuffle
from Edge import Edge
from copy import deepcopy


cdef class Node:
    cdef public object env
    cdef public object parent_edge
    cdef public dict child_edges

    cdef public bint is_leaf
    cdef public bint expanded
    cdef public uint16_t edge_count_sum
    cdef public double state_value

    cdef public set unexpanded_options
    cdef public list options

    def __init__(self, object env, list options):
        self.env = env
        self.parent_edge = None
        self.is_leaf = env.is_leaf()
        self.edge_count_sum = 0
        self.child_edges = {}
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])


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
        cdef int8_t most_visited_move = -1

        for action, edge in self.child_edges.items():
            count = edge.get_count()
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef object get_higher_value_child(self):
        cdef double higher_count = -999999.0

        cdef double count
        cdef int8_t most_visited_move = -1

        for action, edge in self.child_edges.items():
            #count = edge.cost + edge.get_action_value()
            count = edge.get_action_value()
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef bint is_fully_expanded(self):
      return len(self.unexpanded_options) == 0

    cpdef object expand(self):

        if self.is_leaf:
            return self

        cdef int8_t action

        cdef object option = choice(tuple(self.unexpanded_options))
        cdef object env_copy = self.env.copy()
        while True:
            action = option.get_action(env_copy)
            if action == -1 or env_copy.finished():
              break

            env_copy.step(action)

        cdef object new_node = Node(env_copy, self.options)
        cdef object new_edge = Edge(1, self, new_node)
        new_node.parent_edge = new_edge
        self.child_edges[option.opt_id] = new_edge
        self.edge_count_sum += 1


        self.unexpanded_options.remove(option)
        option.executed = False

        return new_node


    cpdef double simulate(self):
        cdef simulationEnv = self.env.copy()

        cdef list moves = simulationEnv.legal_moves()
        cdef int8_t move

        while not simulationEnv.finished():
            move = choice(moves)
            simulationEnv.step(move)
            moves = simulationEnv.legal_moves()
        
        return simulationEnv.get_score()

    cpdef void backprop(self, double value):
        cdef object cur_edge = self.parent_edge

        while cur_edge != None:
            cur_edge.update(value)
            cur_edge = cur_edge.get_parent().parent_edge

    cpdef void info(self, double c):
        for action, edge in self.child_edges.items():
            print('Option ID: ', action)
            edge.info(c)

    cpdef void set_options(self, list options):
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])
