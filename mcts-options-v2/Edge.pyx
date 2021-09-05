# distutils: language = c++
# cython: language_level=3

from libc.stdint cimport uint32_t
from libc.math cimport sqrt, log

cdef class Edge:
    cdef double _prior          # P(s, a)
    cdef double _value_sum      # W(s, a)
    cdef uint32_t _count        # N(s, a)
    cdef double _action_value   # Q(s, a) = W(s, a) / N(s, a)

    cdef object _parent_node
    cdef object _child_node

    cdef public double cost


    def __init__(self, double prior, object parent_node, object child_node, double cost):
        self._prior = prior
        self._value_sum = 0.0
        self._action_value = 0.0
        self._count = 0

        self._parent_node = parent_node
        self._child_node = child_node

        self.cost = cost

    # TODO: DFS for freeing memory
    cpdef void clear(self):
        pass

    cpdef object get_parent(self):
        return self._parent_node

    cpdef object get_child(self):
        return self._child_node

    cpdef void update(self, double value):
        #self._action_value = (self._action_value * self._count + G) / (self._count + 1) 
        self._value_sum += value

        self._parent_node.edge_count_sum += 1
        #self._action_value = (self._count * self._action_value + value) / (self._count + 1)

        self._count += 1
        self._action_value = self._value_sum / (self._count + 1)

    cpdef uint32_t get_count(self):
        return self._count

    cpdef double get_action_value(self):
        return self._action_value

    cpdef double ucb(self, double c):
        cdef double total_count = self._parent_node.edge_count_sum
        cdef exploration_term = (self._prior * sqrt(log(total_count))) / (1 + self._count) # U(s, a)
        return self._action_value + c * exploration_term

    cpdef void info(self, double c):
        cdef double total_count = self._parent_node.edge_count_sum
        cdef exploration_term = c * (self._prior * sqrt(log(total_count))) / (1 + self._count) # U(s, a)


        print('P(s, a): ', self._prior)
        print('N(s, a): ', self._count)
        print('W(s, a): ', self._value_sum)
        print('Q(s, a): ', self._action_value)
        print('C(s, a): ', self.cost)

        print('U(s, a): ', exploration_term)
        print('UCB: ', self.ucb(c))
