# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint16_t, int8_t
from libc.math cimport INFINITY
from libc.math cimport sqrt, log

from random import choice, shuffle
from Edge import Edge
from copy import deepcopy


cdef class Node:
    cdef public object env
    cdef public object parent_node
    cdef public dict child_nodes

    cdef public bint is_leaf
    cdef public bint expanded
    cdef public double state_value

    cdef public set unexpanded_options
    cdef public list options

    cdef public double value   # V(s)
    cdef public double count   # N(s)


    def __init__(self, object env, list options, object parent_node):
        self.env = env
        self.parent_node = parent_node
        self.is_leaf = env.is_leaf()
        self.child_nodes = {}
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])
        self.value = 0.0
        self.count = 1.0

    # TODO: maybe we can avoid this loop by using a heap
    # Everytime we backprop in the tree each edge traversed updates its ucb value and updates the heap
    # So we always keep track of the maximum ucb in first position and this funcion goes from O(n) -> O(1)
    # HOWEVER, this is prob unecessary unless branching factor is really really high
    cpdef object get_highest_ucb_child(self, double c):
        cdef double highest = -INFINITY
        cdef double ucb = -INFINITY

        cdef object edge = None
        cdef object best_edge = None

        values = list(self.child_nodes.values())
        shuffle(values)
        for node in values:
            ucb = node.ucb(c)
            if ucb > highest:
                highest = ucb
                best_node = node

        return best_node

    cpdef double ucb(self, double c):
        return self.value + c * sqrt(log(self.parent_node.count)/self.count)

    cpdef object get_most_visisted_child(self):
        cdef uint16_t higher_count = 0

        cdef uint16_t count
        cdef int8_t most_visited_move = -1

        for action, node in self.child_nodes.items():
            count = node.count
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef object get_higher_value_child(self):
        cdef double higher_count = -999999.0

        cdef double count
        cdef int8_t most_visited_move = -1

        for action, node in self.child_nodes.items():
            #count = edge.cost + edge.get_action_value()
            count = node.value
            if count > higher_count:
                most_visited_move = action
                higher_count = count

        return most_visited_move

    cpdef bint is_fully_expanded(self):
      return len(self.unexpanded_options) == 0

    cpdef object expand(self):

        if self.is_leaf:
            return self

        cdef object cur_node = self
        cdef object new_node
        cdef int8_t action

        cdef object option = choice(tuple(self.unexpanded_options))
        cdef object env_copy = self.env.copy()
        while True:
            action = option.get_action(env_copy)
            if action == -1 or env_copy.finished():
              break

            env_copy.step(action)
            if action not in cur_node.child_nodes.keys():
              new_node = Node(env_copy, [], cur_node)
              cur_node.child_nodes[action] = new_node
              cur_node = new_node
            else:
              cur_node = cur_node.child_nodes[action]

            env_copy = env_copy.copy()

        cur_node.set_options(self.options)
        
        self.unexpanded_options.remove(option)
        option.executed = False

        return cur_node

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
        cdef object cur_node = self
        cpdef double cur_depth = 0
        while cur_node != None:
            cur_depth += 1
            cur_node.update(value, cur_depth)
            cur_node = cur_node.parent_node

    cpdef void update(self, double value, double depth_dif):
        self.value = self.value + value * (0.99 ** depth_dif)
        self.count = self.count + 1


    cpdef void info(self, double c):
        self.basic_info(c)
        for action, node in self.child_nodes.items():
            print('Action: ', action)
            node.basic_info(c)

    cpdef void basic_info(self, double c):
        print('N(s): ', self.count)
        print('V(s): ', self.value)
        if self.parent_node != None:
            print('UCB: ', self.ucb(c))
        else:
            print('First node has no UCB')


    cpdef void set_options(self, list options):
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])
