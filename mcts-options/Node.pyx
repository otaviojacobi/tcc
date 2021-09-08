# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint16_t, int8_t
from libc.math cimport INFINITY

from random import choice, shuffle
from Edge import Edge
from copy import deepcopy


cdef class Node:
    cdef public object env
    cdef public object parent_node
    cdef public dict child_nodes

    cdef public bint is_leaf
    cdef public bint expanded
    cdef public uint16_t edge_count_sum
    cdef public double state_value

    cdef public set unexpanded_options
    cdef public list options

    cdef public double value   # V(s)
    cdef public double count   # N(s)


    def __init__(self, object env, list options):
        self.env = env
        self.parent_node = None
        self.is_leaf = env.is_leaf()
        self.child_nodes = {}
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])
        self.value = 0.0

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

        cdef object cur_node = self
        cdef object new_node
        cdef object new_edge
        cdef int8_t action

        cdef object option = choice(tuple(self.unexpanded_options))
        cdef object env_copy = self.env.copy()
        while True:
            action = option.get_action(env_copy)
            if action == -1 or env_copy.finished():
              break

            env_copy.step(action)
            if action not in cur_node.child_edges.keys():
              new_node = Node(env_copy, [])
              new_edge = Edge(1, cur_node, new_node)
              new_node.parent_edge = new_edge
              cur_node.child_edges[action] = new_edge
              cur_node.edge_count_sum += 1

              cur_node = new_node
            else:
              cur_node = cur_node.child_edges[action].get_child()

            env_copy = env_copy.copy()

        cur_node.set_options(self.options)
        
        self.unexpanded_options.remove(option)
        option.executed = False

        return cur_node


    cpdef double simulate(self):
        cdef simulationEnv = self.env.copy()

        cdef list moves = simulationEnv.legal_moves()
        cdef int8_t move

        cdef double total_return = 0
        while not simulationEnv.finished():
            move = choice(moves)
            _, r, _ = simulationEnv.step(move)
            total_return += r
            moves = simulationEnv.legal_moves()
        
        return total_return

    cpdef void backprop(self, double value):
        cdef object cur_edge = self.parent_edge

        while cur_edge != None:
            cur_edge.update(value)
            cur_edge = cur_edge.get_parent().parent_edge

    cpdef void info(self, double c):
        for action, edge in self.child_edges.items():
            print('Action: ', action)
            edge.info(c)

    cpdef void set_options(self, list options):
        self.options = deepcopy(options)
        self.unexpanded_options = set([opt for opt in options if opt.is_valid_option(self.env)])
